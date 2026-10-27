"""Fresh-open renders and structural checks for Alpha Sigma Phi."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_house_301841603_654031c.blend'
OUT=ROOT/'audit/alpha_sigma_phi/previews'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes['Building_massing_house_301841603_654031c']
bpy.context.window.scene=scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=32
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.camera.data.lens=50
scene.render.filepath=str(OUT/'alpha_sigma_phi_exterior.png')
bpy.ops.render.render(write_still=True,scene=scene.name)

# Produce an evidence-only cutaway by hiding only this asset's exterior/roof.
root=bpy.data.collections['Asset_massing_house_301841603_654031c']
for nm in ('Exterior_Alpha_Sigma_Phi','Roof_Alpha_Sigma_Phi'):
    c=bpy.data.collections.get(nm)
    if c: c.hide_render=True
cam=scene.camera
# Ground-floor plan view: upper floor plates and fittings are hidden only in
# this review render, to make the schematic commons visible.
for o in root.all_objects:
    if o is None: continue
    if o.name.startswith(('Interior_Floor_2','Interior_Floor_3')):
        o.hide_render=True
    if o.name.startswith('Level_') or o.name in ('Stair_Core_2','Stair_Core_3'):
        o.hide_render=True
cam.location=(-1019.0,852.0,75.0)
target=Vector((-1019.0,852.0,0.6))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
# An orthographic plan view keeps the whole L-shaped GIS footprint in frame
# without perspective convergence. For this evidence-only render, remove the
# review sun so schematic furniture is readable without long cast shadows.
cam.data.type='ORTHO'
cam.data.ortho_scale=58.0
for ob in scene.objects:
    if ob.type=='LIGHT': ob.hide_render=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.72,0.76,0.82,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.8
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
# Use a high-contrast review palette only in this temporary render session;
# the source asset materials remain untouched. This separates the illustrative
# furniture from the floor in a flat, shadow-free plan view.
review_colors={
    'Alpha Sigma Phi | interior floor':(0.82,0.79,0.70,1),
    'Alpha Sigma Phi | interior wood':(0.52,0.24,0.075,1),
    'Alpha Sigma Phi | warm gray architectural concrete':(0.62,0.67,0.70,1),
    'Alpha Sigma Phi | charcoal metal':(0.055,0.13,0.20,1),
    'Alpha Sigma Phi | social-room carpet (historic evidence, period unknown)':(0.46,0.16,0.12,1),
    'Alpha Sigma Phi | trophy-case glass (schematic)':(0.12,0.38,0.46,1),
    'Alpha Sigma Phi | trophy display brass (schematic)':(0.78,0.54,0.16,1),
}
for mat_name, color in review_colors.items():
    mat=bpy.data.materials.get(mat_name)
    if mat and mat.use_nodes:
        bsdf=mat.node_tree.nodes.get('Principled BSDF')
        if bsdf: bsdf.inputs['Base Color'].default_value=color
# Render-only annotations clarify that these spaces are illustrative. Derive
# their positions and orientation from the official GIS ring and the longest
# footprint edge; they are never saved into the reusable building asset.
source_ring=json.loads((ROOT/'audit/alpha_sigma_phi/sources/arcgis_fid763_feature.json').read_text(encoding='utf-8'))['features'][0]['geometry']['rings'][0][:-1]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in source_ring]
cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
edge=max(range(len(ring)),key=lambda i:math.dist(ring[i],ring[(i+1)%len(ring)]))
dx=ring[(edge+1)%len(ring)][0]-ring[edge][0]; dy=ring[(edge+1)%len(ring)][1]-ring[edge][1]
angle=math.atan2(dy,dx); ux,uy=math.cos(angle),math.sin(angle); vx,vy=-uy,ux
def review_xy(du,dv): return (cx+ux*du+vx*dv,cy+uy*du+vy*dv)
labelmat=bpy.data.materials.new('Review annotation | navy'); labelmat.diffuse_color=(0.045,0.10,0.16,1)
labelmat.use_nodes=True; labelmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.045,0.10,0.16,1)
labelmat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(0.045,0.10,0.16,1)
labelmat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=0.3
for label,du,dv,size in (
    ('DINING / KITCHEN',-10.0,10.3,0.70),
    ('SOCIAL ROOM',4.0,-12.6,0.70),
    ('TROPHY CASE',8.0,-14.1,0.52),
    ('HALLWAY',4.0,4.1,0.70),
    ('RESTROOM - SCHEMATIC',-19.0,8.0,0.56),
):
    text_data=bpy.data.curves.new('ReviewLabel_'+label.replace(' ','_'),'FONT')
    text_data.body=label; text_data.size=size; text_data.extrude=0.005
    text_obj=bpy.data.objects.new('ReviewLabel_'+label.replace(' ','_'),text_data)
    scene.collection.objects.link(text_obj)
    tx,ty=review_xy(du,dv); text_obj.location=(tx,ty,0.32); text_obj.rotation_euler[2]=angle
    text_obj.data.materials.append(labelmat)
scene.render.filepath=str(OUT/'alpha_sigma_phi_interior_cutaway.png')
bpy.ops.render.render(write_still=True,scene=scene.name)

# Geometry and identity checks from reopened .blend.
objs=list(root.all_objects)
mesh_objs=[o for o in objs if o.type=='MESH']
verts=[]
for o in mesh_objs:
    for v in o.data.vertices: verts.append(o.matrix_world@v.co)
bounds=[
  [min(v.x for v in verts),max(v.x for v in verts)],
  [min(v.y for v in verts),max(v.y for v in verts)],
  [min(v.z for v in verts),max(v.z for v in verts)],
]
source=json.loads((ROOT/'audit/alpha_sigma_phi/sources/arcgis_fid763_feature.json').read_text(encoding='utf-8'))['features'][0]
source_xy=[]
for lon,lat in source['geometry']['rings'][0][:-1]:
    source_xy.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
shell_obj=bpy.data.objects['House_301841603']
model_xy=sorted({(round((shell_obj.matrix_world@v.co).x,6),round((shell_obj.matrix_world@v.co).y,6)) for v in shell_obj.data.vertices})
vertex_errors=[]
for p in source_xy:
    vertex_errors.append(min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in model_xy))
source_area=abs(sum(source_xy[i][0]*source_xy[(i+1)%len(source_xy)][1]-source_xy[(i+1)%len(source_xy)][0]*source_xy[i][1] for i in range(len(source_xy)))/2)
result={
  'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),
  'fresh_open':True,
  'scene':scene.name,
  'asset_collection':root.name,
  'root_object_found':bpy.data.objects.get('House_301841603') is not None,
  'object_count':len(objs),
  'mesh_object_count':len(mesh_objs),
  'bounds_world_m':[[round(a,3),round(b,3)] for a,b in bounds],
  'source_footprint_bounds_projected_m':[
      [round(min(p[0] for p in source_xy),3),round(max(p[0] for p in source_xy),3)],
      [round(min(p[1] for p in source_xy),3),round(max(p[1] for p in source_xy),3)]
  ],
  'rendered_exterior':(OUT/'alpha_sigma_phi_exterior.png').exists(),
  'rendered_interior_cutaway':(OUT/'alpha_sigma_phi_interior_cutaway.png').exists(),
  'materials':sorted({m.name for o in objs if o.type=='MESH' for m in o.data.materials if m}),
  'asset_root_translation':[round(x,6) for x in bpy.data.objects['House_301841603'].location],
  'source_fid':source['attributes']['FID'],
  'source_vertex_count':len(source_xy),
  'model_shell_unique_xy_vertex_count':len(model_xy),
  'max_source_to_shell_vertex_error_m':round(max(vertex_errors),6),
  'source_ring_area_after_project_approx_m2':round(source_area,3),
  'gis_native_shape_area_web_mercator_m2':source['attributes']['Shape__Area'],
  'modeled_height_note':shell_obj.get('height_note',''),
  'modeled_story_count_note':shell_obj.get('story_count_note',''),
  'footprint_vertices_match':len(source_xy)==len(model_xy) and max(vertex_errors)<0.001,
}
(ROOT/'audit/alpha_sigma_phi/fresh_open_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
