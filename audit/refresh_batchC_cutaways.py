"""Refresh render-only cutaway previews for the six repaired batch-C libraries."""
import bpy, json, math, os, sys, datetime
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
KEY=sys.argv[-1]
SLUGS={
 'boilermaker_aquatic':'morgan_j_burke_boilermaker_aquatic_center',
 'lambert':'lambert_fieldhouse',
 'life_science_plant_soils':'life_science_plant_and_soils_laboratory',
 'morgan_center':'burton_morgan_center',
 'national_soil_erosion':'national_soil_erosion_laboratory',
 'nacc':'native_american_educational_and_cultural_center',
}
slug=SLUGS[KEY]
blend=os.path.join(ROOT,'modular','buildings',slug+'.blend')
bpy.ops.wm.open_mainfile(filepath=blend)
asset=bpy.data.collections.get('Asset_'+slug)
groups={c.name.split('_')[-1]:c for c in asset.children}
for group in ('Structure','Facade','Roof'):
 c=next((x for x in asset.children if x.name.endswith('_'+group)),None)
 if c:
  for ob in c.objects: ob.hide_render=True
interior=next((x for x in asset.children if x.name.endswith('_Interior')),None)
if interior:
 for ob in interior.objects:
  if 'interior floor plate' in ob.name.lower() or 'interior arena floor' in ob.name.lower(): ob.hide_render=True
with open(os.path.join(ROOT,'audit','batchC_'+KEY+'_evidence.json'),encoding='utf-8') as f: evidence=json.load(f)
w,d=evidence['footprint']['dimensions_m']; h=evidence['vertical_geometry']['main_wall_height_m']; extent=max(w,d,h,12)
cam_loc=(extent*.58,-extent*.75,extent*1.05)
bpy.ops.object.camera_add(location=cam_loc)
cam=bpy.context.object; cam.name='Preview only | elevated interior cutaway'; cam.data.type='ORTHO'; cam.data.ortho_scale=extent*1.05
from mathutils import Vector
cam.rotation_euler=(Vector((0,0,.25))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.cycles.samples=10; scene.render.resolution_x=720; scene.render.resolution_y=480; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(ROOT,'audit','batchC_'+KEY+'_interior_preview.png')
bpy.ops.render.render(write_still=True)
evidence['validation']['interior_detail_preview']='audit/batchC_'+KEY+'_interior_preview.png'
evidence['validation']['interior_preview_type']='render-only elevated cutaway with shell/facade/roof hidden; it does not alter the saved asset'
evidence['validation']['interior_preview_rendered_at_local']=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
with open(os.path.join(ROOT,'audit','batchC_'+KEY+'_evidence.json'),'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)
print(json.dumps({'key':KEY,'interior_preview':scene.render.filepath,'timestamp':evidence['validation']['interior_preview_rendered_at_local']}))
