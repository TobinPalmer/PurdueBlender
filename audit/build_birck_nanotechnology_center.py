import bpy, json, math, os, statistics
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from math import radians

ROOT = os.path.abspath('.')
SRC = os.path.join(ROOT, 'audit', 'official_purdue_buildings_wgs84.json')
OUT = os.path.join(ROOT, 'modular', 'buildings', 'birck_nanotechnology_center.blend')
PREVIEW = os.path.join(ROOT, 'audit', 'birck_nanotechnology_center', 'birck_front_preview.png')
PLAN = os.path.join(ROOT, 'audit', 'birck_nanotechnology_center', 'birck_plan_preview.png')
EVID = os.path.join(ROOT, 'audit', 'birck_nanotechnology_center', 'evidence.json')
FEATURE_OUT = os.path.join(ROOT, 'audit', 'birck_nanotechnology_center', 'official_feature_604.json')

# Existing massing bounds center is retained for an easy replacement in the master.
ORIGIN_X, ORIGIN_Y = (-927.1537475585938, -525.4301910400391)
LON0, LAT0 = -86.9137, 40.4274

with open(SRC, encoding='utf-8') as f:
    fc=json.load(f)
feature=next(x for x in fc['features'] if x['attributes'].get('FID')==604)
with open(FEATURE_OUT,'w',encoding='utf-8') as f:
    json.dump(feature,f,indent=2)
attrs=feature['attributes']
ring=feature['geometry']['rings'][0]
xy=[]
for lon,lat in ring:
    x=(lon-LON0)*111412.84*math.cos(math.radians(LAT0))
    y=(lat-LAT0)*111040.0
    xy.append((x-ORIGIN_X, y-ORIGIN_Y))
# Remove duplicate closing vertex if present.
if math.dist(xy[0],xy[-1])<1e-6: xy=xy[:-1]

# Remove near-duplicate successive points, but preserve the fine GIS-derived outline.
clean=[]
for p in xy:
    if not clean or math.dist(p,clean[-1])>0.025: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<0.025: clean.pop()
xy=clean

# Empty the default file and establish one exported collection plus isolated preview set.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection')
if base: base.name='Asset_birck_nanotechnology_center'
else:
    base=bpy.data.collections.new('Asset_birck_nanotechnology_center'); bpy.context.scene.collection.children.link(base)
asset=base
asset['building_id']='birck_nanotechnology_center'
asset['source_feature']='Purdue BuildingShapes FeatureServer/0 FID 604 (BRK)'
asset['local_origin_project_m']=[ORIGIN_X,ORIGIN_Y]
asset['plan_xy_source_crs']='EPSG:4326 snapshot derived from ArcGIS EPSG:3857; converted with project local approximation'
preview_col=bpy.data.collections.new('Preview_Set'); bpy.context.scene.collection.children.link(preview_col)

def link_obj(obj, collection=asset):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def make_mat(name, base_color, roughness=0.6, metallic=0.0, noise_scale=7.0, color_variation=0.035, bump_strength=0.08, bump_distance=0.025, alpha=1.0, transmission=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*base_color,alpha); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value=roughness; bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Alpha'].default_value=alpha; bs.inputs['Transmission Weight'].default_value=transmission
    tex=nt.nodes.new('ShaderNodeTexCoord'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=noise_scale; noise.inputs['Detail'].default_value=3.2; noise.inputs['Roughness'].default_value=0.68
    nt.links.new(tex.outputs['Generated'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); lo=tuple(max(0,c*(1-color_variation)) for c in base_color)+(1,); hi=tuple(min(1,c*(1+color_variation)) for c in base_color)+(1,)
    ramp.color_ramp.elements[0].position=0.24; ramp.color_ramp.elements[0].color=lo; ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=hi
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=bump_strength; bump.inputs['Distance'].default_value=bump_distance
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

corten=make_mat('BIRCK • oxidized copper / warm bronze rainscreen',(0.31,0.115,0.065),.48,.42,12,.12,.12,.018)
panel=make_mat('BIRCK • pale warm-gray insulated metal panel',(0.53,0.55,0.53),.64,.18,18,.075,.08,.012)
concrete=make_mat('BIRCK • cast concrete plinth',(0.36,0.37,0.35),.82,.05,9,.08,.16,.025)
glass=make_mat('BIRCK • blue-gray reflective curtain glazing',(0.035,0.095,0.135),.16,.36,3,.12,.015,.006,.74,.12)
roofmat=make_mat('BIRCK • charcoal membrane roof',(0.075,0.085,0.09),.77,.12,22,.10,.14,.012)
metal=make_mat('BIRCK • anodized aluminum mullions',(0.31,0.34,0.35),.34,.72,14,.05,.04,.004)
interior=make_mat('BIRCK • lobby limestone terrazzo',(0.50,0.48,0.41),.49,.04,10,.08,.08,.01)
wood=make_mat('BIRCK • interior timber soffit',(0.31,0.17,0.08),.55,.05,12,.1,.08,.01)
lightmat=bpy.data.materials.new('BIRCK • warm lobby lighting'); lightmat.use_nodes=True
lbs=next(n for n in lightmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); lbs.inputs['Base Color'].default_value=(1.0,.67,.34,1); lbs.inputs['Emission Color'].default_value=(1.0,.48,.18,1); lbs.inputs['Emission Strength'].default_value=1.25

# Main three-level enclosure follows the complete GIS ring without smoothing away its irregular wings.
N=len(xy); z0=0.20; ztop=12.8
verts=[(x,y,z) for z in (z0,ztop) for x,y in xy]
faces=[]
for i in range(N): faces.append((i,(i+1)%N,(i+1)%N+N,i+N))
faces.append(tuple(range(N,2*N)))
mesh=bpy.data.meshes.new('Birck GIS footprint extruded two levels'); mesh.from_pydata(verts,[],faces); mesh.materials.clear()
for m in (panel,concrete,roofmat,corten): mesh.materials.append(m)
mesh.update(); body=bpy.data.objects.new('Birck • full GIS-footprint research block',mesh); asset.objects.link(body)
# material faces: plinth by elevation; upper south-facing volume selectively corten; flat roof membrane.
for i,p in enumerate(mesh.polygons):
    if i==N: p.material_index=2
    else:
        x1,y1=xy[i]; x2,y2=xy[(i+1)%N]; mx=(x1+x2)/2; my=(y1+y2)/2
        # South-facing entrance wing receives the distinctive warm bronze/rust screen.
        if my < -24 and -5 < mx < 28 and p.area>2.0: p.material_index=3
        elif (my < -24 or mx > 38) and p.area>1.0: p.material_index=0
        else: p.material_index=1
# recalc normals consistently
import bmesh
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free(); mesh.update()

# Ground-floor limestone plinth follows the exact perimeter as a continuous low course.
def add_box(name, loc, scale, mat, rot=0, collection=asset, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; o.rotation_euler[2]=rot; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); link_obj(o,collection); o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Soft architectural arris','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
# facade glazing + aluminum frame geometry; exact wall directions follow the GIS-derived plan.
glass_verts=[]; glass_faces=[]; mullion_specs=[]
for i in range(N):
    a=Vector((xy[i][0],xy[i][1],0)); b=Vector((xy[(i+1)%N][0],xy[(i+1)%N][1],0)); d=b-a; L=d.length
    if L<2.3: continue
    mid=(a+b)*.5
    radial=Vector((mid.x,mid.y,0));
    if radial.length<1e-5: continue
    outward=radial.normalized()
    # Most generous glazing at the south-facing curve and eastern glazed wing; restrained ribbons elsewhere.
    south = outward.y < -0.56 and mid.y < -17
    east = outward.x > 0.72 and mid.x > 30
    north = outward.y > 0.64 and mid.y > 24
    west = outward.x < -0.75 and mid.x < -30
    eligible = south or east or (north and -8 < mid.x < 35) or (west and -18 < mid.y < 25)
    if not eligible: continue
    t=d.normalized(); n=Vector((outward.x,outward.y,0)); offset=n*.07
    # Main three-level glazing ribbons with generous sill/spandrel bands.
    for za,zb in ((1.25,3.45),(5.20,7.40),(9.15,11.35)):
        panel_width=2.4; inset=.42; usable=L-2*inset
        if usable<.6: continue
        count=max(1, math.ceil(usable/panel_width)); cell=usable/count
        for k in range(count):
            s0=inset+k*cell+.055; s1=inset+(k+1)*cell-.055
            if s1-s0<.15: continue
            p0=a+t*s0+offset; p1=a+t*s1+offset
            j=len(glass_verts); glass_verts.extend([(p0.x,p0.y,za),(p1.x,p1.y,za),(p1.x,p1.y,zb),(p0.x,p0.y,zb)]); glass_faces.append((j,j+1,j+2,j+3))
            mullion_specs.append((p0,p1,za,zb,n))
# Join the glaze surface into one batched mesh.
gm=bpy.data.meshes.new('Birck curtain wall glazing panels'); gm.from_pydata(glass_verts,[],glass_faces); gm.materials.append(glass); gm.update(); go=bpy.data.objects.new('Birck • glazed window bands',gm); asset.objects.link(go)
# Consolidated mullion and transom mesh keeps the campus library lightweight.
frame_verts=[]; frame_faces=[]
def append_frame_box(center,tangent,normal,width,depth,zmin,zmax):
    start=len(frame_verts)
    for z in (zmin,zmax):
        for st,sn in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            v=center+tangent*(st*width*.5)+normal*(sn*depth*.5)
            frame_verts.append((v.x,v.y,z))
    frame_faces.extend([(start,start+1,start+2,start+3),(start+4,start+7,start+6,start+5),(start,start+4,start+5,start+1),(start+1,start+5,start+6,start+2),(start+2,start+6,start+7,start+3),(start+3,start+7,start+4,start)])
for p0,p1,za,zb,n in mullion_specs:
    d=p1-p0; tangent=Vector((d.x,d.y,0)).normalized(); normal=Vector((n.x,n.y,0)).normalized()
    c=(p0+p1)*.5+normal*.025
    append_frame_box(c,tangent,normal,.075,.055,za,zb)
    transom_c=c+normal*.012+Vector((0,0,.84))
    append_frame_box(transom_c,tangent,normal,max(.18,d.length-.05),.055,za+.8175,za+.8625)
fm=bpy.data.meshes.new('Birck consolidated aluminum mullions and transoms'); fm.from_pydata(frame_verts,[],frame_faces); fm.materials.append(metal); fm.update()
fo=bpy.data.objects.new('Birck • consolidated aluminum facade frames',fm); asset.objects.link(fo)
# Ground floor spandrel/plinth; low sill band at base and stringcourse between levels.
# More visual detail on main entrance facade: find the longest south-facing GIS segment.
front_candidates=[]
for i in range(N):
    a=Vector((xy[i][0],xy[i][1],0)); b=Vector((xy[(i+1)%N][0],xy[(i+1)%N][1],0)); d=b-a
    mid=(a+b)*.5; radial=Vector((mid.x,mid.y,0))
    if d.length>3 and radial.length>1e-4 and radial.normalized().y < -.58:
        front_candidates.append((d.length,i,a,b,radial.normalized()))
front_candidates.sort(reverse=True,key=lambda q:q[0])
entry_center=None; entry_tangent=None; entry_normal=None
if front_candidates:
    _,ei,ea,eb,en=front_candidates[0]; ed=(eb-ea).normalized(); entry_center=(ea+eb)*.5; entry_tangent=ed; entry_normal=en
    # Recessed vestibule and entrance canopy; photograph-supported lobby glazing and sign band.
    door_w=min(5.4,(eb-ea).length*.5); door_h=3.05
    # door dark bronze aluminum frame plus pair of glazed leaves facing south
    c=entry_center+entry_normal*.17
    pL=c-entry_tangent*door_w*.5; pR=c+entry_tangent*door_w*.5
    dv=[(pL.x,pL.y,.2),(pR.x,pR.y,.2),(pR.x,pR.y,door_h),(pL.x,pL.y,door_h)]
    dm=bpy.data.meshes.new('Birck entry door glazing'); dm.from_pydata(dv,[],[(0,1,2,3)]); dm.materials.append(glass); dm.update(); dob=bpy.data.objects.new('Birck • main double-height entrance doors',dm); asset.objects.link(dob)
    # warm bronze portal surround and canopy
    center=entry_center+entry_normal*.28
    add_box('Birck • entry canopy',(center.x,center.y,3.35),(door_w+3.2,2.3,.36),corten,math.atan2(entry_tangent.y,entry_tangent.x),bevel=.045)
    # canopy brackets
    for s in (-1,1):
        q=center+entry_tangent*(s*(door_w*.5+1.2))+entry_normal*.26
        add_box('Birck • canopy blade',(q.x,q.y,2.75),(.12,.52,1.15),metal,math.atan2(entry_tangent.y,entry_tangent.x),bevel=.025)
    # Main sign set just above the canopy on the warm wall/screen.
    bpy.ops.object.text_add(location=(center.x-entry_tangent*5.4+entry_normal*.34).to_tuple() if False else (center-entry_tangent*5.6+entry_normal*.38+Vector((0,0,4.85))).to_tuple())
    text=bpy.context.object; text.name='Birck • facade lettering'; link_obj(text); text.data.body='MICHAEL AND KAY BIRCK\\nNANOTECHNOLOGY CENTER'; text.data.align_x='CENTER'; text.data.align_y='CENTER'; text.data.size=.52; text.data.space_character=1.08; text.data.extrude=.008; text.data.materials.append(panel)
    # default text lies XY; rotate to face south and align tangent to the facade.
    text.rotation_euler=(radians(90),0,math.atan2(entry_tangent.y,entry_tangent.x))
    # visible interior: two pale terrazzo slabs, columns and warm soffit at the glazed lobby.
    # scene geometry remains local; interior modules are restrained and only present in the entrance/lobby zone.
    interior_center=entry_center-entry_normal*10.0
    add_box('Birck • lobby lower terrazzo',(interior_center.x,interior_center.y,.38),(18,14,.18),interior,bevel=.015)
    add_box('Birck • lobby upper bridge',(interior_center.x,interior_center.y,4.45),(18,14,.26),interior,bevel=.015)
    # Timber soffit over reception and mezzanine edge
    add_box('Birck • lobby upper bridge',(interior_center.x,interior_center.y,8.65),(18,14,.26),interior,bevel=.015)
    add_box('Birck • lobby timber soffit',(interior_center.x,interior_center.y,11.55),(20,11,.22),wood,bevel=.02)
    for s in (-1,1):
        q=interior_center+Vector((s*5.4,0,0))
        add_box('Birck • lobby structural column',(q.x,q.y,6.35),(.36,.36,12.1),metal,bevel=.035)
    # a warm, understated luminous ceiling detail seen through the curtain wall
    add_box('Birck • warm lobby light',(interior_center.x,interior_center.y,11.42),(8,.12,.045),lightmat,bevel=.01)

# Flat roof mechanical plant: low, screened blocks consistent with a cleanroom research facility.
# Use two muted penthouse clusters so the roofline reads as layered flat-roof massing, not a gable.
for i,(x,y,sx,sy,h) in enumerate([(-23,19,13,8,2.0),(19,17,17,10,2.6),(34,-8,8,6,1.4),(-37,-4,7,8,1.2)]):
    add_box(f'Birck • rooftop mechanical penthouse {i+1}',(x,y,ztop+h/2),(sx,sy,h),panel,bevel=.08)
    add_box(f'Birck • rooftop plant curb {i+1}',(x,y,ztop+.12),(sx+.42,sy+.42,.24),concrete,bevel=.04)
    # air handling risers / vent stacks are deliberately low against the roof silhouette
    for k in range(3 if i<2 else 2):
        xx=x-sx*.28+k*(sx*.28)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.34, depth=.8, location=(xx,y,ztop+h+.4))
        o=bpy.context.object; o.name=f'Birck • HVAC exhaust {i+1}-{k+1}'; link_obj(o); o.data.materials.append(metal)

# Modest roof edge screen on three main sides, approximated by thin rectangular bars attached to the perimeter.
for i in range(N):
    a=Vector((xy[i][0],xy[i][1],0)); b=Vector((xy[(i+1)%N][0],xy[(i+1)%N][1],0)); d=b-a; L=d.length
    if L<4.5: continue
    m=(a+b)*.5; n=Vector((m.x,m.y,0))
    if n.length<1e-3: continue
    n.normalize(); mid=m+n*.08
    add_box(f'Birck • flat-roof parapet segment {i:03d}',(mid.x,mid.y,ztop+.28),(L+.06,.22,.56),panel,math.atan2(d.y,d.x),bevel=.025)

# Detail: restrained exterior recessed louver panels near HVAC-facing walls.
for i,(x,y,rot) in enumerate([(-26,21,0),(17,20,0),(38,-6,math.pi/2)]):
    for k in range(12):
        z=1.8+k*.78
        add_box(f'Birck • intake louver {i}-{k}',(x,y,z),(2.8,.08,.09),metal,rot,bevel=.012)

# Local presentation setup. Preview_Set never enters the exported asset collection.
# Ground/background plane
groundmat=make_mat('Preview • neutral ground',(0.20,.22,.20),.9,0,3,.1,.04,.01)
add_box('Preview • ground',(0,0,-.45),(240,240,.35),groundmat,collection=preview_col)
# Sun and soft fill
ld=bpy.data.lights.new('Preview • sunset-neutral key','AREA'); lo=bpy.data.objects.new(ld.name,ld); preview_col.objects.link(lo); lo.location=(-65,-95,95); ld.energy=140000; ld.shape='DISK'; ld.size=70
ld2=bpy.data.lights.new('Preview • facade fill','AREA'); lo2=bpy.data.objects.new(ld2.name,ld2); preview_col.objects.link(lo2); lo2.location=(80,-15,45); ld2.energy=65000; ld2.size=55
ld3=bpy.data.lights.new('Preview • roof rim','AREA'); lo3=bpy.data.objects.new(ld3.name,ld3); preview_col.objects.link(lo3); lo3.location=(-15,80,75); ld3.energy=90000; ld3.size=45
world=bpy.data.worlds.new('Preview • clear studio sky') if not bpy.data.worlds else bpy.data.worlds[0]; bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.23,.34,.47,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('Birck front architectural camera'); cam=bpy.data.objects.new(camd.name,camd); preview_col.objects.link(cam); cam.location=(112,-188,38); aim(cam,(22,-4,5)); camd.lens=48; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1440; scene.render.resolution_y=1120; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
scene.camera.data.dof.use_dof=False
scene.render.filepath=PREVIEW
# set metadata and maintain actual source linkage info
scene['Birck_footprint_feature_id']='FeatureServer/0 FID 604 / BRK'
scene['Birck_height_status']='estimated: 2 floors above grade with roof plant, based on published 2-floor facility description and massing envelope'
scene['Birck_footprint_status']='official polygon traced; local projected approximation; matches old block envelope within <0.5m'

# Render exterior and orthographic plan previews.
bpy.context.view_layer.update(); bpy.ops.render.render(write_still=True)
# Top plan render with camera at exact overhead
cam.location=(0,0,175); aim(cam,(0,0,0)); camd.type='ORTHO'; camd.ortho_scale=142; scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.filepath=PLAN; bpy.ops.render.render(write_still=True)
# Reset to entrance view in saved project
camd.type='PERSP'; cam.location=(112,-188,38); aim(cam,(22,-4,5)); camd.lens=48; scene.render.resolution_x=1440; scene.render.resolution_y=1120; scene.render.filepath=PREVIEW
scene.camera=cam
# Select and activate the exported collection; preserve collection as clearly named library asset.
for o in bpy.context.selected_objects: o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
# Save standalone evidence JSON after actual mesh dimensions are evaluated.
asset_objects=[o for o in asset.objects if o.type in {'MESH','CURVE','FONT'}]
coords=[]
for o in asset_objects:
    for corner in o.bound_box:
        coords.append(o.matrix_world @ Vector(corner))
mins=[min(v[a] for v in coords) for a in range(3)]; maxs=[max(v[a] for v in coords) for a in range(3)]
materials=[]
for m in bpy.data.materials:
    if m.name.startswith('BIRCK'):
        connected=False
        if m.use_nodes:
            for node in m.node_tree.nodes:
                if node.type=='BSDF_PRINCIPLED' and any(s.name in {'Base Color','Normal'} and s.is_linked for s in node.inputs): connected=True
        materials.append({'name':m.name,'connected_texture_inputs':connected})
record={
 'building_id':'massing_birck_nanotechnology_center_362d0b7','new_library':os.path.relpath(OUT,ROOT).replace('\\','/'),'exported_collection':'Asset_birck_nanotechnology_center',
 'retrieved_utc':'2026-10-23','source_feature':{'provider':'Purdue University BuildingShapes ArcGIS feature service','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':604,'global_id':attrs.get('GlobalID'),'source_code':attrs.get('BLDG_ABBR'),'building_name':attrs.get('BUILDING_N'),'record_address':attrs.get('ADDRESS'),'feature_service_crs':'EPSG:3857 (WKID 102100 / latestWKID 3857)','local_snapshot':'audit/official_purdue_buildings_wgs84.json (WGS84/EPSG:4326 coordinate snapshot)','retrieval_date':'2026-10-23','service_item_modified_ms':1788192824000,'service_item_modified_utc':'2026-08-31T16:13:44Z','source_attributes':{k:attrs.get(k) for k in ['NUM_LEVELS','CountOfFLO','Extrution','Elevation','BUILT','OCCUPIED','Shape__Area','Shape__Length']}},
 'photos':[{'provider':'Purdue ECE','date':'2023 page publication; image source current as page','url':'https://engineering.purdue.edu/ECE/News/2023/seeing-stars-purdue-trains-next-generation-of-semiconductor-engineers/Birck.jpg','observed_details':'large glass entrance/curtain wall, warm rust/wood-tone panel volume and entrance signage'}, {'provider':'Birck Nanotechnology Center official site','date':'current 2026 site image','url':'https://birck.research.purdue.edu/app/uploads/2026/01/Front-of-Birck-500-pxl.jpeg','observed_details':'front facade with curved glazing, bronze-brown cladding and low landscaping'}, {'provider':'Purdue News Service/David Umberger','date':'2005-10-08','url':'https://www.purdue.edu/uns/uns/images/+2005/birck-nanocenter-ext.jpg','observed_details':'original exterior composition: curved glass wing, rust-colored panels, campus setting'}, {'provider':'Purdue ECE','date':'2024-04-29 news page','url':'https://engineering.purdue.edu/ECE/News/2024/nsf-director-panchanathan-us-sen-young-tout-value-of-university-private-sector-partnerships-to-grow-national-economic-security','observed_details':'entrance to Scifres lab and building exterior; renovation announced, not modeled as complete'}],
 'street_level_map':{'provider':'Google Maps Street View','url':'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.42275,-86.92385','retrieved_date':'2026-10-23','viewpoint_lat_lon':[40.42275,-86.92385],'observation':'visible pale laboratory/service facade, three horizontal window levels, rooftop/service equipment and a glazed connector; the panoramic point is just east of the mapped Birck polygon and may include the attached or neighboring lab wing','pano_capture_date':'not exposed in the inspected Maps view','limitations':'center-of-building viewpoint at 40.42276,-86.92465 reports no Street View imagery; the usable panorama is nearby and exact wall identity is ambiguous'},
 'footprint_transform':{'input_crs':'EPSG:4326 geographic coordinates in local source JSON, transformed from ArcGIS EPSG:3857 snapshot','project_formula_x':'(lon + 86.9137) * 111412.84 * cos(radians(40.4274)','project_formula_y':'(lat - 40.4274) * 111040.0','local_origin_project_m':[ORIGIN_X,ORIGIN_Y],'transform_status':'project approximate local coordinate transform; not surveyed CRS'},
 'dimensions':{'footprint_vertices_original':len(ring),'footprint_vertices_used':len(xy),'local_bounds_m':{'min':mins,'max':maxs},'old_massing_envelope_m':{'x':[-984.744384765625,-869.5631103515625],'y':[-575.8645629882812,-474.9958190917969],'z':[0,16]},'height_basis':'unverified estimate: GIS NUM_LEVELS=3 and nearby east-side Street View shows three horizontal levels; a 2005 Purdue release described the original facility as two-floor. Current model uses a 12.8m roof datum with low rooftop plant to ~16m; both heights are estimates because GIS Extrution=42 unit is unconfirmed and no surveyed elevation/section was found.'},
 'geometry_edits':['replaced one-object placeholder only in newly created detailed library; no massing source/master/manifest edited','extruded GIS footprint into three-level flat-roof shell','added glazed perimeter ribbons and mullions to selected south/east/north/west facades','added bronze/corten rainscreen at south entry wing, entrance doors/canopy/sign','added a visible lobby mezzanine floor, structural columns, terrazzo and warm soffit lighting','added flat membrane roof, HVAC penthouses and low exhaust stacks'],
 'materials':materials,'previews':[os.path.relpath(PREVIEW,ROOT).replace('\\','/'),os.path.relpath(PLAN,ROOT).replace('\\','/')],
 'uncertainty':['GIS polygon can validate only plan extent/shape, not facade divisions or height; the GIS feature’s exact source date is not present in the downloaded item record.','Only exterior imagery was used for facade organization. Interior plan/access was unavailable; the lobby insert is a restrained plausible interpretation visible behind the glass, not a verified floor plan.','Current 2024 renovation work is scheduled through 2027; latest completion/as-built state could differ from the 2023–2026 photographs.','Street View link points at the building but Google panorama capture date/heading was not independently captured in this environment.']}
with open(EVID,'w',encoding='utf-8') as f: json.dump(record,f,indent=2)
print(json.dumps({'saved':OUT,'preview':PREVIEW,'plan':PLAN,'feature_id':attrs.get('FID'),'points':len(xy),'objects':len(asset_objects),'material_texture_nodes':materials,'bounds_local_m':{'min':mins,'max':maxs}},indent=2))






