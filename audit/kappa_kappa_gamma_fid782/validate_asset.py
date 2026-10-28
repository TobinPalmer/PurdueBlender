import bpy, json, math, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(root,'modular','buildings','massing_house_301840871_5d1bc06.blend')
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.context.scene; ob=bpy.data.objects.get('House_301840871')
assert scene.name=='Building_massing_house_301840871_5d1bc06'
assert ob is not None and ob.type=='MESH'
assert [c.name for c in ob.users_collection]==['Asset_massing_house_301840871_5d1bc06']
assert len(bpy.data.objects)==1
assert len(ob.data.vertices)>8000 and len(ob.data.polygons)>6000
assert all(m is not None for m in ob.data.materials)
assert not any(n.type=='TEX_IMAGE' for m in ob.data.materials for n in m.node_tree.nodes)
bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
bounds={'min':[min(v[i] for v in bb) for i in range(3)],'max':[max(v[i] for v in bb) for i in range(3)]}
# Structural footprint remains the raw GIS ring; decorative window trim expands the envelope slightly.
assert abs(bounds['min'][0]-(-404.1764))<.1 and abs(bounds['max'][0]-(-379.3628))<.1
assert abs(bounds['min'][1]-43.3287)<.1 and abs(bounds['max'][1]-83.2742)<.1
result={'fresh_open':'passed','blender_version':bpy.app.version_string,'asset_path':'modular/buildings/massing_house_301840871_5d1bc06.blend','scene':scene.name,'object':ob.name,'object_count':len(bpy.data.objects),'collection':ob.users_collection[0].name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'materials':[m.name for m in ob.data.materials],'world_bounds':bounds,'external_texture_dependencies':0,'notes':'Fresh-open check after wall-shell correction. One mesh and exported collection preserved. XY envelope includes trim/window details; structural perimeter derived from FID 782 ring. Roof-height caps are removed from the wall shell so only the separately modeled mansard wings cover its open top.'}
out=os.path.join(os.path.dirname(__file__),'fresh_open_validation.json')
with open(out,'w',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
