import bpy, os, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def trace(x,z,y0,direction):
 origin=Vector((x,y0,z));d=Vector(direction);hits=[]
 for _ in range(6):
  hit,loc,n,fi,obj,mat=s.ray_cast(dg,origin,d,distance=60)
  if not hit:break
  hits.append({'object':obj.name,'point':[round(v,3) for v in loc]});origin=loc+d*.025
 return hits
rays=[]
for x,z in [(-9.804,2.35),(-5.994,7.836),(-9.804,12.927),(-5.994,18.017)]:
 rays.append({'facade':'south','x':x,'z':z,'hits':trace(x,z,-30,(0,1,0))})
for x,z in [(20.43,2.4),(20.43,7.89),(20.43,13.38),(23,2.4),(23,7.89),(23,13.38),(27.3,2.4),(27.3,7.89),(27.3,13.38)]:
 rays.append({'facade':'north','x':x,'z':z,'hits':trace(x,z,30,(0,-1,0))})
collection=bpy.data.collections['Asset_rawls_hall'];root=bpy.data.objects['AssetRoot_rawls_hall'];wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
report={'asset':bpy.data.filepath,'blender_version':bpy.app.version_string,'objects':len(collection.all_objects),'mesh_objects':sum(o.type=='MESH' for o in collection.all_objects),'missing_images':missing,'root_parent':root.parent.name if root.parent else None,'root_location':list(root.location),'root_scale':list(root.scale),'wall_faces':len(wall.data.polygons),'north_glass_quads':len(bpy.data.objects['RAWL_North_Windows_Glass'].data.polygons),'north_frame_faces':len(bpy.data.objects['RAWL_North_Windows_BronzeMullions'].data.polygons),'south_glass_quads':len(bpy.data.objects['RAWL_South_Windows_South_Glass'].data.polygons),'south_frame_faces':len(bpy.data.objects['RAWL_South_Windows_South_BronzeMullions'].data.polygons),'glass_transmission':next(n for n in bpy.data.materials['RAWL_CurtainWall_Glass'].node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Transmission Weight'].default_value,'rays':rays}
with open('audit/batch4_rawls/round5_checks.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
