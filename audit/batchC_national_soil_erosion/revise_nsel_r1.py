import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'batchC_national_soil_erosion'
ASSET = ROOT / 'modular' / 'buildings' / 'national_soil_erosion_laboratory.blend'
AUDIT.mkdir(parents=True, exist_ok=True)

COL = bpy.data.collections['Asset_national_soil_erosion_laboratory']
FACADE = bpy.data.collections['SOIL_Facade']
WALL = bpy.data.objects['National Soil Erosion Research Laboratory | GIS perimeter wall panels with real glazing openings']
ROOF = bpy.data.objects['SOIL | structural flat roof']

# Local plane is offset by the registered FID242 footprint center.
X_BREAK = -6.49
LOW_ROOF_Z = 5.20
ROOF_THICK = 0.22
HIGH_WALL_TOP = 7.32
DELTA = HIGH_WALL_TOP - LOW_ROOF_Z

def obj_world_bounds(obj):
    vs = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [[min(v[i] for v in vs), max(v[i] for v in vs)] for i in range(3)]

# Split the wall envelope using its individually modeled quads. These are
# disconnected facade panels, so trimming faces avoids non-manifold Boolean
# artifacts while retaining the supported lower wall and corner returns.
src=WALL.data
newverts=[]; newfaces=[]; face_mats=[]
deleted_wall_faces=0; clipped_wall_faces=0
def clip_face_to_west(coords,xcut):
    out=[]
    for a,b in zip(coords,coords[1:]+coords[:1]):
        ina=a.x<=xcut; inb=b.x<=xcut
        if ina and inb: out.append(b)
        elif ina and not inb:
            t=(xcut-a.x)/(b.x-a.x);out.append(Vector((xcut,a.y+t*(b.y-a.y),a.z+t*(b.z-a.z))))
        elif not ina and inb:
            t=(xcut-a.x)/(b.x-a.x);out.append(Vector((xcut,a.y+t*(b.y-a.y),a.z+t*(b.z-a.z))));out.append(b)
    return out
for poly in src.polygons:
    coords=[WALL.matrix_world @ src.vertices[i].co for i in poly.vertices]
    cx=sum(v.x for v in coords)/len(coords)
    zmin=min(v.z for v in coords); zmax=max(v.z for v in coords)
    if cx >= X_BREAK and zmin >= 5.0:
        deleted_wall_faces += 1
        continue
    if min(v.x for v in coords)<X_BREAK and max(v.x for v in coords)>X_BREAK and zmax>LOW_ROOF_Z:
        coords=clip_face_to_west(coords,X_BREAK)
        clipped_wall_faces += 1
    if cx >= X_BREAK and zmax > LOW_ROOF_Z:
        coords=[Vector((v.x,v.y,min(v.z,LOW_ROOF_Z))) for v in coords]
        clipped_wall_faces += 1
    base=len(newverts); newverts.extend(tuple(v) for v in coords)
    newfaces.append(tuple(range(base,base+len(coords))))
    face_mats.append(poly.material_index)
newmesh=bpy.data.meshes.new('NSEL | east wing height-trimmed wall panels')
newmesh.from_pydata(newverts,[],newfaces); newmesh.update()
for mat in src.materials: newmesh.materials.append(mat)
for poly,mi in zip(newmesh.polygons,face_mats): poly.material_index=mi
oldmesh=WALL.data; WALL.data=newmesh
if oldmesh.users==0: bpy.data.meshes.remove(oldmesh)

# Rebuild both roof wings as closed slabs clipped from the official GIS polygon.
refs = json.loads((ROOT/'audit'/'official_building_references.json').read_text(encoding='utf-8'))
feat = next(f for f in refs['buildings'] if int(f.get('fid',-1)) == 242)
origin = [-548.283393, -674.397642]
ring = [(float(x)-origin[0], float(y)-origin[1]) for x,y in feat['rings_xy_m'][0]]
def clip_halfplane(poly, xcut, keep_east=True):
    out=[]
    for a,b in zip(poly, poly[1:]+poly[:1]):
        ina=(a[0]>=xcut) if keep_east else (a[0]<=xcut)
        inb=(b[0]>=xcut) if keep_east else (b[0]<=xcut)
        if ina and inb: out.append(b)
        elif ina and not inb:
            t=(xcut-a[0])/(b[0]-a[0]); out.append((xcut,a[1]+t*(b[1]-a[1])))
        elif not ina and inb:
            t=(xcut-a[0])/(b[0]-a[0]); out.append((xcut,a[1]+t*(b[1]-a[1]))); out.append(b)
    # GIS polygon is closed; remove a duplicate closing vertex if produced.
    clean=[]
    for p in out:
        if not clean or (Vector(p)-Vector(clean[-1])).length>1e-5: clean.append(p)
    if len(clean)>2 and (Vector(clean[0])-Vector(clean[-1])).length<1e-5: clean.pop()
    return clean
low_poly=clip_halfplane(ring,X_BREAK,True)
high_poly=clip_halfplane(ring,X_BREAK,False)
if len(low_poly)<3 or len(high_poly)<3: raise RuntimeError('Could not clip GIS footprint for roof wings')
roof_mat=next((m for m in ROOF.data.materials if m),None)
def make_roof_mesh(poly,z_top,name):
    verts=[(x,y,z_top-ROOF_THICK) for x,y in poly]+[(x,y,z_top) for x,y in poly]
    n=len(poly); faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    if roof_mat: mesh.materials.append(roof_mat)
    for p in mesh.polygons: p.material_index=0
    return mesh
oldroof=ROOF.data
ROOF.data=make_roof_mesh(high_poly,HIGH_WALL_TOP,'NSEL | clipped high west roof mesh')
if oldroof.users==0: bpy.data.meshes.remove(oldroof)
lowmesh=make_roof_mesh(low_poly,LOW_ROOF_Z,'NSEL | clipped east wing roof mesh')
low_roof=bpy.data.objects.new('SOIL | evidence-backed lower east roof wing',lowmesh)
COL.objects.link(low_roof)

# Remove third-level facade bays and associated vertical mullions on the lower
# east wing; they would otherwise project above its lidar-supported roof.
removed=[]
for obj in list(FACADE.all_objects):
    if obj.location.x >= X_BREAK and obj.location.z > 5.30:
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)

# Lower east-wing roof equipment while preserving each item's shape and relation
# to the roof. The west equipment cluster remains at the higher roof elevation.
lowered=[]
for obj in list(COL.all_objects):
    if obj.type!='MESH' or obj in (WALL,ROOF,low_roof): continue
    if any(k in obj.name.lower() for k in ('roof fan','roof fan curb')) and obj.location.x >= X_BREAK:
        obj.location.z -= DELTA
        lowered.append(obj.name)

# The original coping is made from simple rectangular mesh segments. Keep
# segments on the high wing, lower segments wholly over the east wing, and split
# the two crossing segments at the new roof-height seam.
copings=[o for o in list(COL.all_objects) if o.type=='MESH' and 'roof parapet coping' in o.name.lower()]
split_records=[]
for obj in copings:
    b=obj_world_bounds(obj); xmin,xmax=b[0]
    if xmax <= X_BREAK:
        continue
    material=next((m for m in obj.data.materials if m),None)
    ymin,ymax=b[1]; zmin,zmax=b[2]
    spans=[]
    if xmin < X_BREAK: spans.append((xmin,X_BREAK,(zmin+zmax)/2))
    if xmax > X_BREAK: spans.append((X_BREAK,xmax,(zmin+zmax)/2-DELTA))
    old_name=obj.name
    bpy.data.objects.remove(obj,do_unlink=True)
    for i,(xa,xb,zc) in enumerate(spans):
        bpy.ops.mesh.primitive_cube_add(size=1, location=((xa+xb)/2,(ymin+ymax)/2,zc))
        box=bpy.context.object
        box.name=old_name+(' | west segment' if xa<X_BREAK else ' | lower east segment')
        box.dimensions=(xb-xa,ymax-ymin,zmax-zmin)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(box.users_collection): c.objects.unlink(box)
        COL.objects.link(box)
        if material: box.data.materials.append(material)
    split_records.append({'name':old_name,'segments':len(spans),'x_bounds':[xmin,xmax]})

# Remove temporary modifiers and refresh scene bounds.
bpy.context.view_layer.update()

# Evidence/geometry diagnostic snapshot retained with the asset.
report={
  'revision':'R1',
  'edit':'Split roof/wall mass into a high west wing and lower east wing from registered DSM/DTM roof-height pattern.',
  'break_local_x_m':X_BREAK,
  'high_wall_top_m':HIGH_WALL_TOP,
  'low_roof_top_m':LOW_ROOF_Z,
  'low_roof_thickness_m':ROOF_THICK,
  'removed_upper_east_facade_objects':removed,
  'lowered_roof_fan_objects':lowered,
  'parapet_adjustments':split_records,
  'wall_vertices':len(WALL.data.vertices),'wall_faces':len(WALL.data.polygons),
  'wall_faces_deleted':deleted_wall_faces,'wall_faces_trimmed_to_roof':clipped_wall_faces,
  'high_roof_vertices':len(ROOF.data.vertices),'high_roof_faces':len(ROOF.data.polygons),
  'low_roof_polygon_vertices':len(low_poly),
  'limitation':'Roof elevations are approximate 2018 DSM minus interpolated bare-earth DTM, using 5-ft cells; local tangent registration is approximate. Parapet details are simplified at the height break. Interior program and room circulation remain schematic.'
}
(AUDIT/'nsel_revision_r1.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

# Render current saved scene via assigned asset camera.
scene=bpy.context.scene
scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(AUDIT/'nsel_revision_r1_exterior.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps(report,indent=2))
