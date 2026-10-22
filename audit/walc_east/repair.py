import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); D=R/'audit/walc_east'; M=json.loads((R/'modular/manifest.json').read_text()); ref=json.loads((R/'audit/official_building_references.json').read_text()); out={}
def solid(name,pts,z0,z1,mat,col):
 pts=pts[:-1] if pts[0]==pts[-1] else pts; n=len(pts); verts=[(x,y,z) for z in (z0,z1) for x,y in pts]; faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 v=[Vector((x,y,0)) for x,y in pts]; lookup={tuple(p):i for i,p in enumerate(v)}
 for tri in tessellate_polygon([v]):
  ids=[p if isinstance(p,int) else lookup[tuple(p)] for p in tri];faces += [tuple(reversed(ids)),tuple(i+n for i in ids)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);col.objects.link(o);o.data.materials.append(mat); return o
for id,code,height,fids in [('potter_engineering','POTR',15.5,[864]),('mechanical_engineering','ME',18.5,[857,108]),('electrical_engineering','BHEE',18,[292,109]),('walc','WALC',0,[])]:
 a=next(x for x in M['assets'] if x['id']==id);path=R/'modular'/a['file'];shutil.copy2(path,D/(id+'_before.blend'));bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections[a['collection']]; origin=a['placement_origin_xy_m']; old=list(c.all_objects); changed=[]
 if id=='walc':
  for o in old:
   if o.name.startswith('Campus terrain '): changed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 else:
  masonry=next((o.data.materials[0] for o in old if o.type=='MESH' and ('Core' in o.name or 'Masonry' in o.name) and o.data.materials),None)
  if masonry is None: masonry=bpy.data.materials.new(id+'_brick');masonry.diffuse_color=(.35,.16,.1,1)
  roof=bpy.data.materials.new(id+'_roof');roof.diffuse_color=(.12,.13,.14,1)
  band=bpy.data.materials.new(id+'_limestone');band.diffuse_color=(.65,.59,.47,1)
  for o in old:
   if o.type=='MESH':changed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
  for fid in fids:
   r=next(x for x in ref['buildings'] if x['fid']==fid); pts=[(x-origin[0],y-origin[1]) for x,y in r['rings_xy_m'][0]]
   h=height # Original height estimate retained; source does not measure elevation.
   o=solid(f'{code}_Official_{fid}_Structural_Envelope',pts,0,h,masonry,c);o['source_fid']=fid;o['height_status']='original estimate; unverified';o['horizontal_source']=ref['source']
   solid(f'{code}_Official_{fid}_Roof',pts,h,h+.25,roof,c)
   for z in [1,6,11,height-.3]:solid(f'{code}_Official_{fid}_Limestone_Band_{z}',pts,z,z+.2,band,c)
 c['review_note']='2026-10-22: official horizontal outline; heights/facade estimates unverified' if id!='walc' else 'Removed unrelated campus terrain plates; detailed shape still unverified'
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 # Create a top-down review image using Blender workbench.
 sc=bpy.context.scene;camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);sc.collection.objects.link(cam);cam.location=(0,0,250);cam.rotation_euler=(0,0,0);camdata.type='ORTHO';camdata.ortho_scale=170 if id!='walc' else 150;sc.camera=cam
 sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.filepath=str(D/(id+'_after_top.png'));bpy.ops.render.render(write_still=True)
 out[id]={'replaced_or_removed':changed,'official_features':fids,'placement_unchanged':origin,'height_status':'unverified original estimates','reopened':True}
(D/'changes.json').write_text(json.dumps(out,indent=2))

