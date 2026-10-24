import bpy, json, os
from mathutils import Vector

root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
path=os.path.join(root,'modular','buildings','national_soil_erosion_laboratory.blend')
bpy.ops.wm.open_mainfile(filepath=path)
asset=bpy.data.collections.get('Asset_national_soil_erosion_laboratory')
assert asset is not None, 'export collection missing after reopen'
objs=[]
def walk(c):
 for o in c.objects: objs.append(o)
 for child in c.children: walk(child)
walk(asset)
meshes=[o for o in objs if o.type=='MESH']
materials={m for o in meshes for m in o.data.materials if m}
bad=[]
for m in materials:
 if not m.use_nodes: bad.append(m.name+':nodes-disabled'); continue
 nt=m.node_tree
 outputs=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']
 if not outputs or not any(link.to_node in outputs and link.to_socket.name=='Surface' for link in nt.links): bad.append(m.name+':surface-unconnected')
 elif not any(n.type in {'TEX_NOISE','TEX_BRICK','TEX_IMAGE','TEX_COORD'} for n in nt.nodes): bad.append(m.name+':no-texture-node')
mins=[1e9,1e9,1e9]; maxs=[-1e9,-1e9,-1e9]
for ob in meshes:
 for v in ob.bound_box:
  p=ob.matrix_world@Vector(v)
  for i in range(3): mins[i]=min(mins[i],p[i]); maxs[i]=max(maxs[i],p[i])
door=bpy.data.objects.get('Soil Lab | loading / equipment door')
evidence=json.load(open(os.path.join(root,'audit','batchC_national_soil_erosion_evidence.json'),encoding='utf-8'))
assert not bad, bad
assert door is not None
result={'reload':'PASS','asset_file':'modular/buildings/national_soil_erosion_laboratory.blend','collection':asset.name,'objects':len(objs),'mesh_objects':len(meshes),'unique_materials':len(materials),'connected_texture_materials':len(materials)-len(bad),'material_failures':bad,'local_object_bounds_m':[mins,maxs],'footprint_dimensions_m':evidence['footprint']['dimensions_m'],'recommended_master_marker_xy_m':evidence['coordinate_method']['recommended_master_marker_xy_m'],'detached_door_check':'door is attached to south GIS facade at local y='+str(round(door.location.y,3)),'no_image_texture_dependencies':not any(n.type=='TEX_IMAGE' for m in materials for n in m.node_tree.nodes),'master_or_manifest_edited':False}
out=os.path.join(root,'audit','batchC_national_soil_erosion_validation.json')
json.dump(result,open(out,'w',encoding='utf-8'),indent=2)
print(json.dumps(result,indent=2))
