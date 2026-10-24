"""Neil Armstrong Hall evidence-backed R2 source revision.
Only edits this building library and audit/complete_neil_armstrong outputs.
"""
import bpy, bmesh, json, math, os
from mathutils import Vector, geometry
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET=os.path.join(ROOT,'modular','buildings','neil_armstrong_hall.blend')
OUT=os.path.join(ROOT,'audit','complete_neil_armstrong')
SRC=os.path.join(OUT,'sources')
RD=os.path.join(OUT,'renders_r2')
os.makedirs(RD,exist_ok=True)

def ensure(ok,msg):
    if not ok: raise RuntimeError(msg)
def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,lens=50):
    data=bpy.data.cameras.new(name+'Data'); obj=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(obj)
    obj.location=loc; data.lens=lens; data.clip_start=.1; data.clip_end=1000; aim(obj,target); bpy.context.view_layer.update(); return obj
def bounds(objects):
    pts=[]; dg=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        if o.type!='MESH' or o.hide_render: continue
        e=o.evaluated_get(dg); pts.extend(e.matrix_world@Vector(c) for c in e.bound_box)
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None

def gis_points():
    fp=json.load(open(os.path.join(SRC,'gis_feature_642_20261024.json'),encoding='utf-8'))['features'][0]
    r=fp['geometry']['rings'][0]
    lat0,lon0=40.4274,-86.9137; ox,oy=-109.0,400.1893310546875
    out=[]
    for X,Y in r:
        lon=X/6378137.0*180/math.pi
        lat=(2*math.atan(math.exp(Y/6378137.0))-math.pi/2)*180/math.pi
        x=(lon-lon0)*111412.84*math.cos(math.radians(lat0))-ox
        y=(lat-lat0)*111040.0-oy
        out.append((x,y))
    return out

bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; col=bpy.data.collections.get('Asset_neil_armstrong_hall')
ensure(scene.name=='Building_neil_armstrong_hall' and col and len(col.objects)==444,'Unexpected source asset identity/count')
root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall'); ensure(root and tuple(root.location)==(0.0,0.0,0.0),'Asset root changed')
# Principal-source verification: existing audit of saved master marker records
# marker at manifest origin, 0 rotation, unit scale. Keep this asset local.
marker_audit=json.load(open(os.path.join(ROOT,'audit','batch3_master','placement_check.json'),encoding='utf-8'))
marker=next(x for x in marker_audit['rows'] if x.get('id')=='neil_armstrong_hall')
ensure(marker['marker_present'] and marker['position_error_m']==0 and marker['rotation']==[0.0,0.0,0.0] and marker['scale']==[1.0,1.0,1.0],'Placement audit does not support current marker')

# Reconcile the footprint screening in one common frame. GIS geometry is Web
# Mercator; convert it to project tangent-plane meters, then subtract manifest
# placement marker. Preserve it as a thin ground-level footprint plate rather
# than claiming the GIS polygon defines upper floor walls or room layout.
poly=gis_points(); ensure(len(poly)>20,'GIS source polygon incomplete')
area=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
foot=bpy.data.objects['ARMS_Atrium_Terrazzo_Floor']; ensure(foot.type=='MESH','GIS footprint target missing')
mat=bpy.data.materials.get('ARMS_Official_GIS_Footprint_Base')
if mat is None: mat=bpy.data.materials.new('ARMS_Official_GIS_Footprint_Base')
mat.diffuse_color=(0.23,0.27,0.30,1); mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(0.08,0.10,0.11,0); bs.inputs['Alpha'].default_value=0.0; bs.inputs['Roughness'].default_value=.82
try: mat.surface_render_method='DITHERED'
except Exception: pass
if mat.name not in [m.name for m in foot.data.materials if m]: foot.data.materials.append(mat)
mat_index=next(i for i,m in enumerate(foot.data.materials) if m and m.name==mat.name)
bm=bmesh.new(); bm.from_mesh(foot.data); bm.verts.ensure_lookup_table(); inv=foot.matrix_world.inverted()
top=[]; bot=[]
for x,y in poly:
    top.append(bm.verts.new(inv@Vector((x,y,0.035))))
    bot.append(bm.verts.new(inv@Vector((x,y,-0.10))))
bm.verts.ensure_lookup_table()
# triangulate the concave official polygon; each output point maps to the ring.
tri=geometry.tessellate_polygon([[Vector((x,y,0.0)) for x,y in poly]])
def nearest(v):
    return min(range(len(poly)),key=lambda i:(poly[i][0]-v.x)**2+(poly[i][1]-v.y)**2)
for t in tri:
    ids=list(t)
    if len(set(ids))<3: continue
    try:
        f=bm.faces.new([top[i] for i in ids]); f.material_index=mat_index
        f=bm.faces.new([bot[i] for i in reversed(ids)]); f.material_index=mat_index
    except ValueError: pass
for i in range(len(poly)):
    j=(i+1)%len(poly)
    try:
        f=bm.faces.new((top[i],bot[i],bot[j],top[j])); f.material_index=mat_index
    except ValueError: pass
bm.normal_update(); bm.to_mesh(foot.data); bm.free(); foot.data.update()
foot['source_status']='Official Purdue GIS FID 642 footprint trace; ground-level reference plate only; does not assert wall lines, interior layout, or upper-floor plan.'
foot['gis_crs_source']='EPSG:3857; converted to project local tangent-plane meters, translated by manifest marker (-109.0, 400.1893310547), no rotation.'
foot['gis_area_local_m2']=area; foot['gis_vertex_count']=len(poly)

# The engineering structural source confirms two exposed concrete bridges
# through the atrium at two levels. Existing 52 m slabs/rails were near the
# south edge and read as perimeter balconies; center them through the atrium.
# Positions are schematic since the project page supplies no bridge coordinates.
for n in ('ARMS_Balcony_Level2_Slab','ARMS_Balcony_Level2_GlassRail','ARMS_Balcony_Level2_Handrail',
          'ARMS_Balcony_Level3_Slab','ARMS_Balcony_Level3_GlassRail','ARMS_Balcony_Level3_Handrail'):
    o=bpy.data.objects.get(n); ensure(o is not None,'Missing bridge object '+n)
    o.location.y += 13.0
    if 'Slab' in n:
        o.name=o.name.replace('Balcony','Atrium_Bridge')
    elif 'GlassRail' in n: o.name=o.name.replace('Balcony','Atrium_Bridge')
    else: o.name=o.name.replace('Balcony','Atrium_Bridge')
    o['evidence_status']='Bridge at documented atrium level; exact alignment is schematic because no dimensioned as-built plan was located.'
# Preserve original manifest object names for compatibility: Blender's object
# rename is avoided below by restoring the prior labels through custom aliases.
# The exported master manifest references names; restore names from explicit map.
for current,original in [('ARMS_Atrium_Bridge_Level2_Slab','ARMS_Balcony_Level2_Slab'),('ARMS_Atrium_Bridge_Level2_GlassRail','ARMS_Balcony_Level2_GlassRail'),('ARMS_Atrium_Bridge_Level2_Handrail','ARMS_Balcony_Level2_Handrail'),('ARMS_Atrium_Bridge_Level3_Slab','ARMS_Balcony_Level3_Slab'),('ARMS_Atrium_Bridge_Level3_GlassRail','ARMS_Balcony_Level3_GlassRail'),('ARMS_Atrium_Bridge_Level3_Handrail','ARMS_Balcony_Level3_Handrail')]:
    bpy.data.objects[current].name=original

# Qualitative, source-supported wing-like roof form. The project engineer and
# case history describe cantilevered/warped wing extensions; exact curvature
# and dimensions are not published. Keep panel length almost intact and use a
# restrained taper/dihedral; preserve names/materials and mesh count.
def wing_mesh(obj):
    old=obj.data; mats=[m for m in old.materials]
    # Find original dimensions from local mesh bounds and preserve center.
    xs=[v.co.x for v in old.vertices]; ys=[v.co.y for v in old.vertices]
    xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
    width=xmax-xmin; depth=ymax-ymin
    nx,ny=17,7; halfx=width*.5+2.5; halfy=depth*.5
    top=[]; bot=[]
    for iy in range(ny):
        v=iy/(ny-1); yn=2*v-1
        for ix in range(nx):
            u=ix/(nx-1); xn=2*u-1
            # Wing tips cantilever modestly past the wall ends; smooth twist
            # lifts the span ends and edges. Values are visual estimates only.
            x=xn*halfx
            taper=1.0-0.14*(abs(xn)**1.6)
            y=yn*halfy*taper
            ztop=0.20 + 1.05*(abs(xn)**1.7) + 0.45*(yn*yn) + 0.18*xn*yn
            top.append((x,y,ztop)); bot.append((x,y,ztop-0.35))
    verts=top+bot; offset=len(top); faces=[]
    def idx(ix,iy):return iy*nx+ix
    for iy in range(ny-1):
        for ix in range(nx-1):
            a,b,c,d=idx(ix,iy),idx(ix+1,iy),idx(ix+1,iy+1),idx(ix,iy+1)
            faces.extend([(a,b,c,d),(offset+d,offset+c,offset+b,offset+a)])
    # perimeter walls
    boundary=[]
    boundary += [idx(ix,0) for ix in range(nx)]
    boundary += [idx(nx-1,iy) for iy in range(1,ny)]
    boundary += [idx(ix,ny-1) for ix in range(nx-2,-1,-1)]
    boundary += [idx(0,iy) for iy in range(ny-2,0,-1)]
    for k,a in enumerate(boundary):
        b=boundary[(k+1)%len(boundary)]; faces.append((a,offset+a,offset+b,b))
    new=bpy.data.meshes.new(obj.name+'_WingProfile_R2'); new.from_pydata(verts,[],faces);new.update()
    for m in mats:new.materials.append(m)
    # Assign every face to the panel's existing first material.
    for p in new.polygons:p.material_index=0
    obj.data=new
    obj['roof_form']='qualitative wing-like cantilever profile from project descriptions/photos; no measured elevation/curvature found.'
    obj['roof_geometry_uncertainty']='2.5 m end overhang, edge lift/taper are visual estimates; do not treat as surveyed values.'
for name in ('ARMS_East_Roof_Slab','ARMS_West_Roof_Slab'):
    wing_mesh(bpy.data.objects[name])

# Output a focused evidence bundle, preserving previous R1 evidence.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; col=bpy.data.collections['Asset_neil_armstrong_hall']; ensure(len(col.objects)==444,'Object count changed after reopen')
ensure(scene.name=='Building_neil_armstrong_hall','Scene name changed')
ensure(tuple(bpy.data.objects['AssetRoot_neil_armstrong_hall'].location)==(0.0,0.0,0.0),'Asset root changed')
ensure(len(bpy.data.objects['ARMS_Atrium_Terrazzo_Floor'].data.polygons)>200,'Footprint plate failed to triangulate')
for n in ('ARMS_Balcony_Level2_Slab','ARMS_Balcony_Level3_Slab'):
    o=bpy.data.objects[n]; ensure(abs(o.matrix_world.translation.y - (-25.1893310546875+13.0))<.02,'Bridge center offset unexpected')
# Render using temporary camera/light and hide only obscuring envelope objects.
world=scene.world or bpy.data.worlds.new('NeilReviewWorld_R2');scene.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.30,.34,.40,1);bg.inputs['Strength'].default_value=.65
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.film_transparent=False
sun_data=bpy.data.lights.new('NeilR2_KeyData','AREA');sun_data.energy=5500;sun_data.shape='DISK';sun_data.size=45
sun=bpy.data.objects.new('NeilR2_Key',sun_data);scene.collection.objects.link(sun);sun.location=(10,50,80);aim(sun,(0,-10,6))
old_camera=scene.camera
ext=camera('NeilR2_Exterior',(20,100,45),(-1,-10,9),48);ext.data.type='ORTHO';ext.data.ortho_scale=205
scene.camera=ext;scene.render.filepath=os.path.join(RD,'exterior_wing_r2.png');bpy.ops.render.render(write_still=True)
roofcam=camera('NeilR2_Roof',(90,70,110),(-1,-10,9),45);roofcam.data.type='ORTHO';roofcam.data.ortho_scale=205
scene.camera=roofcam;scene.render.filepath=os.path.join(RD,'roof_oblique_r2.png');bpy.ops.render.render(write_still=True)
inside=camera('NeilR2_Atrium',(0,-42,8),(-1.5,-11,9),42);inside.data.type='ORTHO';inside.data.ortho_scale=82
hide_names=['ARMS_Curved_Mullion_','ARMS_Curved_Transom_','ARMS_Curtain_Glass_Bay_']
cut=[]
for o in col.objects:
    if o.name.startswith(tuple(hide_names)) or o.name in ('ARMS_East_Wall_North','ARMS_West_Wall_North','ARMS_East_Roof_Slab','ARMS_West_Roof_Slab','ARMS_Atrium_South_Wall','ARMS_East_Wall_South','ARMS_West_Wall_South','ARMS_East_Roof_Penthouse','ARMS_West_Roof_Penthouse','ARMS_East_Penthouse_Louvers','ARMS_West_Penthouse_Louvers','ARMS_Atrium_Skylight_Glazing'):
        cut.append((o,o.hide_render));o.hide_render=True
scene.camera=inside;bg.inputs['Strength'].default_value=.10;scene.view_settings.exposure=-0.5;sun_data.energy=650;sun_data.size=22;scene.render.filepath=os.path.join(RD,'atrium_bridges_r2.png');bpy.ops.render.render(write_still=True)
for o,h in cut:o.hide_render=h
scene.camera=old_camera
# temporary cameras/lights removed and never written to the asset
for o in (ext,roofcam,inside,sun):bpy.data.objects.remove(o,do_unlink=True)

# Footprint comparison values in a single coordinate frame. Model shell bounds
# use asset-local object matrices from the saved source; GIS shape uses the
# exact manifest placement translation and zero marker rotation.
wall_names=('ARMS_East_Wall_North','ARMS_East_Wall_South','ARMS_East_Wall_East','ARMS_West_Wall_North','ARMS_West_Wall_South','ARMS_West_Wall_West','ARMS_Atrium_South_Wall')
wall_objects=[bpy.data.objects[n] for n in wall_names]
wb=bounds(wall_objects);gb=[[min(p[i] for p in poly),max(p[i] for p in poly)] for i in range(2)];gb.append([0,0])
validation={
 'building_id':'neil_armstrong_hall','revision':'R2','asset_path':'modular/buildings/neil_armstrong_hall.blend','scene':scene.name,'collection':col.name,'object_count':len(col.objects),
 'saved_then_reopened':True,'asset_root_location':list(bpy.data.objects['AssetRoot_neil_armstrong_hall'].location),
 'manifest_marker_read_only':{'marker_present':marker['marker_present'],'expected_xy':marker['expected_xy'],'actual_xyz':marker['actual_xyz'],'position_error_m':marker['position_error_m'],'rotation':marker['rotation'],'scale':marker['scale']},
 'gis_polygon_local_bounds_m':gb,'gis_polygon_area_local_m2':area,'gis_polygon_vertices':len(poly),'shell_wall_matrix_bounds_m':wb,
 'footprint_representation':'GIS polygon appended to existing atrium floor mesh as thin ground-level reference slab; does not claim upper-floor walls/room layout.',
 'atrium_bridge_objects':{n:{'matrix_world_center':list(bpy.data.objects[n].matrix_world.translation),'size':list(bpy.data.objects[n].dimensions)} for n in ('ARMS_Balcony_Level2_Slab','ARMS_Balcony_Level3_Slab')},
 'roof_objects':{n:{'dimensions':list(bpy.data.objects[n].dimensions),'vertices':len(bpy.data.objects[n].data.vertices),'form':'qualitative wing profile; exact curvature/overhang unmeasured'} for n in ('ARMS_East_Roof_Slab','ARMS_West_Roof_Slab')},
 'temporary_review_objects_saved':False,'cutaway_hides_render_only':True,
 'renders':['renders_r2/exterior_wing_r2.png','renders_r2/roof_oblique_r2.png','renders_r2/atrium_bridges_r2.png']}
with open(os.path.join(OUT,'validation_r2.json'),'w',encoding='utf8') as f:json.dump(validation,f,indent=2)
# Structured sources
sources={
 'building_id':'neil_armstrong_hall','retrieved_date':'2026-10-24','revision':'R2','sources':[
  {'title':'Neil Armstrong Hall of Engineering','provider':'Purdue University official BuildingShapesZip4 ArcGIS FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':642,'source_date':'not stated; layer dataEditDate 2026-08-30','retrieval_date':'2026-10-24','crs':'EPSG:3857 (WKID 102100, latest 3857)','raw_snapshot':'sources/gis_feature_642_20261024.json','method':'Converted feature vertices from Web Mercator to lon/lat, then Purdue project local tangent approximation; subtracted manifest placement marker (-109.0, 400.1893310547), zero marker rotation. Area computed after local projection.','result':{'local_bounds_m':gb,'local_area_m2':area,'vertex_count':len(poly)},'uncertainty':'Building polygon supports a ground footprint boundary. It does not define facade wall lines, courtyard voids, upper-floor plans, or exact entrance position. Used only as a thin ground-level plate, not extruded walls.'},
  {'title':'Neil Armstrong Hall of Engineering structural project description','provider':'FRP structural engineering project page','url':'https://frpinc.com/projects/neil-armstrong-hall-of-engineering/','source_date':'Project completed 2006; source page current at retrieval','retrieval_date':'2026-10-24','crs':'Not applicable; project description and photographs','evidence':['Three-story cast-in-place frame with steel mechanical penthouse and basement/partial sub-basement.','Elaborate cantilevered steel roof truss.','Exposed concrete bridge at two levels through atrium and three concrete stairs.','Elevated tiered lecture room.'],'method':'Used to relabel/reposition existing model slabs as two atrium bridge levels and to guide source-supported massing/roof interpretation. Bridge positions, routes and stair locations remain schematic; page provides no dimensioned plan.'},
  {'title':'Neil Armstrong Hall of Engineering case history','provider':'Design and Build With Metal / Arconic','url':'https://designandbuildwithmetal.com/featured-projects/neil-armstrong-hall-of-engineering','source_date':'Project-era case history; building completed 2007','retrieval_date':'2026-10-24','crs':'Not applicable; descriptive source','evidence':['High roof described as a warped wing-like cantilever on both ends, clad in Mayflower Red ACM.','Atrium ceiling described as 53 feet high.','Canopy/vestibule clad in Sea Wolf ACM.'],'method':'Roof slab mesh reshaped to qualitative tapered/warped wing profile with restrained edge lift and small illustrative overhang; exact curvature/overhang is not measured. R1 53 ft atrium datum and materials preserved.'},
  {'title':'3D anamorphic video wall features Purdue’s most consequential engineers','provider':'Purdue University College of Engineering','url':'https://engineering.purdue.edu/Engr/AboutUs/News/Spotlights/2025/2025-0619-3d-anamorphic-video-wall','source_date':'2025-06-19','retrieval_date':'2026-10-24','crs':'Not applicable; current interior exhibit description','evidence':['New anamorphic LED video wall installed inside Armstrong atrium in 2025.','A specific floor sticker/viewing point guides visitors; screen described as flush in brick wall above doorway.'],'method':'Recorded as current exhibit evidence; not geometrically added in R2 because available source gives screen dimensions but not a registered wall/door location in the current source asset.'},
 {'title':'ARMS – Armstrong Hall Building Emergency Plan','provider':'Purdue University Office of Emergency Preparedness','url':'https://www.purdue.edu/operations/emergency-preparedness/arms/','source_date':'Revision 2026-03-27','retrieval_date':'2026-10-24','crs':'Not applicable; facility record','evidence':['Four levels: lower level, at grade, and two upper floors.'],'method':'Context for interior floors only; no floor plates or elevations.'}
 ],
 'r2_changes':[
  {'change':'Added GIS-traced thin base footprint to existing atrium floor mesh.','basis':'Official feature 642 footprint and manifest marker transform.','uncertainty':'Ground footprint polygon only; no claims about wall lines, holes, or upper levels.'},
  {'change':'Repositioned existing two slabs/rails toward atrium center to represent the structural source’s two exposed bridge levels.','basis':'Structural engineer page says exposed concrete bridge at two levels through atrium.','uncertainty':'Exact bridge route/coordinates unsupported; current centerline is a renderable schematic.'},
  {'change':'Rebuilt existing red roof slab meshes as tapered, warped winglike surfaces.','basis':'Project case history and 2007 building photos identify a winglike cantilever roof.','uncertainty':'Exact roof curvature, tip shape, and overhang are not dimensioned; modeled profile is qualitative.'}
 ],
 'validation':'See validation_r2.json. Individual asset saved and reopened before validation and renders. Master file and shared project files were not written.'}
with open(os.path.join(OUT,'evidence_r2.json'),'w',encoding='utf8') as f:json.dump(sources,f,indent=2)
print(json.dumps(validation,indent=2))


