import bpy, os, math, json
from mathutils import Vector
OUT=os.path.dirname(__file__)
BLEND=os.path.abspath(r"modular/buildings/rawls_hall.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=20
s.render.resolution_x=1200;s.render.resolution_y=840;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.film_transparent=False
for o in bpy.data.objects:
    if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World')
s.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.55,0.62,0.72,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
ld=bpy.data.lights.new('RAWL_Batch4_Sun','SUN');ld.energy=2.0
sun=bpy.data.objects.new('RAWL_Batch4_Sun',ld);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-34),math.radians(-35))
cam_data=bpy.data.cameras.new('RAWL_Batch4_Camera');cam=bpy.data.objects.new('RAWL_Batch4_Camera',cam_data);s.collection.objects.link(cam);s.camera=cam
def point(eye,target):
    cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def render(name,eye,target,ortho=None,lens=42):
    point(eye,target);cam.data.lens=lens
    if ortho:
        cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else:cam.data.type='PERSP'
    s.render.filepath=os.path.join(OUT,name+'.png')
    bpy.ops.render.render(write_still=True)

saved_interior={}
for o in bpy.data.objects:
    if o.name.startswith('RAWL_2026_'):
        saved_interior[o.name]=o.hide_render;o.hide_render=True
render('exterior_round1',(76,73,58),(2,0,12),ortho=102)
for name,value in saved_interior.items():bpy.data.objects[name].hide_render=value

# Hide only upper level, roof, exterior shell and glazing for first-floor cutaways.
hidden={}
hide_prefixes=("RAWL_Masonry_Exterior_Walls","RAWL_Basement_Foundation_Walls","RAWL_Limestone_Base_Plinth",
"RAWL_Limestone_BeltCourse","RAWL_Limestone_Parapet","RAWL_NW_Rotunda","RAWL_North_Windows",
"RAWL_SE_Diagonal","RAWL_South_Windows","RAWL_West_Windows","RAWL_East_Windows",
"RAWL_Roof","RAWL_Rooftop","RAWL_Site_Sidewalk_Apron")
for o in bpy.data.objects:
    h=(o.type=='MESH' and o.name!='RAWL_FloorSlab_L1_Ground' and not o.name.startswith('RAWL_2026_'))
    if o.name.startswith('RAWL_FloorSlab_L') and o.name!='RAWL_FloorSlab_L1_Ground':h=True
    if h:
        hidden[o.name]=o.hide_render;o.hide_render=True

area_data=bpy.data.lights.new('RAWL_Batch4_Interior_Area','AREA');area_data.energy=1800;area_data.shape='DISK';area_data.size=8
area=bpy.data.objects.new('RAWL_Batch4_Interior_Area',area_data);s.collection.objects.link(area);area.location=(34,2,7);area.rotation_euler=(0,0,0)
render('interior_1086_round1',(24,5.0,1.72),(34.0,2.3,1.52),lens=35)
render('first_floor_cutaway_round1',(8,14,82),(8,-2,0),ortho=108)

# Restore render flags, then write the measurements report without saving temp render gear.
for name,value in hidden.items():bpy.data.objects[name].hide_render=value
root=bpy.data.objects.get('AssetRoot_rawls_hall')
fp=bpy.data.objects.get('RAWL_FloorSlab_L1_Ground')
poly=[fp.matrix_world@fp.data.vertices[i].co for i in range(29)]
poly=[(p.x,p.y) for p in poly]
def inside(x,y):
    c=False;j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i];xj,yj=poly[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
        j=i
    return c
furn=[o for o in bpy.data.collections['Asset_rawls_hall'].all_objects if o.type=='MESH' and ('1086_Desk' in o.name or '1086_Chair' in o.name)]
validation={"source_blend":BLEND,"export_collection":"Asset_rawls_hall","collection_objects":len(bpy.data.collections['Asset_rawls_hall'].all_objects),"desks":sum('1086_Desk' in o.name for o in furn),"chairs":sum('1086_Chair' in o.name for o in furn),"furniture_centroids_inside_gis_shell":sum(inside(o.matrix_world.translation.x,o.matrix_world.translation.y) for o in furn),"furniture_centroid_total":len(furn),"root_world_matrix":[[round(v,6) for v in row] for row in root.matrix_world] if root else None,"ground_bounds_world_m":[[round(min((fp.matrix_world@v.co)[i] for v in fp.data.vertices),3),round(max((fp.matrix_world@v.co)[i] for v in fp.data.vertices),3)] for i in range(3)]}
with open(os.path.join(OUT,'round1_validation.json'),'w') as f:json.dump(validation,f,indent=2)
print('RENDER_VALIDATION',json.dumps(validation))
