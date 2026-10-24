import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); ASSET=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
# Move only the three upper-story window assemblies on the portico-facing wall.
# Their new centers sit in the six-column bays, as visible in the 2016 front view.
# First-floor vestibule glazing and all side/rear windows stay fixed.
old_to_new={-5.0:-3.495,-0.0:-.255,5.0:2.985}
logs={}
for name in ('HOVD_Window_Sash_Detail','HOVD_R10_Window_Stone_Reveals','HOVD_R10_Window_Muntins'):
 me=bpy.data.objects[name].data
 adj=[set() for _ in me.vertices]
 for poly in me.polygons:
  ids=poly.vertices
  for a,b in zip(ids,tuple(ids[1:])+(ids[0],)):
   adj[a].add(b); adj[b].add(a)
 seen=set(); moved={c:0 for c in old_to_new}
 for start in range(len(adj)):
  if start in seen: continue
  stack=[start]; seen.add(start); ids=[]
  while stack:
   q=stack.pop(); ids.append(q)
   for nxt in adj[q]:
    if nxt not in seen: seen.add(nxt); stack.append(nxt)
  vs=[me.vertices[k].co for k in ids]
  xmin=min(v.x for v in vs); xmax=max(v.x for v in vs)
  ymin=min(v.y for v in vs); ymax=max(v.y for v in vs)
  zmin=min(v.z for v in vs); zmax=max(v.z for v in vs)
  center=(ymin+ymax)*.5; zc=(zmin+zmax)*.5
  if xmin>9.5 and xmax>10.0 and zc>4.0 and zc<15.0:
   key=min(old_to_new,key=lambda c:abs(c-center))
   if abs(center-key)<.20:
    delta=old_to_new[key]-key
    for vi in ids: me.vertices[vi].co.y += delta
    moved[key]+=1
 me.update(); logs[name]=moved
print('front upper windows shifted into portico bays:',logs)
# Guardrails: exactly three upper floors were shifted for each of three window layers.
assert logs['HOVD_Window_Sash_Detail']=={-5.0:11,-0.0:11,5.0:11},logs
assert logs['HOVD_R10_Window_Stone_Reveals']=={-5.0:2,-0.0:2,5.0:2},logs
assert logs['HOVD_R10_Window_Muntins']=={-5.0:6,-0.0:6,5.0:6},logs
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('ROUND12_WINDOWS_SAVED; doors, first-floor entry, side/rear glazing, and root transform unchanged.')

