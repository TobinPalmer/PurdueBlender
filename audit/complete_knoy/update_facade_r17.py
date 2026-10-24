import bpy
from pathlib import Path
ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
SRC = ROOT / 'audit/complete_knoy/knoy_hall_before_r17.blend'
OUT = ROOT / 'audit/complete_knoy/knoy_hall_r17_candidate.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
old_bands = [(1.10,3.10),(5.58,7.58),(10.06,12.06),(14.54,16.54)]
new_bands = [(1.40,2.80),(5.88,7.28),(10.36,11.76),(14.84,16.24)]
records = {}
for name in ('KNOY_Fenestration_Ribbon_Glass','KNOY_Fenestration_Bronze_Mullions'):
    obj = bpy.data.objects[name]
    inv = obj.matrix_world.inverted()
    changed = 0
    untouched_top = 0
    for vert in obj.data.vertices:
        world = obj.matrix_world @ vert.co
        for (old_lo,old_hi),(new_lo,new_hi) in zip(old_bands,new_bands):
            if abs(world.z-old_lo) < 1e-5:
                world.z = new_lo
                vert.co = inv @ world
                changed += 1
                break
            if abs(world.z-old_hi) < 1e-5:
                world.z = new_hi
                vert.co = inv @ world
                changed += 1
                break
        else:
            if abs(world.z-18.0)<1e-5 or abs(world.z-19.1)<1e-5:
                untouched_top += 1
    obj.data.update()
    records[name] = {'changed_vertices':changed,'unchanged_L5_band_vertices':untouched_top}
    if changed == 0:
        raise RuntimeError(f'No expected facade geometry changed for {name}')
root = bpy.data.objects.get('KNOY_Exterior_Masonry_Walls')
if root:
    root['r17_facade_revision'] = 'Reduced L1-L4 glazing ribbon height from 2.00 m to estimated 1.40 m, keeping each existing band center fixed, based on an uncalibrated Purdue Archives Knoy photo showing narrow ribbon windows within deeper brick bands.'
    root['r17_facade_uncertainty'] = 'Qualitative proportion only; photo perspective and unknown camera/scale prevent as-built measurements. L5/top band preserved and unresolved.'
# Add solid masonry infill at the 0.30 m strips exposed by the narrower ribbon windows.
# The official archival photo supports brick bands surrounding the narrow ribbons;
# the precise proportions remain explicitly qualitative.
from mathutils import Vector
poly = [
(195.927,14.735),(202.924,14.861),(202.880,29.748),(201.527,29.650),
(201.384,46.841),(196.379,46.832),(196.316,50.768),(197.230,50.787),
(202.657,57.644),(202.591,68.949),(206.373,72.828),(203.752,75.375),
(206.047,77.529),(208.571,75.131),(223.620,90.701),(230.431,84.025),
(225.589,78.761),(232.267,72.817),(229.788,70.140),(236.558,64.353),
(233.994,61.640),(240.852,55.567),(228.371,42.936),(228.487,29.494),
(234.999,23.976),(235.317,-1.878),(202.973,-2.461),(202.935,10.835),
(195.989,10.708)]
boundary=[Vector(p) for p in poly]
area=sum(boundary[i].x*boundary[(i+1)%len(boundary)].y-boundary[(i+1)%len(boundary)].x*boundary[i].y for i in range(len(boundary)))/2
ccw=area>0
inner=[]
for i,cur in enumerate(boundary):
    prev=boundary[(i-1)%len(boundary)]; nxt=boundary[(i+1)%len(boundary)]
    d0=(cur-prev).normalized(); d1=(nxt-cur).normalized()
    n0=Vector((-d0.y,d0.x)) if ccw else Vector((d0.y,-d0.x))
    n1=Vector((-d1.y,d1.x)) if ccw else Vector((d1.y,-d1.x))
    bis=(n0+n1).normalized(); dot=bis.dot(n1)
    scale=0.40 if abs(dot)<0.1 else 0.40/dot
    scale=min(max(scale,0.20),1.00)
    inner.append(cur+bis*scale)
solid={4,5,6,9,10,11,12,14,28}
old_bands=[(1.10,3.10),(5.58,7.58),(10.06,12.06),(14.54,16.54)]
new_bands=[(1.40,2.80),(5.88,7.28),(10.36,11.76),(14.84,16.24)]
verts=[]; faces=[]
for i in range(len(boundary)):
    if i in solid: continue
    p0,p1=boundary[i],boundary[(i+1)%len(boundary)]
    q0,q1=inner[i],inner[(i+1)%len(inner)]
    for (lo,hi),(nlo,nhi) in zip(old_bands,new_bands):
        for z0,z1 in ((lo,nlo),(nhi,hi)):
            b=len(verts)
            verts.extend([(p0.x,p0.y,z0),(p1.x,p1.y,z0),(p1.x,p1.y,z1),(p0.x,p0.y,z1),
                          (q0.x,q0.y,z0),(q1.x,q1.y,z0),(q1.x,q1.y,z1),(q0.x,q0.y,z1)])
            faces.extend([(b,b+1,b+2,b+3),(b+7,b+6,b+5,b+4),(b,b+4,b+5,b+1),
                          (b+1,b+5,b+6,b+2),(b+2,b+6,b+7,b+3),(b+3,b+7,b+4,b)])
mesh=bpy.data.meshes.new('KNOY_Facade_Brick_Spandrels_R17')
mesh.from_pydata(verts,[],faces)
mat=bpy.data.materials['KNOY_Purdue_Red_Brick']; mesh.materials.append(mat)
obj=bpy.data.objects.new('KNOY_Facade_Brick_Spandrels_R17',mesh)
obj.active_material=mat
asset=bpy.data.collections['Asset_knoy_hall']; asset.objects.link(obj)
wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls']
obj.parent=wall.parent; obj.matrix_parent_inverse=wall.matrix_parent_inverse.copy()
obj['r17_source_basis']='Purdue Archives public building-record photo shows narrow glazing ribbons with brick spandrels above/below on visible faces.'
obj['r17_uncertainty']='Photographic proportion only, uncalibrated. The 0.30 m infill widths correspond to the revised 1.40 m modeled glass bands within inherited 2.00 m opening envelopes; these are not measured as-built dimensions.'
notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if notes:
    body = notes.as_string()
    body += "\n\nROUND 17 — PHOTO-LED RIBBON-GLAZING PROPORTION\n------------------------------------------------------------\nPurdue Archives and Special Collections' Historic Facilities and Buildings Database provides a public Knoy Hall photograph (record: https://collections.lib.purdue.edu/campus/buildings/75; image: https://collections.lib.purdue.edu/campus/images/buildings/75-maurice-g-knoy-hall-of-technology.jpeg; image capture date not stated). Several visible exterior faces show narrow horizontal window ribbons within substantially deeper masonry bands. The previous L1-L4 glazing bands were 2.00 m high. They are now 1.40 m high, centered at the same elevations; L5/top band is unchanged because its status remains unresolved. This is a qualitative, uncalibrated photo proportion, not a measured facade elevation. The photograph supports ribbon-versus-masonry proportion only and does not resolve exact window cadence, dimensions, orientation or material assignment. See audit/complete_knoy/evidence_round17.json.\n"
    notes.clear()
    notes.write(body)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('R17_GEOMETRY',records)
print('R17_SAVED',OUT)
print('R17_EMBEDDED_NOTES', 'narrow horizontal dark-tinted glazing ribbons' in notes.as_string() if notes else 'NOT_FOUND')





