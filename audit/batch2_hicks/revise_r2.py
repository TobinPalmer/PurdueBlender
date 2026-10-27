import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path.cwd()
ASSET=bpy.data.collections['Asset_hicks_library']
SCENE=bpy.context.scene
AUDIT=ROOT/'audit'/'batch2_hicks'
ORIGIN=(88.25,-317.24000549316406)
GIS=json.loads((ROOT/'audit'/'official_building_references.json').read_text(encoding='utf-8'))
GIS_REC=next(x for x in GIS['buildings'] if x.get('fid')==197)
RING=[(x-ORIGIN[0],y-ORIGIN[1]) for x,y in GIS_REC['rings_xy_m'][0][:-1]]

# Rebuild only this R2 additions collection if the script is rerun.
for name in ['HIKS_R2_Sloped_Masonry_Envelope','HIKS_R2_2013_Furnishing_Details','HIKS_R2_Review']:
 col=bpy.data.collections.get(name)
 if col:
  for obj in list(col.objects): bpy.data.objects.remove(obj,do_unlink=True)
  for child in list(col.children): bpy.data.collections.remove(child,do_unlink=True)
  bpy.data.collections.remove(col)

def new_col(name,parent):
 c=bpy.data.collections.new(name); parent.children.link(c); return c
shell_col=new_col('HIKS_R2_Sloped_Masonry_Envelope',ASSET)
furn_col=new_col('HIKS_R2_2013_Furnishing_Details',ASSET)
review_col=new_col('HIKS_R2_Review',SCENE.collection)

brick=bpy.data.materials['Mat_HIKS_Purdue_Red_Brick']
wood=bpy.data.materials.get('HIKS_Study_Light_Maple')
white=bpy.data.materials.get('HIKS_Study_OffWhite')
green=bpy.data.materials.get('HIKS_Study_Green_Upholstery')
rust=bpy.data.materials.get('HIKS_Study_Rust_Upholstery')
steel=bpy.data.materials.get('HIKS_Study_Satin_Metal')
black=bpy.data.materials.get('HIKS_Study_Dark_Equipment')
if not all([wood,white,green,rust,steel,black]): raise RuntimeError('Expected previously built Hicks material set not found')

# The Purdue 2023 exterior photograph and 2026 masonry-renovation scope document
# four sloping masonry faces. The GIS perimeter fixes plan shape; only slope
# rise/run are estimated. Lower ring fits inside the existing plaza paving bounds.
center=((min(x for x,y in RING)+max(x for x,y in RING))/2,
        (min(y for x,y in RING)+max(y for x,y in RING))/2)
scale_x=1.29
scale_y=1.415
upper_z=2.438 # official Purdue GIS FID 197 roof extrusion/elevation attribute
lower_z=0.0   # campus model exterior grade datum; documented source, not survey elevation
n=len(RING)
verts=[(x,y,upper_z) for x,y in RING]
verts += [(center[0]+(x-center[0])*scale_x,
           center[1]+(y-center[1])*scale_y,lower_z) for x,y in RING]
faces=[]
for i in range(n):
 j=(i+1)%n
 faces.append((i,j,n+j,n+i))
mesh=bpy.data.meshes.new('HIKS_R2_GIS_Following_Sloped_Wall_Mesh')
mesh.from_pydata(verts,[],faces); mesh.materials.append(brick); mesh.update()
uv=mesh.uv_layers.new(name='Brick_Courses_Metric')
perimeter=0.0
edge_lengths=[]
for i in range(n):
 a=Vector(RING[i]); b=Vector(RING[(i+1)%n]); edge_lengths.append((b-a).length)
for poly in mesh.polygons:
 i=poly.index; j=(i+1)%n
 top_a=Vector(RING[i]); top_b=Vector(RING[j])
 bot_a=Vector((verts[n+i][0],verts[n+i][1])); bot_b=Vector((verts[n+j][0],verts[n+j][1]))
 slope_i=math.sqrt((top_a.x-bot_a.x)**2+(top_a.y-bot_a.y)**2+(upper_z-lower_z)**2)
 slope_j=math.sqrt((top_b.x-bot_b.x)**2+(top_b.y-bot_b.y)**2+(upper_z-lower_z)**2)
 u0=perimeter; u1=perimeter+edge_lengths[i]
 # Polygon loops follow the face vertex order: top_i, top_j, bottom_j, bottom_i.
 coords=[(u0,0.0),(u1,0.0),(u1,slope_j),(u0,slope_i)]
 for li,coord in zip(poly.loop_indices,coords): uv.data[li].uv=coord
 perimeter+=edge_lengths[i]
# Consistent normals on the closed outer frustum.
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free(); mesh.update()
obj=bpy.data.objects.new('HIKS_R2_Four_Sloped_GIS_Masonry_Walls',mesh); shell_col.objects.link(obj)
obj['source']='Purdue Physics 2023 Hicks exterior photograph; Indiana Commission September 2025 Hicks masonry renovation project description'
obj['feature_id']=197
obj['measurement']='Plan follows official Purdue GIS BuildingShapesZip4 FID 197; roof-level top elevation 2.438 m follows the GIS building attribute; lower grade ring anisotropic scale 1.29 x / 1.415 y and surface rise/run are interpretive estimates constrained to existing plaza bounds.'
obj['uncertainty']='The source confirms four sloped masonry walls but publishes no dimensions or section; wall inclination, lower apron offset, and exact contact elevation are estimated.'# Warm red-brown ramp matches the inherited material swatch; the prior grey ramp
# made the newly added masonry shell look white.
brick_bs=next(x for x in brick.node_tree.nodes if x.type=='BSDF_PRINCIPLED')
base_link=next((l for l in brick.node_tree.links if l.to_node==brick_bs and l.to_socket.name=='Base Color'),None)
if base_link and base_link.from_node.type=='VALTORGB':
 ramp=base_link.from_node.color_ramp
 ramp.elements[0].color=(.19,.035,.015,1)
 ramp.elements[1].color=(.42,.095,.038,1)
brick.diffuse_color=(.3075,.0915,.0435,1)
sol=obj.modifiers.new('Masonry wall backing','SOLIDIFY'); sol.thickness=0.16; sol.offset=-0.5
bev=obj.modifiers.new('Soft masonry arris','BEVEL'); bev.width=0.025; bev.segments=2

# Improve the carpet color response using the documented 2013 photo: warm brown
# carpet with fine rust/charcoal flecks, rather than a flat salmon tone.
carpet=bpy.data.materials.get('HIKS_Study_Terracotta_Carpet')
if carpet and carpet.use_nodes:
 nodes=carpet.node_tree.nodes; links=carpet.node_tree.links
 bs=next((x for x in nodes if x.type=='BSDF_PRINCIPLED'),None)
 if bs:
  tex=next((x for x in nodes if x.type=='TEX_NOISE'),None)
  if tex is None:
   tex=nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=105; tex.inputs['Detail'].default_value=2.0
   tc=nodes.new('ShaderNodeTexCoord'); links.new(tc.outputs['Object'],tex.inputs['Vector'])
  ramp=nodes.new('ShaderNodeValToRGB'); ramp.name='HIKS_R2_2013_Carpet_Fleck_Range'
  ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(.095,.063,.043,1)
  ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(.31,.205,.132,1)
  links.new(tex.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
  bump=next((x for x in nodes if x.type=='BUMP'),None)
  if bump: bump.inputs['Distance'].default_value=.0018; bump.inputs['Strength'].default_value=.15
  carpet.diffuse_color=(.24,.15,.09,1)

# Furniture pieces are interpreted from the official 2013 renovation photograph
# and Purdue Libraries description. Positions/sizes are explicitly approximate.
def move_into(o,collection):
 for col in list(o.users_collection): col.objects.unlink(o)
 collection.objects.link(o)
 return o

def box(name,loc,dims,mat,bevel=.035,rotation=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object; o.name='HIKS_R2_'+name; o.dimensions=dims
 o.rotation_euler[2]=rotation
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 move_into(o,furn_col); o.data.materials.append(mat)
 o['source']='Purdue 2013 Hicks renovation photograph / Purdue 2013 renovation announcement; approximate dimensions and placement'
 if bevel:
  mod=o.modifiers.new('Rounded upholstered/wood edges','BEVEL'); mod.width=bevel; mod.segments=3
  mod.profile=.5
 return o

def cylinder(name,loc,radius,depth,mat,vertices=32,bevel=.015):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
 o=bpy.context.object; o.name='HIKS_R2_'+name; move_into(o,furn_col); o.data.materials.append(mat)
 o['source']='Purdue 2013 renovation photograph; approximate furniture detail'
 if bevel:
  mod=o.modifiers.new('Soft furniture edge','BEVEL'); mod.width=bevel; mod.segments=2
 return o

def rod_between(name,a,b,radius,mat,vertices=12):
 a=Vector(a); b=Vector(b); delta=b-a
 o=cylinder(name,(a+b)/2,radius,delta.length,mat,vertices,0)
 o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
 return o

def round_table(cx,cy,diameter=1.0,height=.72):
 z=-5.304
 cylinder('Bistro_Table_Top',(cx,cy,z+height),diameter/2,.055,white,48,.025)
 cylinder('Bistro_Table_Pedestal',(cx,cy,z+height/2),.055,height-.055,steel,20,.015)
 for angle in (0,2*math.pi/3,4*math.pi/3):
  r=.38
  end=(cx+r*math.cos(angle),cy+r*math.sin(angle),z+.035)
  start=(cx+.035*math.cos(angle),cy+.035*math.sin(angle),z+height*.52)
  rod_between('Bistro_Table_Tripod_Foot',start,end,.025,steel)

def booth(cx,cy,length=3.6,angle=0):
 # Low fixed banquette with dark leather seat and rust-patterned back, matching the 2013 photo.
 z=-5.304; ca=math.cos(angle); sa=math.sin(angle)
 def point(dx,dy,dz): return (cx+dx*ca-dy*sa,cy+dx*sa+dy*ca,z+dz)
 box('Booth_Base',point(0,0,.22),(length,.72,.44),steel,.06,angle)
 box('Booth_Seat_Cushion',point(0,-.02,.49),(length-.06,.68,.16),black,.07,angle)
 box('Booth_Back_Outer',point(0,.29,.91),(length,.14,.82),rust,.065,angle)
 # Separate cushions, visible seams and small upholstery piping details.
 count=max(3,round(length/.72))
 for k in range(count):
  dx=(k-(count-1)/2)*(length/count)
  box('Booth_Back_Cushion',point(dx,.20,.91),(length/count-.035,.045,.70),rust,.055,angle)
  box('Booth_Seat_Pad',point(dx,-.045,.585),(length/count-.035,.61,.07),black,.045,angle)
 box('Booth_End_Arm',point(-length/2+.07,-.01,.75),(.14,.72,.60),rust,.06,angle)
 box('Booth_End_Arm',point(length/2-.07,-.01,.75),(.14,.72,.60),rust,.06,angle)

# Two low lounge/booth islands and circular tables; keep the main interior/atrium
# and existing evidence-backed study furniture clear.
booth(-9.3,-6.4,3.4,0)
booth(8.9,-6.4,3.8,0)
round_table(-9.3,-5.1,1.0)
round_table(8.9,-5.1,1.0)
# Source-supported informal group tables and movable chairs. Their positions are schematic.
round_table(-2.0,-6.7,1.1)
round_table(2.2,-6.7,1.1)
round_table(-2.0,2.7,.9)
round_table(2.2,2.7,.9)

# Privacy screens on desk/workstation backs, a featured element in the renovation photo.
for idx,x in enumerate([-5.7,-2.3,1.1,4.5]):
 y=1.3
 box('Acoustic_Privacy_Screen',(x,y,-4.18),(2.55,.075,.82),steel,.025)
 # Contrasting inset face and shallow bevel convey a fabric-wrapped acoustic panel.
 box('Acoustic_Privacy_Screen_Inset',(x,y-.045,-4.18),(2.42,.012,.70),white,.02)
 for dx in [-1.05,1.05]:
  rod_between('Splayed_Screen_Support',(x+dx,y,-4.55),(x+dx*1.16,y,-4.99),.028,wood)
# Narrow raised touch-down/computer counters, shown in the official renovation description.
for x in [-10.7,-6.7,6.7,10.7]:
 box('Quick_Access_StandUp_Counter',(x,5.0,-4.17),(1.45,.54,.07),wood,.025)
 box('Quick_Access_Monitor',(x,5.16,-3.88),(.48,.055,.31),black,.025)
 box('Quick_Access_Counter_Post',(x,5.0,-4.72),(.09,.12,1.0),steel,.015)
# iDesk/service point: a compact, distinctive front desk supported by the 2013 source.
box('iDesk_Service_Base',(0.0,5.5,-4.82),(2.1,.82,.94),wood,.055)
box('iDesk_Counter',(0.0,5.43,-4.29),(2.3,.9,.10),white,.035)
box('iDesk_Front_Panel',(0.0,5.08,-4.78),(1.8,.035,.58),rust,.02)
box('iDesk_Monitor',(0.0,5.72,-4.03),(.52,.07,.36),black,.025)

# R2 review cameras/lights live outside the exported building collection.
for o in list(review_col.objects): bpy.data.objects.remove(o,do_unlink=True)
def track(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
# Hide inherited evidence lights to avoid double illumination; no asset geometry is hidden.
for o in SCENE.objects:
 if o.type=='LIGHT': o.hide_render=True
world=bpy.data.worlds.new('HIKS_R2_Review_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.55,.66,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
SCENE.world=world
sun_data=bpy.data.lights.new('HIKS_R2_Sun','SUN'); sun_data.energy=2.2; sun_data.angle=math.radians(9)
sun=bpy.data.objects.new('HIKS_R2_Sun',sun_data); review_col.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-34),math.radians(-33))
for loc,energy,size in [((18,-25,22),1400,15),((-20,-12,12),750,12)]:
 ld=bpy.data.lights.new('HIKS_R2_Area','AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
 lo=bpy.data.objects.new('HIKS_R2_Area',ld); review_col.objects.link(lo); lo.location=loc; track(lo,(0,0,1))# Dedicated soft sources for a readable basement/interior evidence view.
for loc,energy,size in [((-4,-3,-1.25),650,10),((6,3,-1.1),520,9),((0,8,-1.35),400,8)]:
 ld=bpy.data.lights.new('HIKS_R2_Interior_Area','AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
 lo=bpy.data.objects.new('HIKS_R2_Interior_Area',ld); review_col.objects.link(lo); lo.location=loc; track(lo,(0,0,-5.1))
cam_data=bpy.data.cameras.new('HIKS_R2_Exterior_Review'); cam=bpy.data.objects.new('HIKS_R2_Exterior_Review',cam_data); review_col.objects.link(cam)
cam.location=(34,-33,10); track(cam,(0,0,1.4)); cam_data.lens=45; SCENE.camera=cam
SCENE.render.engine='CYCLES'; SCENE.cycles.samples=32
SCENE.render.resolution_x=1200; SCENE.render.resolution_y=800; SCENE.render.resolution_percentage=100
SCENE.render.image_settings.file_format='PNG'
SCENE.render.filepath=str(AUDIT/'r2_exterior_sloped_walls.png')
# Save the revised source before rendering.
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.render.render(write_still=True)
# Interior view; keep the same asset materials and R2 furniture.
cam.location=(-14,-10,-2.25); track(cam,(2,0,-4.25)); cam_data.lens=34
SCENE.render.resolution_x=1200; SCENE.render.resolution_y=800
SCENE.view_settings.exposure=0.0
SCENE.render.filepath=str(AUDIT/'r2_interior_2013_booths.png')
bpy.ops.render.render(write_still=True)
# Write scoped R2 evidence including applied build parameters and source-linked uncertainty.
asset_hash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
evidence={
 'asset':'modular/buildings/hicks_library.blend','asset_sha256':asset_hash,
 'building_id':'hicks_library','collection':'Asset_hicks_library','scene':SCENE.name,
 'source_feature_id':197,'gis_provider':'Purdue University Campus GIS BuildingShapesZip4, FID 197',
 'r2_geometry':{'sloped_wall_top_m':upper_z,'sloped_wall_bottom_m':lower_z,'base_scale_xy':[scale_x,scale_y], 'sloped_wall_segment_count':n,'mesh':'GIS perimeter lofted to lower outer ring'},
 'source_urls':[
  'https://www.physics.purdue.edu/interactions/images/2023/Hicks-Undergraduate-Library-616x409.jpg',
  'https://www.physics.purdue.edu/interactions/2023/research/research-publications.php',
  'https://www.purdue.edu/newsroom/archive/releases/2013/Q3/purdue-libraries-celebrates-hicks-undergraduate-library-renovation-with-sept.-13-event.html',
  'https://www.purdue.edu/uns/images/2013/walker-hicks.jpg',
  'https://secure.in.gov/che/files/September-25-Commission-Meeting.pdf',
  'https://lib.purdue.edu/wp-content/uploads/2024/03/Purdue_Libraries_Master_Plan_Vol2_Full_Doc_2023.09.29_Redacted_sm.pdf'
 ],
 'visuals':['audit/batch2_hicks/r2_exterior_sloped_walls.png','audit/batch2_hicks/r2_interior_2013_booths.png'],
 'uncertainties':['The source confirms four sloped masonry walls but no measured section; the 2.438 m top elevation follows the Purdue GIS roof extrusion attribute, while the footprint-relative lower apron scale is estimated from the photo and existing plaza extent.','The Purdue 2013 interior photo supports booth/lounge seating, circular bistro tables, acoustic privacy screens, quick-access computer counters, and an iDesk. These furnish positions and sizes are interpreted; the photo does not establish current as-built layout.','The Purdue Libraries 2023 master plan includes proposed Hicks ground-floor study partitions and basement seat additions; those are recommendations, not proof of completed construction, and were not represented as current as-built rooms.','The Indiana commission agenda describes planned metal coverings over four sloped masonry walls; no claim is made that the proposed covers are installed.']
}
(AUDIT/'evidence_r2.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'asset_sha256':asset_hash,'object_count':len(ASSET.all_objects),'sloped_segments':n,'mesh_vertices':len(mesh.vertices),'render_paths':evidence['visuals']}))
