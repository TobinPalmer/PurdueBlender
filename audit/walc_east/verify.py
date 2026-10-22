import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/walc_east';m=json.loads((R/'modular/manifest.json').read_text());ref=json.loads((R/'audit/official_building_references.json').read_text());report={}
for id in ['walc','potter_engineering','mechanical_engineering','electrical_engineering','knoy_hall']:
 a=next(x for x in m['assets'] if x['id']==id);bpy.ops.wm.open_mainfile(filepath=str(R/'modular'/a['file']));c=bpy.data.collections[a['collection']];bpy.context.view_layer.update();ox,oy=a['placement_origin_xy_m'];rows=[]
 for o in c.all_objects:
  if o.type=='MESH' and ('Structural_Envelope' in o.name or o.name=='WALC_Official_906_Roof'):
   r=next(x for x in ref['buildings'] if x['fid']==o['source_fid']);source=r['rings_xy_m'][0];p=[o.matrix_world@v.co for v in o.data.vertices];err=max(min(((q.x+ox-x)**2+(q.y+oy-y)**2)**.5 for x,y in source) for q in p);rows.append({'fid':r['fid'],'max_vertex_to_source_m':err})
 report[id]={'structural_outline_checks':rows,'objects':len(c.all_objects),'export_collection':c.name,'unrelated_terrain_remaining':sum(o.name.startswith('Campus terrain ') for o in c.all_objects)}
 ps=[o.matrix_world@Vector(v) for o in c.all_objects if o.type=='MESH' for v in o.bound_box];xs=[p.x for p in ps];ys=[p.y for p in ps];sc=bpy.context.scene;cd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',cd);sc.collection.objects.link(cam);cam.location=((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,250);cd.type='ORTHO';cd.ortho_scale=max(max(xs)-min(xs),max(ys)-min(ys))*1.2;sc.camera=cam;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='MATERIAL';sc.display.shading.background_type='WORLD';sc.world=sc.world or bpy.data.worlds.new('ReviewWorld');sc.world.color=(.5,.5,.5);sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.filepath=str(D/(id+'_after_top.png'));bpy.ops.render.render(write_still=True)
(D/'verification.json').write_text(json.dumps(report,indent=2))


