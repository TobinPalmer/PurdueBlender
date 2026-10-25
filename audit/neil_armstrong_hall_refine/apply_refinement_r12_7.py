import bpy,bmesh,hashlib,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend';AUDIT=ROOT/'audit/neil_armstrong_hall_refine'
EXPECTED='659489bc2962d5118945d0b09060e576bb441318006d0c531019a12b558dbb69'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError('Asset SHA changed; refusing roof reshape')
bpy.ops.wm.open_mainfile(filepath=str(ASSET));obj=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
if len(obj.data.vertices)!=379 or obj.get('R12_7_peak_profile'):raise RuntimeError('Unexpected or already edited canopy')
# Keep the registered orthophoto/eaves XY unchanged. Make only the vertical
# profile more localized and peaked, as a photo-based interpretation of the
# wing form in attributed 2016 views. The 21.5 m apex stays below the 21.6 m
# coarse LiDAR ceiling; neither apex nor profile is a measured height.
inv=obj.matrix_world.inverted();bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
# Generated roof grid remains vertices 8..367 (five segments, 4x9 top/bottom pairs).
# Segment 0 is the long north edge. Create an apex at its midpoint and taper to
# the ends; all other edges remain a lower eave band.
for seg in range(5):
 for j in range(4):
  t=j/3
  for k in range(9):
   s=k/8
   if seg==0:
    zo=17.6+3.9*(1.0-abs(2*s-1.0))
   else:
    zo=17.6
   zi=[17.10,17.35,17.20,16.45,16.75][seg]*(1-s)+[17.35,17.20,16.45,16.75,17.10][seg]*s
   warp=1.25*math.sin(math.pi*t)*math.sin(math.pi*s)
   z=zo*(1-t)+zi*t+warp
   base=8+((seg*4+j)*9+k)*2
   for idx,dz in ((base,0.0),(base+1,-0.30)):
    world=obj.matrix_world@obj.data.vertices[idx].co
    world.z=z+dz
    obj.data.vertices[idx].co=inv@world
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(obj.data);bm.free();obj.data.update()
obj['R12_7_peak_profile']='Photo-based roof silhouette refinement: registered orthophoto/eaves XY unchanged; long north edge now has a localized peaked wing apex (21.5 m) and lower surrounding eaves (17.6 m). Profile is unmeasured visual inference, bounded by 21.6 m coarse 5-ft LiDAR ceiling.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'sha256':sha(ASSET),'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'bounds':{'min':[round(min((obj.matrix_world@v.co)[i] for v in obj.data.vertices),3) for i in range(3)],'max':[round(max((obj.matrix_world@v.co)[i] for v in obj.data.vertices),3) for i in range(3)]},'apex_z':21.5},indent=2))
