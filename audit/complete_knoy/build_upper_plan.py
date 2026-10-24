import bpy,json,os,math
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BLEND=ROOT+r'\modular\buildings\knoy_hall.blend'
TRACE=ROOT+r'\audit\complete_knoy\upper_plan_wall_trace.json'
bpy.ops.wm.open_mainfile(filepath=BLEND)
asset=bpy.data.collections.get('Asset_knoy_hall')
if not asset: raise RuntimeError('Asset_knoy_hall collection missing')
name='KNOY_UpperLevel_TypicalPartitions_L2-L4'
coll=bpy.data.collections.get(name)
if coll:
    for obj in list(coll.objects): bpy.data.objects.remove(obj,do_unlink=True)
else:
    coll=bpy.data.collections.new(name);asset.children.link(coll)
trace=json.load(open(TRACE,encoding='utf-8'))
segs=trace['segments'];mat=bpy.data.materials.get('KNOY_Ground_Painted_Partitions')
if mat is None: raise RuntimeError('Expected partition material missing')
# Positions match the saved L2-L4 slab top surfaces. Partition height follows the existing
# ground-trace wall convention (2.8m); the planning sheet does not specify partition height.
levels=[('L2',4.481),('L3',8.961),('L4',13.442)]
width=0.13;height=2.8
for label,zbase in levels:
    verts=[];faces=[];nwall=0
    for seg in segs:
        (ax,ay),(bx,by)=seg['local_xy_m'];dx=bx-ax;dy=by-ay;length=math.hypot(dx,dy)
        if length<1e-6:continue
        nx=-dy/length;ny=dx/length;hx=nx*width/2;hy=ny*width/2
        base=len(verts)
        verts.extend([(ax+hx,ay+hy,zbase),(bx+hx,by+hy,zbase),(bx-hx,by-hy,zbase),(ax-hx,ay-hy,zbase),
                      (ax+hx,ay+hy,zbase+height),(bx+hx,by+hy,zbase+height),(bx-hx,by-hy,zbase+height),(ax-hx,ay-hy,zbase+height)])
        faces.extend([(base,base+1,base+2,base+3),(base+4,base+7,base+6,base+5),(base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),(base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)])
        nwall+=1
    mesh=bpy.data.meshes.new(f'KNOY_{label}_UpperPlanTrace_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update()
    obj=bpy.data.objects.new(f'KNOY_{label}_TypicalPlan_InteriorPartitions',mesh);coll.objects.link(obj)
    obj['source']='Purdue College of Engineering Gateway Formation Study; PDF page 24, Typical Plan Levels 2-4, review 2018-05-31.'
    obj['source_url']='https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf'
    obj['source_plan_crop']=trace['source_image']
    obj['source_trace_json']='audit/complete_knoy/upper_plan_wall_trace.json'
    obj['trace_method']='Automated raster line extraction on the preserved plan crop: luminance <0.8 and chroma <0.16; straight runs along 0/45/90/135-degree axes, consolidated within 2 pixels; excluded likely exterior wall centerlines within 1.2m of GIS footprint boundary and manually masked visible stair cores.'
    obj['trace_segment_count']=nwall
    obj['source_registration']='Manual three-control affine registration to official GIS, approximately +/-1m; no printed scale/north arrow.'
    obj['partition_height_m']=height
    obj['partition_height_status']='Estimated from existing L1 trace-wall convention; source plan does not state internal partition height.'
    obj['source_level']=label
    obj['floor_base_z_m']=zbase
    obj['level_height_reference_m']=4.4704
    obj['uncertainty']='Planning study is not an as-built drawing. Raster linework includes ambiguous short fixture/service-area marks; segments below 1.25m are omitted. Door openings follow plan line gaps but individual widths are not surveyed.'
# Add source and trace summary to asset evidence.
sc=bpy.context.scene;root=bpy.data.objects.get('AssetRoot_knoy_hall')
for owner in (sc,root):
    if owner is not None:
        owner['typical_upper_plan_modeled']=f'PDF page 24 typical Levels 2-4 raster trace; {len(segs)} retained segments per level, local GIS registration +/-1m.'
        owner['typical_upper_plan_model_collection']=name
        owner['typical_upper_plan_partition_height']='2.8m illustrative estimate; only plan location is source-derived, height is not shown.'
# Make sure the collection remains inside the exported asset hierarchy.
asset.children.unlink(coll) if coll.name in [c.name for c in asset.children] else None
asset.children.link(coll)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('saved upper-floor partition trace',len(segs),'segments/level, collection',coll.name,'asset children',[c.name for c in asset.children])


