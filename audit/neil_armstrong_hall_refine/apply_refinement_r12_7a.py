import bpy,hashlib,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
EXPECTED='20a81273253491342a800f484f0c550534fb8dff13298737605c015ad0691908'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError('Neil SHA changed; refusing R12.7 profile update')
bpy.ops.wm.open_mainfile(filepath=str(ASSET));obj=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
inv=obj.matrix_world.inverted()
# Regenerate only the Z profile for top/soffit vertices. Orthophoto XY remains fixed.
# The first eight vertices are the legacy deck; the following 360 are the 5x4x9x2 ring.
inner=[17.10,17.35,17.20,16.45,16.75]
inner_next=[17.35,17.20,16.45,16.75,17.10]
for seg in range(5):
 for j in range(4):
  t=j/3
  for k in range(9):
   s=k/8
   zo=17.6+3.9*(1.0-abs(2*s-1.0)) if seg==0 else 17.6
   zi=inner[seg]*(1-s)+inner_next[seg]*s
   warp=1.25*math.sin(math.pi*t)*math.sin(math.pi*s)
   z=zo*(1-t)+zi*t+warp
   base=8+((seg*4+j)*9+k)*2
   for idx,dz in ((base,0.0),(base+1,-0.30)):
    w=obj.matrix_world@obj.data.vertices[idx].co;w.z=z+dz;obj.data.vertices[idx].co=inv@w
obj.data.update()
obj['R12_7_peak_profile']='R12.7a applied photo-based roof profile: registered orthophoto/eaves XY unchanged; the long northern eave is a localized peaked wing (21.5 m at mid-edge) tapering to lower ends (17.6 m). Inferred visual profile only; the 21.6 m NDHM ceiling is coarse, not a verified roof height.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'sha256':sha(ASSET),'bounds':{'min':[round(min((obj.matrix_world@v.co)[i] for v in obj.data.vertices),3) for i in range(3)],'max':[round(max((obj.matrix_world@v.co)[i] for v in obj.data.vertices),3) for i in range(3)]},'vertex8':[round(x,3) for x in obj.matrix_world@obj.data.vertices[8].co], 'vertex44':[round(x,3) for x in obj.matrix_world@obj.data.vertices[44].co], 'vertex80':[round(x,3) for x in obj.matrix_world@obj.data.vertices[80].co]},indent=2))
