"""Build the Wiley Dining Court asset from Purdue GIS footprint and official architectural references.

Rebuilds only massing_wiley_dining_court_wdct_8a6c669.blend. Detailed geometry is in
local meters around the proposed GIS-centroid marker recorded in audit/wiley_dining_court.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend'
AUDIT=ROOT/'audit/wiley_dining_court'
DATA=json.loads((AUDIT/'sources/gis_outline_local.json').read_text(encoding='utf-8'))
COLLECTION_NAME='Asset_massing_wiley_dining_court_wdct_8a6c669'
SCENE_NAME='Building_massing_wiley_dining_court_wdct_8a6c669'
ROOT_NAME='Wiley Dining Court (WDCT)'

# Load existing library to preserve the stable scene, collection, and root object identities.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes.get(SCENE_NAME)
col=bpy.data.collections.get(COLLECTION_NAME)
root=bpy.data.objects.get(ROOT_NAME)
assert scene and col and root and root.name in col.objects
for obj in list(col.objects):
    if obj != root:
        bpy.data.objects.remove(obj, do_unlink=True)
old_mesh=root.data
root.data=None
if old_mesh and old_mesh.users==0:
    bpy.data.meshes.remove(old_mesh)
# Rebuild the asset's material set while leaving unrelated startup materials untouched.
for mat in list(bpy.data.materials):
    if mat.name.startswith('WDCT |') and mat.users==0:
        bpy.data.materials.remove(mat)


def material(name,color,roughness=.7,metallic=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic
    return m

def brick_material():
    m=material('WDCT | warm red-brown brick',(.43,.16,.10),.83)
    nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Color1'].default_value=(.44,.17,.105,1);tex.inputs['Color2'].default_value=(.30,.095,.06,1);tex.inputs['Mortar'].default_value=(.59,.49,.38,1);tex.inputs['Scale'].default_value=2.4;tex.inputs['Mortar Size'].default_value=.018;tex.inputs['Mortar Smooth'].default_value=.08;tex.inputs['Brick Width'].default_value=.5;tex.inputs['Row Height'].default_value=.25
    coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.035;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);return m

def noise_mat(name,color1,color2,scale,rough=.7,metal=.0):
    m=material(name,color1,rough,metal);nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3.0
    coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],tex.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.18;r.color_ramp.elements[0].color=(*color1,1);r.color_ramp.elements[1].position=.82;r.color_ramp.elements[1].color=(*color2,1);nt.links.new(tex.outputs['Fac'],r.inputs['Fac']);nt.links.new(r.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.025;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);return m

BRICK=brick_material()
STONE=noise_mat('WDCT | Indiana limestone bands',(.60,.54,.43),(.79,.73,.62),5,.62)
GLASS=material('WDCT | blue-gray insulated glazing',(.055,.13,.18),.19,.45);GLASS.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
FRAME=material('WDCT | dark bronze window frames',(.095,.11,.115),.36,.68)
ROOF=noise_mat('WDCT | charcoal standing-seam roof',(.075,.095,.105),(.17,.20,.21),4,.48,.35)
WOOD=noise_mat('WDCT | exposed oak ceiling',(.24,.12,.055),(.48,.29,.12),3,.48)
WOOD_DARK=material('WDCT | oak furniture',(.33,.19,.09),.56)
TILE=noise_mat('WDCT | dining terrazzo and tile',(.39,.40,.38),(.68,.67,.62),8,.35)
CARPET=noise_mat('WDCT | dining carpet',(.22,.11,.085),(.40,.25,.17),20,.86)
STEEL=material('WDCT | kitchen stainless steel',(.44,.49,.51),.28,.72)
COUNTER=material('WDCT | serving counter walnut',(.27,.15,.085),.4)
LIGHT=material('WDCT | warm pendant diffuser',(.96,.79,.49),.25)


def mesh_obj(name,verts,faces,mat,hide_cutaway=False,uv_coords=None):
    me=bpy.data.meshes.new(name+' Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    if uv_coords:
        uv=me.uv_layers.new(name='Facade UV')
        for poly,coords in zip(me.polygons,uv_coords):
            for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
    ob=bpy.data.objects.new(name,me);col.objects.link(ob)
    if hide_cutaway: ob['hide_for_interior_preview']=True
    return ob

def cube(name,center,dims,mat,hide_cutaway=False):
    x,y,z=center;dx,dy,dz=(v*.5 for v in dims)
    verts=[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_obj(name,verts,faces,mat,hide_cutaway)

def beam_between(name,a,b,width,mat):
    va,vb=Vector(a),Vector(b);axis=(vb-va).normalized()
    ref=Vector((0,1,0)) if abs(axis.dot(Vector((0,1,0))))<.92 else Vector((1,0,0))
    u=axis.cross(ref).normalized();v=axis.cross(u).normalized();h=width*.5
    verts=[]
    for point in (va,vb):
        verts.extend([tuple(point+u*sx*h+v*sy*h) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh_obj(name,verts,faces,mat)

def polyline(name,pts,bevel,mat):
    cu=bpy.data.curves.new(name+' Curve','CURVE');cu.dimensions='3D';cu.bevel_depth=bevel;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.data.materials.append(mat);return ob

def extruded_outline(name,points,z0,z1,mat):
    n=len(points);verts=[(x,y,z0) for x,y in points]+[(x,y,z1) for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,verts,faces,mat)

# GIS-derived structural wall shell; the asset is now in a local frame centered on the proposed marker.
outline=[tuple(p) for p in DATA['outline_local_xy_m']]
rootmesh=bpy.data.meshes.new(ROOT_NAME+' | GIS wall shell')
n=len(outline);verts=[(x,y,.20) for x,y in outline]+[(x,y,6.15) for x,y in outline]
faces=[tuple(reversed(range(n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
rootmesh.from_pydata(verts,[],faces);rootmesh.materials.append(BRICK);rootmesh.update()
uv=rootmesh.uv_layers.new(name='Facade UV')
for poly in rootmesh.polygons:
    if poly.index==0:
        for li in poly.loop_indices:
            vi=rootmesh.loops[li].vertex_index;x,y,_=verts[vi];uv.data[li].uv=(x,y)
    else:
        edge=poly.index-1;i=edge;length=(Vector(outline[(i+1)%n])-Vector(outline[i])).length
        for li in poly.loop_indices:
            vi=rootmesh.loops[li].vertex_index
            if vi==i:co=(0,.20)
            elif vi==(i+1)%n:co=(length,.20)
            elif vi==(i+1)%n+n:co=(length,6.15)
            else:co=(0,6.15)
            uv.data[li].uv=co
root.data=rootmesh;root.location=(0,0,0);root.rotation_euler=(0,0,0);root.scale=(1,1,1)
root['source']='Purdue BuildingShapesZip4 FID 649 (WDCT), simplified 0.30 m';root['coordinate_frame']='detailed local meters; GIS polygon centroid origin'
root.hide_render=False;root.hide_viewport=False;root.hide_set(False)

# Main eaves / parapets and the broad gabled dining hall in the south-central frontage.
xmin=min(p[0] for p in outline);xmax=max(p[0] for p in outline);ymin=min(p[1] for p in outline);ymax=max(p[1] for p in outline)
# A thin pale limestone base follows the exact GIS perimeter.
extruded_outline('WDCT | continuous limestone foundation course',outline,.20,.58,STONE)
# Main gabled hall is informed by Purdue's exterior photograph; central axis follows the long south frontage.
gable_half=17.2; y_front=ymin+.18; y_back=8.8; eave=6.15; ridge=10.85
# Low membrane cap for the service/side wings, slightly below the tall dining hall roof.
for label,x0,x1,y0,y1 in [('west',xmin+.15,-17.4,ymin+.15,ymax-.15),('east',17.4,xmax-.15,ymin+.15,ymax-.15),('rear service',-17.2,17.2,9.0,ymax-.15)]:
    if x1>x0 and y1>y0:
        mesh_obj('WDCT | '+label+' low-slope roof',[(x0,y0,6.20),(x1,y0,6.20),(x1,y1,6.20),(x0,y1,6.20)],[(0,1,2,3)],ROOF,True)
# Main hall two gable planes, ridge runs north-south. Interior timber ceiling is a separate cutaway-view object.
mesh_obj('WDCT | main dining hall west roof slope',[(-gable_half,y_front,eave),(0,y_front,ridge), (0,y_back,ridge),(-gable_half,y_back,eave)],[(0,1,2,3)],ROOF,True)
mesh_obj('WDCT | main dining hall east roof slope',[(0,y_front,ridge),(gable_half,y_front,eave),(gable_half,y_back,eave),(0,y_back,ridge)],[(0,1,2,3)],ROOF,True)
# Gable-end masonry faces close the front and rear high volume.
for label,y in [('south',y_front-.03),('north',y_back+.03)]:
    verts=[(-gable_half,y,eave),(gable_half,y,eave),(0,y,ridge)]
    mesh_obj('WDCT | '+label+' brick gable',verts,[(0,1,2)],BRICK,True,uv_coords=[[(-gable_half,eave),(gable_half,eave),(0,ridge)]])
# Limestone fascia at eaves and a main gable rake outline.
for sx in [-1,1]:
    beam_between('WDCT | limestone gable rake', (sx*gable_half,y_front-.06,eave),(0,y_front-.06,ridge),.28,STONE)
    beam_between('WDCT | dining hall eave band',(sx*gable_half,y_front-.06,eave),(sx*gable_half,y_back,eave),.26,STONE)
# Decorative crest at the roof peak, as seen in Purdue's south-elevation photograph.
beam_between('WDCT | gable crest finial',(0,y_front-.10,ridge-.05),(0,y_front-.10,ridge+.7),.20,STONE)
beam_between('WDCT | finial crossbar',(-.85,y_front-.10,ridge+.38),(.85,y_front-.10,ridge+.38),.13,STONE)

# Full-height central glazed dining-room bay with arched top and dark mullions.
arch=[(-12.3,.82),(-12.3,5.35),(-10.0,5.92),(-6.0,6.30),(0,6.50),(6.0,6.30),(10.0,5.92),(12.3,5.35),(12.3,.82)]
glass_y=y_front-.16
mesh_obj('WDCT | south arched curtain wall glazing',[(x,glass_y,z) for x,z in arch],[tuple(range(len(arch)))],GLASS)
# outline steel frame, vertical mullions and horizontal transoms
polyline('WDCT | arched curtain wall perimeter frame',[(x,glass_y-.055,z) for x,z in arch],.16,FRAME)
for x in [-9.8,-5.0,0.0,5.0,9.8]:
    top=6.45-abs(x)*.075
    cube('WDCT | curtain wall mullion',(x,glass_y-.09,3.65),(.16,.12,max(0.2,top-1.0)),FRAME)
for z in [2.35,4.2]:cube('WDCT | curtain wall transom',(0,glass_y-.095,z),(24.2,.12,.14),FRAME)
# Brick/limestone piers divide the broad glazed bays and anchor the facade.
for x in [-16.9,-12.8,12.8,16.9]:
    cube('WDCT | south facade limestone pier',(x,y_front-.22,3.25),(.48,.42,5.55),STONE)
for x in [-29,-23,23,29,35]:
    cube('WDCT | south facade tall side window glass',(x,glass_y,3.0),(3.4,.08,4.25),GLASS)
    for dx in [-1.75,1.75]:cube('WDCT | side window bronze jamb',(x+dx,glass_y-.06,3.0),(.12,.12,4.45),FRAME)
    for z in [.82,5.18]:cube('WDCT | side window limestone sill',(x,glass_y-.10,z),(3.7,.20,.18),STONE)
    for dx in [-.58,.58]:cube('WDCT | side window mullion',(x+dx,glass_y-.08,3.0),(.10,.10,4.25),FRAME)
# Side entrances at either end of the central bay, glazed and deeply framed.
for x in [-18.7,18.7]:
    cube('WDCT | south vestibule glazing',(x,glass_y-.10,1.75),(2.5,.10,3.15),GLASS)
    for dx in [-1.3,1.3]:cube('WDCT | vestibule frame',(x+dx,glass_y-.18,1.8),(.14,.18,3.4),FRAME)
    cube('WDCT | vestibule limestone lintel',(x,glass_y-.20,3.52),(2.85,.24,.22),STONE)
# Continuous stone band and lower entry apron on the public south side.
cube('WDCT | south facade upper limestone belt',(0,y_front-.24,5.80),(58.0,.34,.33),STONE)
cube('WDCT | south entrance limestone threshold',(0,y_front-.50,.30),(32.5,.62,.28),STONE)

# Regular window rhythm on long east/west ends; evidence shows large dining-room windows rather than office bands.
for side in ['east','west']:
    xwall=(xmax-.12 if side=='east' else xmin+.12);sgn=1 if side=='east' else -1
    ys=[-16,-9,-2,5,12,19]
    for y in ys:
        if y<ymin+3 or y>ymax-3:continue
        cube('WDCT | '+side+' dining window glass',(xwall+sgn*.10,y,3.15),(.08,3.0,3.6),GLASS)
        for dy in [-1.55,1.55]:cube('WDCT | '+side+' window bronze jamb',(xwall+sgn*.16,y+dy,3.15),(.13,.14,3.8),FRAME)
        for z in [1.25,5.05]:cube('WDCT | '+side+' limestone sill',(xwall+sgn*.18,y,z),(.25,3.3,.18),STONE)
        cube('WDCT | '+side+' window mullion',(xwall+sgn*.18,y,3.15),(.14,.11,3.6),FRAME)
# North elevation smaller windows and service doors; these are schematic but compatible with the footprint.
for x in [-31,-23,-15,-7,7,15,23,31,38]:
    if x<xmin+3 or x>xmax-3:continue
    cube('WDCT | north window glass',(x,ymax-.1,2.65),(3.0,.08,2.8),GLASS)
    for dx in [-1.55,1.55]:cube('WDCT | north window jamb',(x+dx,ymax-.17,2.65),(.13,.12,3.0),FRAME)
    cube('WDCT | north window sill',(x,ymax-.19,1.18),(3.2,.18,.18),STONE)
for x in [xmin+8,xmax-6]:
    cube('WDCT | north service door',(x,ymax-.22,1.55),(1.55,.10,2.8),FRAME)
    cube('WDCT | north service door glazing',(x,ymax-.29,1.60),(1.14,.05,2.2),GLASS)
# Simple corner quoins and limestone caps distinguish the public elevations.
for x in [xmin+.25,xmax-.25]:
    for y in [ymin+.25,ymax-.25]:
        for z in [1.35,2.6,3.85,5.1]:cube('WDCT | corner limestone quoin',(x,y,z),(.40,.40,.32),STONE)

# Schematic, source-backed dining hall interior. Official project photos show vaulted timber ceiling,
# pendant lights, tables/chairs, tiled/terrazzo circulation, and food-service counters.
cube('WDCT | interior schematic dining floor',(0,-1.5,.27),(34,27,.18),TILE)
cube('WDCT | interior schematic seating carpet',(0,-5,.39),(32,17,.08),CARPET)
# Exposed oak ceiling planes, visible in model; exterior roof planes are hidden for the cutaway preview.
mesh_obj('WDCT | interior vaulted oak ceiling west',[(-gable_half+.4,y_front+1,eave-.20),(0,y_front+1,ridge-.42),(0,y_back-1,ridge-.42),(-gable_half+.4,y_back-1,eave-.20)],[(0,1,2,3)],WOOD)
mesh_obj('WDCT | interior vaulted oak ceiling east',[(0,y_front+1,ridge-.42),(gable_half-.4,y_front+1,eave-.20),(gable_half-.4,y_back-1,eave-.20),(0,y_back-1,ridge-.42)],[(0,1,2,3)],WOOD)
for y in [-18,-14,-10,-6,-2,2,6]:
    beam_between('WDCT | oak vaulted ceiling truss west',(-gable_half+.35,y,eave-.18),(0,y,ridge-.38),.20,WOOD_DARK)
    beam_between('WDCT | oak vaulted ceiling truss east',(0,y,ridge-.38),(gable_half-.35,y,eave-.18),.20,WOOD_DARK)
    beam_between('WDCT | oak ceiling tie beam',(-gable_half+.35,y,eave-.18),(gable_half-.35,y,eave-.18),.14,WOOD_DARK)
# Dining furniture is deliberately schematic. Twenty tables with simplified chairs evoke the capacity without claiming a plan.
def chair(x,y):
    cube('WDCT | schematic oak dining chair seat',(x,y,.87),(.48,.48,.12),WOOD_DARK)
    for dx in [-.19,.19]:
        for dy in [-.18,.18]:cube('WDCT | schematic chair leg',(x+dx,y+dy,.57),(.07,.07,.58),WOOD_DARK)
    cube('WDCT | schematic chair back',(x,y+.22,1.15),(.46,.08,.58),WOOD_DARK)
for row,y in enumerate([-16,-11,-6,-1,4,9]):
    for x in [-13,-7,-1,5,11]:
        cube('WDCT | schematic dining table',(x,y,1.18),(2.6,1.15,.13),WOOD_DARK)
        for dx in [-1.0,1.0]:
            chair(x+dx,y-.75);chair(x+dx,y+.75)
# Serving stations and central service counter, reflecting the documented ring of stations.
for i,x in enumerate([19.2,23.2,27.2,31.2]):
    cube('WDCT | schematic food station counter %02d'%i,(x,-1.0,1.35),(3.1,9.0,1.15),COUNTER)
    cube('WDCT | schematic stainless station top %02d'%i,(x,-1.0,1.98),(3.2,9.1,.12),STEEL)
    for y in [-4.0,-1.0,2.0]:cube('WDCT | schematic sneeze guard post',(x,y,2.8),(.08,.08,1.55),STEEL)
# Pendant cylinders and warm luminous lamps along the vault.
for y in [-16,-10,-4,2,8]:
    for x in [-10,-5,0,5,10]:
        beam_between('WDCT | schematic pendant cable',(x,y,9.45),(x,y,7.4),.045,FRAME)
        # cylinders along Z
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.16, depth=.72, location=(x,y,7.12));ob=bpy.context.object;ob.name='WDCT | schematic pendant diffuser';
        for c in list(ob.users_collection):c.objects.unlink(ob)
        col.objects.link(ob);ob.data.materials.append(LIGHT)
# Move the floor and dining items inside the main hall plan with some overlap to services intentionally avoided.

# Roof units reflect the low service roof visible in current aerial; no claim of exact equipment layout.
for i,(x,y) in enumerate([(26,14),(33,16),(-31,13),(-35,-12)]):
    cube('WDCT | roof mechanical unit %02d'%i,(x,y,6.55),(3.0,2.1,.7),STEEL,True)
    cube('WDCT | rooftop exhaust curb %02d'%i,(x,y,6.28),(3.4,2.5,.18),STONE,True)

# Keep interior-only detail out of the exterior preview while retaining all geometry in the saved asset.
for ob in col.objects:
    if any(t in ob.name.lower() for t in ('interior schematic','schematic','vaulted oak','oak vaulted','pendant cable','dining chair','dining table','food station','ceiling tie beam','ceiling truss','dining floor','seating carpet')):
        ob['hide_for_exterior_preview']=True

# Lighting, review cameras, and portable world. Keep the asset collection strictly building-specific.
world=bpy.data.worlds.get('WDCT Review World') or bpy.data.worlds.new('WDCT Review World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.38,.44,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
for o in list(scene.objects):
    if o.type in {'LIGHT','CAMERA'} and o.name.startswith('WDCT Review'):bpy.data.objects.remove(o,do_unlink=True)
def aim(obj,pt):obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
def area_light(name,loc,power,size,target):
    dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;ob=bpy.data.objects.new(name,dat);scene.collection.objects.link(ob);ob.location=loc;aim(ob,target);return ob
area_light('WDCT Review Sunbox',(-28,-42,32),7400,32,(0,-5,3))
area_light('WDCT Review Fill',(38,-10,28),3800,24,(0,0,4))
area_light('WDCT Review Rim',(0,36,32),4500,22,(0,0,4))
camdat=bpy.data.cameras.new('WDCT Review Exterior Camera');cam=bpy.data.objects.new('WDCT Review Exterior Camera',camdat);scene.collection.objects.link(cam);cam.location=(8,-106,11);aim(cam,(0,-2,4.2));camdat.type='ORTHO';camdat.ortho_scale=106;scene.camera=cam
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(AUDIT/'previews/wdct_exterior_south.png')
# Save asset before review renders. Root object and collection identifiers remain stable; all geometry is local.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
exterior_hidden=[]
for ob in col.objects:
    if ob.get('hide_for_exterior_preview'):
        ob.hide_render=True; exterior_hidden.append(ob)
bpy.ops.render.render(write_still=True)
for ob in exterior_hidden: ob.hide_render=False
cam.location=(62,-82,27);aim(cam,(0,-1,4.3));camdat.type='ORTHO';camdat.ortho_scale=122;scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.filepath=str(AUDIT/'previews/wdct_exterior_three_quarter.png')
bpy.ops.render.render(write_still=True)

# A cutaway interior review view; this changes only render visibility in memory and is not saved to the asset.
for ob in col.objects:
    if ob.get('hide_for_interior_preview'):ob.hide_render=True
    if any(t in ob.name.lower() for t in ('window','vestibule','service door','limestone pier','south facade','corner limestone')) and 'curtain wall' not in ob.name.lower():ob.hide_render=True
# Hide the outer GIS shell to expose a clearly labeled schematic dining layout.
root.hide_render=True
cam.location=(0,-14,2.5);aim(cam,(20,-1,3.0));camdat.type='PERSP';camdat.lens=35;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.filepath=str(AUDIT/'previews/wdct_interior_schematic.png')
bpy.ops.render.render(write_still=True)
print(json.dumps({'asset':str(ASSET),'collection':col.name,'scene':scene.name,'objects':len(col.objects),'origin_world_m':DATA['proposed_marker_origin_world_m'],'local_bounds_xy':DATA['bounds_xy_local_m'],'previews':['previews/wdct_exterior_south.png','previews/wdct_interior_schematic.png']}))





