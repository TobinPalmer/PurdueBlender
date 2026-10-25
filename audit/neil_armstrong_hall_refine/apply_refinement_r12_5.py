import bpy, bmesh, hashlib, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'; AUDIT=ROOT/'audit/neil_armstrong_hall_refine'
EXPECTED='fd6a8c7dcbdd21eab4d94ae3a9b38d72d87069260e059996ab689d432927c62e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError('Asset SHA changed; refusing R12.5 edit: '+sha(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_neil_armstrong_hall']; deck=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']; wall=bpy.data.objects['ARMS_West_Wall_North']
if len(col.objects)!=445 or len(deck.data.vertices)!=371 or len(deck.data.polygons)!=357:raise RuntimeError('Unexpected Neil state')
if deck.get('R12_5_restored_low_canopy'):raise RuntimeError('R12.5 low canopy already applied')
if wall.get('R12_5_photo_window_band'):raise RuntimeError('R12.5 facade already applied')
# The R12 roof rewrite replaced the old eight-vertex ground-level lobby awning.
# Restore that measured-from-prior-asset box in the same mesh object, using its
# original local-space coordinates and original soffit material.
old_box=[(-12,-4.75,-.25),(12,-4.75,-.25),(12,4.75,-.25),(-12,4.75,-.25),(-12,-4.75,.25),(12,-4.75,.25),(12,4.75,.25),(-12,4.75,.25)]
box_faces=[(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(3,0,4,7)]
bm=bmesh.new();bm.from_mesh(deck.data);base=len(bm.verts);bv=[bm.verts.new(v) for v in old_box];bm.verts.ensure_lookup_table()
for f in box_faces:
 try:face=bm.faces.new([bv[i] for i in f]);face.material_index=0
 except ValueError:raise RuntimeError('Unexpected duplicate low-canopy face')
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(deck.data);bm.free();deck.data.update()
deck['R12_5_restored_low_canopy']='Restored the original 24 x 9.5 x 0.5 m entrance canopy deck from pre-R12 mesh evidence (prior object geometry); keeps the separate high roof/eaves inference distinct.'
# Direct 2016 photo 02 shows a long upper-storey glazed clerestory band with
# repeated vertical framing on the long brick wing. Add an explicitly inferred
# photo-derived band to the existing wall mesh, not a new asset object.
glass=bpy.data.materials['ARMS_R6_Reflective_Blue_Glass'];steel=bpy.data.materials['ARMS_Mullion_Steel']
if glass.name not in [m.name for m in wall.data.materials]: wall.data.materials.append(glass)
if steel.name not in [m.name for m in wall.data.materials]: wall.data.materials.append(steel)
glass_i=list(wall.data.materials).index(glass); steel_i=list(wall.data.materials).index(steel)
inv=wall.matrix_world.inverted()
# Estimated panel range stays within the wall’s roof and beltcourse bounds;
# its position/cadence is a photographic interpretation, not measured drawing data.
x0,x1=-59.0,-13.0; z0,z1=15.15,18.85; yf=-3.815; ybar=-3.845
bm=bmesh.new();bm.from_mesh(wall.data)
def face_world(points,mi):
 vs=[bm.verts.new(inv@Vector(p)) for p in points]
 f=bm.faces.new(vs);f.material_index=mi
# continuous, dark reflective top-storey glazing
face_world([(x0,yf,z0),(x1,yf,z0),(x1,yf,z1),(x0,yf,z1)],glass_i)
# Regular bays: 2.4 m nominal rhythm inferred from image; thin bars avoid
# claiming exact facade stationing. Ribbons are faces on the common wall mesh.
span=x1-x0; pitch=2.4
for n in range(1,round(span/pitch)):
 x=x0+n*span/round(span/pitch); half=.045
 face_world([(x-half,ybar,z0),(x+half,ybar,z0),(x+half,ybar,z1),(x-half,ybar,z1)],steel_i)
for z in (z0+.04,z1-.04):
 half=.04
 face_world([(x0,ybar,z-half),(x1,ybar,z-half),(x1,ybar,z+half),(x0,ybar,z+half)],steel_i)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(wall.data);bm.free();wall.data.update()
wall['R12_5_photo_window_band']='Added an upper-level reflective window strip and repeated mullions using visual evidence from Wikimedia Commons 2016 photo 02 (CC BY 4.0). Approximate range/cadence is photo-derived inference; no dimensioned elevation or facade registration was found.'
if len(col.objects)!=445 or len(bpy.data.objects)!=445:raise RuntimeError('Object inventory changed')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'sha256':sha(ASSET),'object_count':len(col.objects),'restored_deck_vertices':len(deck.data.vertices),'restored_deck_faces':len(deck.data.polygons),'facade_wall_vertices':len(wall.data.vertices),'facade_wall_faces':len(wall.data.polygons),'wall_materials':[m.name for m in wall.data.materials],'window_band_world_bounds':{'min':[x0,yf,z0],'max':[x1,yf,z1]}},indent=2))

