import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; structure=bpy.data.collections['AQUA_Structure']; facade=bpy.data.collections['AQUA_Facade']; rig=bpy.data.collections['Preview_Rig']; wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']; metal=bpy.data.materials['AQUA | charcoal anodized metal']; concrete=bpy.data.materials['AQUA | cast concrete']
# Remove generic roof-edge signage from the inherited builder: it was on the far elevation and appeared as a floating bar through interior views.
for n in ('AQUA | Purdue gold sign fascia','AQUA | Purdue gold sign field'):
 o=bpy.data.objects.get(n)
 if o: bpy.data.objects.remove(o,do_unlink=True)
# Fit the perimeter shell to the retained shallow gable instead of carrying a full-height 12m box above the eaves.
for v in wall.data.vertices:
 p=wall.matrix_world@v.co
 if p.z>8.0:
  p.z=9.2+3.0*(1.0-min(1.0,abs(p.x)/30.0))
  v.co=wall.matrix_world.inverted()@p
wall['r2_roof_alignment']='Perimeter wall top now follows the retained estimated gable profile: 9.2m at eaves to 12.2m ridge. Height is not survey-derived.'
# Roof extends just beyond the GIS perimeter; this 0.3m edge allowance is an explicit model assumption.
for n in ('AQUA | clear-span natatorium | pitched roof planes','AQUA | clear-span natatorium | standing seam roof ribs'):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH': continue
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co; p.x*=30.45/28.89; p.y*=51.55/49.71; p.z=12.2-3.0*min(1.0,abs(p.x)/30.45); v.co=inv@p
 o.data.update()
for n in ('AQUA | clear-span natatorium | gable end infill','AQUA | clear-span natatorium | gable end infill.001'):
 o=bpy.data.objects.get(n)
 if o and o.type=='MESH':
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co; p.x*=30.45/28.89; p.z=12.2-3.0*min(1.0,abs(p.x)/30.45); v.co=inv@p
  o.data.update()
# Put new ridge cap and gutters on the updated roof edges.
ridge=bpy.data.objects.get('AQUA R2 | continuous roof ridge cap')
if ridge: ridge.location.z=12.28
for o in asset.all_objects:
 if o.name.startswith('AQUA R2 | continuous eaves gutter'):
  side=-1 if o.name.endswith('-1') else 1
  for sp in o.data.splines:
   for p in sp.points:
    p.co.x=side*30.35; p.co.z=9.15
# Slender canopy posts to make the entry legible at a distance.
def cube(name,loc,size,mat,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o); o.data.materials.append(mat); return o
for i,x in enumerate((-4.7,4.7)):
 if not bpy.data.objects.get(f'AQUA R2 | north canopy support {i+1}'):
  cube(f'AQUA R2 | north canopy support {i+1}',(x,51.62,1.65),(.16,.16,2.55),metal,facade)
# Reframe exterior composition with full-building margin and 3/4 read; add a direct elevation crop for sign/building identity.
def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects['AQUA R2 | North Three Quarter Camera']; cam.location=(72,156,37); cam.data.lens=35; aim(cam,(0,2,5.3))
# Build a sign close-up camera focused on upper entry for legibility review.
old=bpy.data.objects.get('AQUA R2 | North Sign Camera')
if old: bpy.data.objects.remove(old,do_unlink=True)
d=bpy.data.cameras.new('AQUA R2 | North Sign Camera'); d.lens=55; signcam=bpy.data.objects.new('AQUA R2 | North Sign Camera',d); rig.objects.link(signcam); signcam.location=(0,83,8.3); aim(signcam,(0,51.2,6.1))
# Cutaway renders should not retain exterior fenestration or preview floor as detached floating elements.
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.camera=cam; scene.render.resolution_x=1700; scene.render.resolution_y=1100; scene.render.resolution_percentage=75; scene.render.filepath=str(AUD/'aquatic_r2_north_three_quarter.png'); bpy.ops.render.render(write_still=True)
tog=[]
for o in asset.all_objects:
 name=o.name.lower()
 hide=(o==wall or any(k in name for k in ['pitched roof planes','standing seam roof ribs','gable end infill','schematic clear-span roof truss','exterior concrete clear-span pier','facade bay','vertical glazing mullion','glazing sill','north brick pilaster','north concrete water table','north upper brick belt','north roof eave','ribbon jamb','ribbon head','ribbon sill','purdue gold sign']))
 if hide: tog.append((o,o.hide_render)); o.hide_render=True
for o in rig.objects:
 if o.name=='AQUA R2 | preview ground plane': tog.append((o,o.hide_render)); o.hide_render=True
scene.camera=bpy.data.objects['AQUA R2 | Interior Seating Camera']; scene.render.resolution_x=1300; scene.render.resolution_y=1000; scene.render.resolution_percentage=80; scene.render.filepath=str(AUD/'aquatic_r2_interior_seating_cutaway.png'); bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R1 | Interior Detail Camera']; scene.render.resolution_x=1500; scene.render.resolution_y=950; scene.render.resolution_percentage=75; scene.render.filepath=str(AUD/'aquatic_r2_interior_feature_detail.png'); bpy.ops.render.render(write_still=True)
for o,v in tog: o.hide_render=v
scene.camera=signcam; scene.render.resolution_x=1200; scene.render.resolution_y=700; scene.render.resolution_percentage=100; scene.render.filepath=str(AUD/'aquatic_r2_north_entry_sign_detail.png'); bpy.ops.render.render(write_still=True)
# Save after permanent geometry and camera improvements; temporary cutaway hide flags are restored.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'saved':str(ASSET),'removed_wrong_elevation_signage':True,'shell_roof_gable_adjusted':True,'roof_bounds':{'x':[-30.45,30.45],'y':[-51.55,51.55],'eave_z_m':9.2,'ridge_z_m':12.2},'interior_cutaway_hides_exterior_shell_windows_and_roof':True},indent=2))

