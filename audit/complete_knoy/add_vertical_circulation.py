import bpy
import json
import math
import os

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BLEND = ROOT + r'\modular\buildings\knoy_hall.blend'
TRACE = ROOT + r'\audit\complete_knoy\upper_plan_wall_trace.json'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
asset = bpy.data.collections.get('Asset_knoy_hall')
if asset is None:
    raise RuntimeError('Asset_knoy_hall missing')

name = 'KNOY_TypicalPlan_StairRuns_L2-L4'
old = bpy.data.collections.get(name)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    old = bpy.data.collections.new(name)
    asset.children.link(old)
if old.name not in [c.name for c in asset.children]:
    asset.children.link(old)

trace = json.load(open(TRACE, encoding='utf-8'))
aff = trace['pixel_to_local_xy_affine']
def xy(u, v):
    return (aff['x'][0]*u + aff['x'][1]*v + aff['x'][2],
            aff['y'][0]*u + aff['y'][1]*v + aff['y'][2])

# These regions were explicitly masked out of line extraction because the source
# plan depicts stair symbols there. Their boxes are approximate pixel regions, not
# construction dimensions. Keep each stair inside a conservative envelope.
source_cores = [
    {'id':'A', 'box_px':[360,165,410,225]},
    {'id':'B', 'box_px':[100,690,190,785]},
    {'id':'C', 'box_px':[435,1195,515,1270]},
]
for core in source_cores:
    x0,y0=xy(core['box_px'][0],core['box_px'][1])
    x1,y1=xy(core['box_px'][2],core['box_px'][3])
    core['center_xy']=((x0+x1)/2,(y0+y1)/2)
    core['source_box_dimensions_xy']=(abs(x1-x0),abs(y1-y0))

mat = bpy.data.materials.get('KNOY_Precast_Concrete')
if mat is None:
    raise RuntimeError('Evidence-backed neutral concrete material missing')

def add_box(verts, faces, cx, cy, cz, sx, sy, sz):
    base=len(verts)
    verts.extend([(cx-sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy-sy/2,cz-sz/2),
                  (cx+sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy+sy/2,cz-sz/2),
                  (cx-sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy-sy/2,cz+sz/2),
                  (cx+sx/2,cy+sy/2,cz+sz/2),(cx-sx/2,cy+sy/2,cz+sz/2)])
    faces.extend([(base,base+3,base+2,base+1),(base+4,base+5,base+6,base+7),
                  (base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),
                  (base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)])

# The page labels Levels 2-4 as typical and the adjacent existing elevations give
# 14 ft 8 in nominal floor-to-floor. Two 13-riser flights span each L2-L3 / L3-L4
# interval. Runs and tread widths are conservative, visible-plan estimates.
transitions=[('L2','L3',4.481,8.961),('L3','L4',8.961,13.442)]
tread_depth=0.28
flight_width=1.12
flight_gap=0.30
landing_width=2.54
landing_depth=0.42
landing_thickness=0.10
risers_per_flight=13
for src,dst,z0,z1 in transitions:
    rise=(z1-z0)/(2*risers_per_flight)
    run=tread_depth*risers_per_flight
    for core in source_cores:
        cx,cy=core['center_xy']
        verts=[];faces=[]
        for flight,(xsign,reverse,zbase) in enumerate([(-1,False,z0),(1,True,z0+rise*risers_per_flight)]):
            fx=cx+xsign*(flight_width+flight_gap)/2
            for i in range(risers_per_flight):
                if not reverse:
                    sy=cy-run/2+(i+0.5)*tread_depth
                else:
                    sy=cy+run/2-(i+0.5)*tread_depth
                top=zbase+(i+1)*rise
                add_box(verts,faces,fx,sy,top-0.045,flight_width,tread_depth-0.015,0.09)
        # Shared half-level landing and end landings make the run visually legible.
        add_box(verts,faces,cx,cy,z0+(z1-z0)/2-landing_thickness/2,
                landing_width,landing_depth,landing_thickness)
        add_box(verts,faces,cx,cy-run/2-landing_depth/2,z0+landing_thickness/2,
                landing_width,landing_depth,landing_thickness)
        add_box(verts,faces,cx,cy+run/2+landing_depth/2,z1-landing_thickness/2,
                landing_width,landing_depth,landing_thickness)
        mesh=bpy.data.meshes.new(f'KNOY_Stair_{src}_{dst}_Core_{core["id"]}_Mesh')
        mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update()
        obj=bpy.data.objects.new(f'KNOY_Stair_{src}_{dst}_Core_{core["id"]}',mesh)
        old.objects.link(obj)
        obj['source']='Purdue College of Engineering Gateway Formation Study, 2018-05-31, PDF page 24, Typical Plan Levels 2-4.'
        obj['source_url']=trace.get('source_url','https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf')
        obj['source_stair_core_pixel_box']=core['box_px']
        obj['source_stair_core_local_xy_center_m']=[round(cx,3),round(cy,3)]
        obj['source_stair_core_local_xy_box_size_m']=[round(core['source_box_dimensions_xy'][0],2),round(core['source_box_dimensions_xy'][1],2)]
        obj['levels_connected']=f'{src} to {dst}'
        obj['flight_count']=2;obj['risers_per_flight']=risers_per_flight
        obj['floor_to_floor_height_m']=round(z1-z0,4)
        obj['geometry_status']='Illustrative switchback flights positioned in stair symbols visible on the typical plan. Exact riser/tread dimensions and finish are not dimensioned by the source; material is a neutral estimate.'
        obj['registration_uncertainty']='The three-control affine plan registration is approximate +/-1m; source drawing has no printed scale or north arrow.'

scene['vertical_circulation_status']='Added two source-traced typical-floor stair intervals (L2-L3 and L3-L4) at the three manually masked stair-symbol regions in the official 2018 plan. Geometry/risers/treads/material are illustrative estimates; no basement, L1, L5 or roof connection is asserted.'
scene['typical_plan_stair_evidence']='audit/complete_knoy/upper_plan_wall_trace.json; stair symbol mask boxes retained in audit/complete_knoy/add_vertical_circulation.py.'
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('Saved 6 illustrative stair assemblies in',name)
