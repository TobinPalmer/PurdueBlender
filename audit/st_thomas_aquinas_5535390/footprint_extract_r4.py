import bpy, json, math
from pathlib import Path
out={}
for name in ['SOTAC_Stone_Foundation_and_Plinth','SOTAC_Continuous_Brick_Base_Shell','SOTAC_Original_Church_Upper_Walls','SOTAC_New_Church_Addition_Upper_Walls','SOTAC_Office_Classroom_Upper_Walls']:
 ob=bpy.data.objects.get(name)
 if not ob: continue
 mesh=ob.data; world=[ob.matrix_world@v.co for v in mesh.vertices]
 levels={}
 for v in world:
  z=round(float(v.z),2)
  levels.setdefault(str(z),[]).append([round(float(v.x),6),round(float(v.y),6)])
 selected={}
 for z,pts in levels.items():
  if len(pts)>5: selected[z]=pts
 edges_by_level={}
 for edge in mesh.edges:
  a,b=edge.vertices
  if abs(float(world[a].z-world[b].z))<1e-6:
   z=round(float((world[a].z+world[b].z)/2),2)
   edges_by_level.setdefault(str(z),[]).append([[round(float(world[a].x),6),round(float(world[a].y),6)],[round(float(world[b].x),6),round(float(world[b].y),6)]])
 out[name]={'verts':len(mesh.vertices),'faces':len(mesh.polygons),'levels':{k:len(v) for k,v in levels.items()},'selected_levels':selected,'horizontal_edges':{k:v for k,v in edges_by_level.items() if len(v)>5}}
Path(__file__).resolve().parent.joinpath('footprint_extract_r4.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:{'verts':v['verts'],'faces':v['faces'],'levels':v['levels'],'edgecounts':{l:len(q) for l,q in v['horizontal_edges'].items()}} for k,v in out.items()},indent=2))
