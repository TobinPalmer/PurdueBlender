import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; scene=bpy.context.scene
hide=[]
for cn in ('AQUA_Facade','AQUA_Roof','AQUA_Structure'):
 c=bpy.data.collections.get(cn)
 if c: hide.append((c,c.hide_render)); c.hide_render=True
for o in asset.all_objects:
 if o is None: continue
 if 'schematic clear-span roof truss' in o.name or o.name=='AQUA | Purdue pool-hall sign lettering': hide.append((o,o.hide_render)); o.hide_render=True
site=bpy.data.objects.get('AQUA R2 | preview ground plane')
if site: hide.append((site,site.hide_render)); site.hide_render=True
cam=bpy.data.objects.get('AQUA R2 | Interior Seating Camera'); cam.location=(55,-55,38); cam.rotation_euler=(Vector((1,0,3.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=42
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=80; scene.camera=cam; scene.render.filepath=str(AUD/'aquatic_r2_interior_seating_cutaway.png'); bpy.ops.render.render(write_still=True)
for o,v in hide:o.hide_render=v
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest(); p=AUD/'validation_r2.json'; d=json.loads(p.read_text()); d['asset_sha256']=sha; d['interior_render_cutaway']='Facade, roof and exterior structure collections, clear-span trusses, pool-hall lettering and preview ground hidden during interior renders only; visibility restored and saved asset unchanged.'; p.write_text(json.dumps(d,indent=2)+'\n'); (AUD/'asset_sha256_r2.txt').write_text(sha+'  modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend\n'); print('Final R2 render refreshed; asset hash',sha)
