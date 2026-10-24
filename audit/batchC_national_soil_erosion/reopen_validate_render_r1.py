import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
ASSET=ROOT/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
COL=bpy.data.collections['Asset_national_soil_erosion_laboratory']
WALL=bpy.data.objects['National Soil Erosion Research Laboratory | GIS perimeter wall panels with real glazing openings']
ROOF=bpy.data.objects['SOIL | structural flat roof']
LOW=bpy.data.objects['SOIL | evidence-backed lower east roof wing']
X_BREAK=-6.49; LOW_Z=5.20; HIGH_Z=7.32

def bounds(o):
    vv=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)]
def mesh_area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def projected_top_vertices(o):
    return [o.matrix_world@v.co for v in o.data.vertices]

wv=projected_top_vertices(WALL)
east_z=max(v.z for v in wv if v.x>X_BREAK+0.02)
west_z=max(v.z for v in wv if v.x<X_BREAK-1e-4)
hb=bounds(ROOF); lb=bounds(LOW)
orig=[-548.283393,-674.397642]
refs=json.loads((ROOT/'audit'/'official_building_references.json').read_text(encoding='utf-8'))
ft=next(f for f in refs['buildings'] if int(f.get('fid',-1))==242)
gis=[(x-orig[0],y-orig[1]) for x,y in ft['rings_xy_m'][0]]
roof_area=mesh_area([(v.co.x,v.co.y) for v in ROOF.data.vertices[:len(ROOF.data.vertices)//2]])+mesh_area([(v.co.x,v.co.y) for v in LOW.data.vertices[:len(LOW.data.vertices)//2]])
gis_area=mesh_area(gis)
mat_list=sorted({m.name for o in COL.all_objects if o.type=='MESH' for m in o.data.materials if m})
external=[]
for img in bpy.data.images:
    if img.source=='FILE' and img.filepath and not img.packed_file:
        p=Path(bpy.path.abspath(img.filepath))
        if not p.exists(): external.append(str(img.filepath))
val={
 'reload':'PASS','asset_file':'modular/buildings/national_soil_erosion_laboratory.blend',
 'collection':'Asset_national_soil_erosion_laboratory','object_count':len(COL.all_objects),
 'mesh_object_count':sum(o.type=='MESH' for o in COL.all_objects),
 'wall_vertex_count':len(WALL.data.vertices),'wall_face_count':len(WALL.data.polygons),
 'east_wall_max_z_m':east_z,'west_wall_max_z_m':west_z,
 'high_roof_bounds_m':hb,'low_roof_bounds_m':lb,
 'official_footprint_area_m2':round(gis_area,2),'two_roof_wing_plan_area_m2':round(roof_area,2),
 'roof_plan_area_delta_percent':round(100*(roof_area-gis_area)/gis_area,3),
 'material_count':len(mat_list),'external_missing_textures':external,
 'checks':{'east_wall_trimmed_to_approx_5_2m':east_z<=LOW_Z+0.02,'west_wall_retains_approx_7_32m':west_z>=HIGH_Z-0.02,'roof_regions_separate':hb[0][1]<=X_BREAK+0.01 and lb[0][0]>=X_BREAK-0.01,'roof_plan_matches_GIS_within_1pct':abs(roof_area-gis_area)/gis_area<0.01,'no_missing_external_textures':not external},
 'interior_collection_objects':len(bpy.data.collections['SOIL_Interior'].all_objects)
}
val['status']='PASS' if all(val['checks'].values()) else 'CHECK'
(AUDIT/'nsel_revision_r1_validation.json').write_text(json.dumps(val,indent=2)+'\n',encoding='utf-8')

scene=bpy.context.scene
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
oldcam=scene.camera
def add_camera(name,loc,target,ortho=None,lens=52):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=loc; direction=Vector(target)-Vector(loc);cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    if ortho is not None: cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else: cam.data.lens=lens
    return cam
cam=add_camera('TEMP | NSEL R1 exterior three-quarter',(82,-116,72),(0,0,3.1),ortho=94)
scene.camera=cam;scene.render.filepath=str(AUDIT/'nsel_revision_r1_exterior_threequarter.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,110);cam.rotation_euler=Vector((0,0,-1)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=82
scene.render.filepath=str(AUDIT/'nsel_revision_r1_roof_orthographic.png');bpy.ops.render.render(write_still=True)

# A roof-off cutaway is useful for judging the currently schematic, sparse
# interior. Hide exterior envelope and floor plates only for this render.
hidden=[]
for o in COL.all_objects:
    if o in (WALL,ROOF,LOW) or o.name.startswith('SOIL | facade') or o.name.startswith('SOIL | vertical glazing') or 'roof parapet coping' in o.name.lower() or 'floor plate' in o.name.lower() or o.name.startswith('National Soil Erosion Research Laboratory | GIS footprint'):
        hidden.append((o,o.hide_render));o.hide_render=True
cam.location=(0,-72,54);cam.rotation_euler=(Vector((0,0,1.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=82
scene.render.filepath=str(AUDIT/'nsel_revision_r1_interior_cutaway.png');bpy.ops.render.render(write_still=True)
for o,h in hidden:o.hide_render=h
scene.camera=oldcam
camdata=cam.data
bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
print(json.dumps(val,indent=2))
