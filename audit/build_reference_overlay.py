"""Run in factory-startup background Blender to create a visual GIS reference."""
import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
r=json.loads((P/'official_building_references.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
c=bpy.data.collections.new('Official_Purdue_Footprints_Reference')
bpy.context.scene.collection.children.link(c)
for b in r['buildings']:
 mesh=bpy.data.meshes.new('GIS_'+str(b['fid']))
 verts=[];edges=[]
 rings=b.get('rings_xy_m',b.get('rings',[]))
 for ring in rings:
  start=len(verts)
  verts.extend([(p[0],p[1],0.15) for p in ring])
  edges.extend([(start+i,start+i+1) for i in range(len(ring)-1)])
  if ring and ring[0]!=ring[-1]:edges.append((len(verts)-1,start))
 if not verts:raise RuntimeError('No reference rings: '+str(b.keys()))
 mesh.from_pydata(verts,edges,[]);mesh.update()
 o=bpy.data.objects.new(b['code']+' | '+b['name']+' | FID '+str(b['fid']),mesh)
 c.objects.link(o);o.show_in_front=True;o.hide_render=True
 o['official_code']=b['code'];o['source_fid']=b['fid'];o['source_url']=r['source']
bpy.context.scene.unit_settings.system='METRIC'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'official_footprints_reference.blend'))
print('REFERENCE_OVERLAY_SAVED',len(c.objects))
