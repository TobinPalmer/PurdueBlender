"""Stanley Coulter Hall R5: source-guided facade cleanup and option isolation."""
import bpy, hashlib, json, math, re
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
asset=bpy.data.collections['Asset_stanley_coulter_hall']
scene=bpy.context.scene

def world_bounds(obj):
 pts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

def transform_mesh_world(obj, transform):
 if obj.type!='MESH': return
 if obj.data.users>1: obj.data=obj.data.copy()
 inv=obj.matrix_world.inverted()
 for v in obj.data.vertices:
  p=obj.matrix_world@v.co
  transform(p)
  v.co=inv@p
 obj.data.update()

def active_bounds(collection, render_only=False):
 objs=[]
 for obj in collection.all_objects:
  if obj.type!='MESH': continue
  if render_only and (obj.hide_render or obj.hide_get() or obj.hide_viewport): continue
  objs.append(obj)
 pts=[]
 for obj in objs:
  pts.extend(obj.matrix_world@Vector(c) for c in obj.bound_box)
 return {'mesh_object_count':len(objs),'bounds_local_m':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]} if pts else {'mesh_object_count':0,'bounds_local_m':None}

# Isolate 47 hidden high roof/dormer/chimney/HVAC study meshes, plus four unsupported copper ridges and one secondary-entry pediment.
# These remain recoverable for review but are no longer members of the exported asset collection.
archive=bpy.data.collections.get('SC_Unverified_Architectural_Options_R5')
if archive is None:
 archive=bpy.data.collections.new('SC_Unverified_Architectural_Options_R5')
 scene.collection.children.link(archive)
archive.hide_render=True
archive.hide_viewport=True
archive['purpose']='Unverified alternative roof/entry option meshes retained for audit only; excluded from Asset_stanley_coulter_hall exports and active bounds.'
archive['source_limit']='No current roof plan/elevation or source imagery validates the archived dormers, chimneys, HVAC arrangement, copper ridges, or west-entry pediment.'
high_options=[]
for obj in list(asset.all_objects):
 if obj.type!='MESH': continue
 zmax=world_bounds(obj)[1][2]
 if zmax>15.9 and (obj.name.startswith(('SC_Dormer_','SC_Chimney_','SC_HVAC_'))):
  high_options.append(obj)
if len(high_options)!=47:
 raise RuntimeError(f'Expected 47 high roof option meshes; found {len(high_options)}')
additional_names=['SC_Copper_Ridge_Main','SC_Copper_Ridge_North','SC_Copper_Ridge_SPav_W','SC_Copper_Ridge_SPav_E','SC_West_Entrance_Pediment']
additional=[]
for name in additional_names:
 obj=bpy.data.objects.get(name)
 if obj and obj.name in asset.all_objects:
  additional.append(obj)
option_objects=high_options+additional
archived=[]
for obj in option_objects:
 if obj not in archive.objects.values():
  for col in list(bpy.data.collections):
   if col!=archive and obj.name in col.objects:
    col.objects.unlink(obj)
  archive.objects.link(obj)
 obj.hide_render=True
 obj.hide_viewport=True
 obj.hide_set(True)
 obj['R5_status']='Unverified alternative, retained outside exported building collection for audit/recovery.'
 archived.append(obj.name)

# Reduce the east entrance projection and cap width while retaining the photo-supported stone frame,
# semicircular transom, two slender round columns, inset doors, landing, stair and rail geometry.
entry_changes={}
for name,factor in [('SC_Portico_Rectangular_Stone_Portal_Surround',0.90),('SC_Portico_Entablature',0.90),('SC_Portico_Flat_Stone_Canopy',0.85)]:
 obj=bpy.data.objects.get(name)
 if obj:
  entry_changes[name+'_before']=world_bounds(obj)
  center_y=-4.0
  if name=='SC_Portico_Flat_Stone_Canopy':
   x0=world_bounds(obj)[0][0]
   target_xmax=28.97
   old_xmax=world_bounds(obj)[1][0]
   x_factor=(target_xmax-x0)/(old_xmax-x0)
  elif name=='SC_Portico_Entablature':
   x0=world_bounds(obj)[0][0]
   target_xmax=28.97
   old_xmax=world_bounds(obj)[1][0]
   x_factor=(target_xmax-x0)/(old_xmax-x0)
  else:
   x_factor=1.0
  def f(p, factor=factor, center_y=center_y, x0=x0 if name!='SC_Portico_Rectangular_Stone_Portal_Surround' else 0, x_factor=x_factor):
   p.y=center_y+(p.y-center_y)*factor
   if x_factor!=1.0:p.x=x0+(p.x-x0)*x_factor
  transform_mesh_world(obj,f)
  entry_changes[name+'_after']=world_bounds(obj)
  obj['R5_entry_note']='Reduced projection/width to read as a restrained stone doorway surround rather than a broad canopy; dimensions estimated from current CLA photograph.'
# Pull the two round supports back to the shallow cap. Their separation and round form remain aligned with the doorway.
for obj in list(bpy.data.objects):
 if obj.name.startswith('SC_Portico_Column_') and any(token in obj.name for token in ('_0','_3')) and obj.type=='MESH':
  entry_changes[obj.name+'_before']=world_bounds(obj)
  transform_mesh_world(obj,lambda p:setattr(p,'x',p.x-0.35))
  entry_changes[obj.name+'_after']=world_bounds(obj)
  obj['R5_entry_note']='Two photo-supported slender round supports; pulled back under the reduced shallow entrance header.'
# Keep the inscription centered over the narrower header.
inscription=bpy.data.objects.get('SC_Portico_3D_Text')
if inscription:
 entry_changes['SC_Portico_3D_Text_before']=world_bounds(inscription)
 mw=inscription.matrix_world.copy();mw.translation.x-=0.35;inscription.matrix_world=mw
 entry_changes['SC_Portico_3D_Text_after']=world_bounds(inscription)
# The current CLA photo shows paired/grouped east windows and a distinct wider upper glazed band.
# Preserve each opening center (and wall aperture); enlarge component meshes into paired modules instead of moving openings.
width_factors={'Level1_FirstFloor':2.50/1.82,'Level2_SecondFloor':2.70/1.95,'Level3_ThirdFloor':2.90/2.02}
window_regex=re.compile(r'^SC_Win_East_(Level1_FirstFloor|Level2_SecondFloor|Level3_ThirdFloor)_(\d+)_')
window_edits=[]
for obj in list(asset.all_objects):
 if obj.type!='MESH': continue
 match=window_regex.match(obj.name)
 if not match: continue
 row,index=match.group(1),int(match.group(2))
 factor=width_factors[row]
 pts=[obj.matrix_world@v.co for v in obj.data.vertices]
 center_y=sum(p.y for p in pts)/max(1,len(pts))
 if not pts: continue
 transform_mesh_world(obj,lambda p,cy=center_y,f=factor:setattr(p,'y',cy+(p.y-cy)*f))
 window_edits.append({'object':obj.name,'row':row,'index':index,'width_factor':round(factor,4),'center_preserved':True})
# Tone down the pair of entrance lanterns to warm low-output wall fixtures, not white emissive blocks.
lantern=bpy.data.materials.get('Lantern_Warm_Glow')
if lantern and lantern.use_nodes:
 bs=next((n for n in lantern.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bs:
  bs.inputs['Base Color'].default_value=(0.34,0.19,0.08,1)
  bs.inputs['Roughness'].default_value=0.48
  if 'Emission Color' in bs.inputs:bs.inputs['Emission Color'].default_value=(0.70,0.38,0.13,1)
  if 'Emission Strength' in bs.inputs:bs.inputs['Emission Strength'].default_value=0.22
 lantern.diffuse_color=(0.34,0.19,0.08,1)
# Source-backed color/roughness variation on the primary low hipped roof. The archived historic image
# is warm brown; present-day roof color/construction remain unverified. No physical seams or dormers added.
roofmat=bpy.data.materials.get('Historic_Slate_Roof_Procedural')
roof_material_note='Subtle warm, weathered brown variation follows undated PPBUC01117 image only; current roof material, form and total height remain unverified.'
if roofmat and roofmat.use_nodes:
 mix=roofmat.node_tree.nodes.get('Mix')
 if mix and len(mix.inputs)>7:
  mix.inputs[6].default_value=(0.34,0.18,0.095,1)
  mix.inputs[7].default_value=(0.17,0.085,0.045,1)
  mix.inputs[0].default_value=0.55
 noise=roofmat.node_tree.nodes.get('Noise Texture')
 if noise:noise.inputs['Scale'].default_value=2.2;noise.inputs['Detail'].default_value=2.5
 bump=roofmat.node_tree.nodes.get('Bump')
 if bump:bump.inputs['Strength'].default_value=0.10;bump.inputs['Distance'].default_value=0.003
 bs=next((n for n in roofmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bs:bs.inputs['Roughness'].default_value=0.84
 roofmat.diffuse_color=(0.25,0.125,0.06,1)
roof=bpy.data.objects.get('SC_Historic_Slate_Roof')
if roof:roof['R5_material_note']=roof_material_note
cornice=bpy.data.objects.get('SC_Classical_Entablature_Cornice')
if cornice:cornice['R5_fascia_note']='0.45 m modeled pale limestone eave; thin, differentiated band retained as an estimate, not a measured profile.'
if list(root.location)!=[0.0,0.0,0.0] or any(abs(v-1.0)>1e-6 for v in root.scale):raise RuntimeError('asset root changed')

# Record bounds of both the exported collection and render-visible meshes before saving.
active_all=active_bounds(asset,False)
active_visible=active_bounds(asset,True)
archive_all=active_bounds(archive,False)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
digest=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'round':5,'asset':str(ASSET),'sha256':digest,'asset_collection':'Asset_stanley_coulter_hall','active_collection_object_count':len(asset.all_objects),'archive_collection':archive.name,'archived_mesh_count':len(archived),'archived_high_option_count':len(high_options),'archived_additional_unverified_count':len(additional),'archived_option_names':archived,'active_all_geometry_bounds_local_m':active_all,'active_render_visible_mesh_bounds_local_m':active_visible,'archive_mesh_bounds_local_m':archive_all,'entry_before_after_bounds_m':entry_changes,'east_window_meshes_reproportioned':len(window_edits),'east_window_rows':width_factors,'entrance_lantern_material':'warm amber base/emission, emission strength 0.22','roof_material_note':roof_material_note,'root_transform':{'location':list(root.location),'rotation_euler':list(root.rotation_euler),'scale':list(root.scale)},'uncertainties':['Roof form/material/height are not current-as-built verified; warm color variation is based only on undated PPBUC01117.','Window widths are qualitative from the current CLA photo; opening centers and GIS footprint remain unchanged.','Interior location/layout remains schematic from 2022 plans and broad stated uses, not a current as-built plan.']}
(AUDIT/'build_r5.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
