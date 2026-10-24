import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
ASSET=ROOT/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
INTERIOR=bpy.data.collections['SOIL_Interior']
COL=bpy.data.collections['Asset_national_soil_erosion_laboratory']
for obj in list(COL.all_objects):
    if obj.name.startswith('SOIL | R3 '):bpy.data.objects.remove(obj,do_unlink=True)

# The 2018 exterior photograph shows large raised laboratory lettering. Its
# scale remains an estimate because the photo has no architectural dimensions.
title=bpy.data.objects['SOIL | R2 entrance sign main line']
service=bpy.data.objects['SOIL | R2 entrance sign service line']
agency=bpy.data.objects['SOIL | R2 entrance sign agency line']
address=bpy.data.objects['SOIL | R2 entrance address plaque']
front_slope=-0.040643
front_angle=math.atan(front_slope)
front_line=lambda x:-25.560637+front_slope*(x-20.253156)
for obj,x,size in ((title,-3.5,.50),(service,-3.5,.31),(agency,-3.5,.31),(address,2.59,.27)):
    obj.data.size=size
    obj.location.x=x
    obj.location.y=front_line(x)-.06
    obj.rotation_euler=(math.pi/2,0,front_angle)
    obj.data.extrude=.014
    obj.data.bevel_depth=.002
    obj.data.bevel_resolution=2
bpy.context.view_layer.update()
sign_metrics={o.name:{'text':o.data.body,'estimated_font_height_m':o.data.size,'evaluated_width_m':o.dimensions.x,'location_m':list(o.location)} for o in (title,service,agency,address)}

# Add a bounded high-bay floor and three portal frames around the photographed
# USDA-style flume apparatus. Room extent, columns and frame dimensions are
# illustrative estimates, not a surveyed interior layout.
concrete=bpy.data.materials['SOIL | cast concrete']
steel=bpy.data.materials['SOIL | R2 brushed hydraulic steel']
def box(name,center,dims,mat):
    dx,dy,dz=dims
    verts=[(x,y,z) for x in (-dx/2,dx/2) for y in (-dy/2,dy/2) for z in (-dz/2,dz/2)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh=bpy.data.meshes.new(name+' | mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);INTERIOR.objects.link(obj);obj.location=center
    if mat:mesh.materials.append(mat)
    return obj
def beam(name,a,b,width,depth,mat):
    start=Vector(a);end=Vector(b);delta=end-start
    obj=box(name,(start+end)/2,(width,depth,delta.length),mat)
    obj.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    return obj
fcx=-25.4
floor=box('SOIL | R3 bounded high-bay concrete floor',(fcx,0,-.08),(9.0,35.5,.16),concrete)
for index,y in enumerate((-13.5,0,13.5)):
    for side in (-1,1):
        x=fcx+side*4.05
        box(f'SOIL | R3 high-bay portal column {index}-{side}',(x,y,3.18),(.18,.18,6.36),steel)
    beam(f'SOIL | R3 high-bay portal crossbeam {index}',(fcx-4.05,y,6.36),(fcx+4.05,y,6.36),.18,.18,steel)
for side in (-1,1):
    x=fcx+side*4.05
    beam(f'SOIL | R3 high-bay longitudinal tie {side}',(x,-13.5,6.36),(x,13.5,6.36),.14,.14,steel)
# A narrow dry service walkway complements the existing handrail and control
# station, matching the side access visible in the USDA interior photograph.
walk=box('SOIL | R3 high-bay service walkway',(fcx+2.35,0,.09),(1.0,33.5,.18),concrete)

scene=bpy.context.scene
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
report={
 'revision':'R3','previous_independent_score':'7.6/10',
 'source':['https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg','https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/','https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer'],
 'exterior_sign_changes':sign_metrics,
 'high_bay_context':{'floor_bounds_local_m':[[fcx-4.5,fcx+4.5],[-17.75,17.75],[-.16,0]],'portal_frame_y_positions_m':[-13.5,0,13.5],'column_height_m':6.36,'service_walkway_dimensions_m':[1.0,33.5,.18],'all_room_dimensions_approximate':True,'source_support':'USDA ARS K7567-11 hydraulics-lab photo shows the flume in a large industrial lab with a hard floor, access platforms, supports and test equipment.'},
 'roof_facade_decision':'No roof geometry changes in R3. The 2023 aerial confirms plan outline and broad roof zones, but its imagery does not support additional height, parapet or rooftop equipment dimensions. The 2018 wall photo supports the larger raised name lettering and blank brick field.',
 'limitations':['Font size and exact sign position are estimated from the 2018 visitor photo, not an elevation.','High-bay floor extent, portal frame layout and walkway are illustrative, based on equipment context in the USDA image; exact room layout and circulation remain unverified.','Roof height split remains approximate from 5-ft DSM cells and interpolated DTM ground, not surveyed.']
}
(AUDIT/'nsel_revision_r3.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
