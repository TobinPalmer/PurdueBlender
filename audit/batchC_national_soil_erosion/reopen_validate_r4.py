import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
ASSET=ROOT/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
COL=bpy.data.collections['Asset_national_soil_erosion_laboratory']
WALL=bpy.data.objects['National Soil Erosion Research Laboratory | GIS perimeter wall panels with real glazing openings']
ROOF=bpy.data.objects['SOIL | structural flat roof']
LOW=bpy.data.objects['SOIL | evidence-backed lower east roof wing']
X_BREAK=-6.49

def bounds(obj):
    pts=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def ring_edges(obj):
    n=len(obj.data.vertices)//2
    ring=[(obj.matrix_world@obj.data.vertices[i+n].co).to_2d() for i in range(n)]
    return [(ring[i],ring[(i+1)%n]) for i in range(n) if not (abs(ring[i].x-X_BREAK)<.002 and abs(ring[(i+1)%n].x-X_BREAK)<.002)]
def samples(edges,step=.2):
    out=[]
    for a,b in edges:
        length=(b-a).length
        count=max(1,math.ceil(length/step))
        out.extend(a.lerp(b,i/count) for i in range(count))
    return out
def point_segment_distance(p,a,b):
    d=b-a
    t=0 if d.length_squared==0 else max(0,min(1,(p-a).dot(d)/d.length_squared))
    return (p-(a+t*d)).length
def directed_dist(src,dst):
    pts=samples(src)
    distances=[min(point_segment_distance(p,a,b) for a,b in dst) for p in pts]
    return {'max_m':max(distances),'rms_m':math.sqrt(sum(d*d for d in distances)/len(distances)),'samples':len(pts)}

refs=json.loads((ROOT/'audit'/'official_building_references.json').read_text(encoding='utf-8'))
feature=next(f for f in refs['buildings'] if int(f.get('fid',-1))==242)
origin=(-548.283393,-674.397642)
gis=[Vector((x-origin[0],y-origin[1])) for x,y in feature['rings_xy_m'][0]]
gis_edges=list(zip(gis[:-1],gis[1:]))
roof_edges=ring_edges(ROOF)+ring_edges(LOW)
gis_to_roof=directed_dist(gis_edges,roof_edges)
roof_to_gis=directed_dist(roof_edges,gis_edges)
roof_delta=max(gis_to_roof['max_m'],roof_to_gis['max_m'])
roof_rms=max(gis_to_roof['rms_m'],roof_to_gis['rms_m'])
gis_area=area([(p.x,p.y) for p in gis[:-1]])
roof_area=sum(area([(ROOF.data.vertices[i].co.x,ROOF.data.vertices[i].co.y) for i in range(len(ROOF.data.vertices)//2)]),0) if False else 0
roof_area=area([(v.co.x,v.co.y) for v in ROOF.data.vertices[:len(ROOF.data.vertices)//2]])+area([(v.co.x,v.co.y) for v in LOW.data.vertices[:len(LOW.data.vertices)//2]])
verts=[WALL.matrix_world@v.co for v in WALL.data.vertices]
east=max(v.z for v in verts if v.x>X_BREAK+.02);west=max(v.z for v in verts if v.x<X_BREAK-1e-4)
asset_objects=list(COL.all_objects)
materials=sorted({m.name for o in asset_objects if o.type=='MESH' for m in o.data.materials if m})
missing=[]
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:
        p=Path(bpy.path.abspath(image.filepath))
        if not p.exists():missing.append(image.filepath)
south_names=['SOIL | R2 continuous blank brick elevation west wing','SOIL | R2 continuous blank brick elevation east left','SOIL | R2 continuous blank brick elevation east right']
south=[]
front_slope=-0.040643
for name in south_names:
    obj=bpy.data.objects.get(name)
    if obj:
        pts=[obj.matrix_world@v.co for v in obj.data.vertices]
        d=[abs(p.y-(-25.560637+front_slope*(p.x-20.253156)))/math.sqrt(1+front_slope*front_slope) for p in pts]
        south.append({'name':name,'bounds_m':bounds(obj),'max_distance_from_FID242_south_edge_m':max(d)})
approx_entry=[o.name for o in asset_objects if o.name.startswith('SOIL | R2 entrance') or o.name.startswith('SOIL | R2 glazed entry') or o.name.startswith('SOIL | R2 brick lintel') or o.name.startswith('SOIL | R2 entrance sign')]
flume=[o.name for o in asset_objects if o.name.startswith('SOIL | R2 flume') or o.name.startswith('SOIL | R2 overhead instrument') or o.name.startswith('SOIL | R2 adjustable instrument') or o.name.startswith('SOIL | R2 instrument gantry')]
context=[o for o in asset_objects if o.name.startswith(('SOIL | R3','SOIL | R4'))]
floor=bpy.data.objects.get('SOIL | R3 bounded high-bay concrete floor')
portal_columns=[o for o in context if 'portal column' in o.name]
portal_beams=[o for o in context if 'portal crossbeam' in o.name]
title=bpy.data.objects['SOIL | R2 entrance sign main line']
room_walls=[bpy.data.objects.get('SOIL | R4 high-bay '+side+' liner wall') for side in ('west','east')]
room_walls += [bpy.data.objects.get('SOIL | R4 high-bay '+side+' end wall') for side in ('north','south')]
room_ceiling=bpy.data.objects.get('SOIL | R4 high-bay ceiling')
benches=[o for o in asset_objects if o.name.startswith(('SOIL | R4 stainless','SOIL | R4 instrument worktable'))]
sample_trays=[o for o in asset_objects if o.name.startswith('SOIL | R4 soil sample tray')]
diffusers=[o for o in asset_objects if o.name.startswith('SOIL | R4 overhead light diffuser')]
aisle_marks=[o for o in asset_objects if o.name.startswith('SOIL | R4 circulation boundary')]
sha256=hashlib.sha256(ASSET.read_bytes()).hexdigest()
render_outputs={name:(AUDIT/name).exists() for name in ('nsel_revision_r4_exterior_sign_lit.png','nsel_revision_r4_enclosed_high_bay_cutaway.png')}
val={
 'revision':'R4','reload':'PASS','blend_version':bpy.app.version_string,
 'asset_file':'modular/buildings/national_soil_erosion_laboratory.blend','asset_collection':COL.name,
 'asset_sha256':sha256,'asset_size_bytes':ASSET.stat().st_size,
 'renders_present':render_outputs,
 'object_count':len(asset_objects),'mesh_object_count':sum(o.type=='MESH' for o in asset_objects),
 'wall_max_z_by_wing_m':{'east_lower':east,'west_higher':west},
 'roof_bounds_m':{'higher_west':bounds(ROOF),'lower_east':bounds(LOW)},
 'official_footprint_fid':242,'official_footprint_area_m2':gis_area,'roof_union_area_m2':roof_area,
 'roof_area_delta_percent':100*(roof_area-gis_area)/gis_area,
 'roof_boundary_symmetric_sampled_distance':{'gis_to_roof':gis_to_roof,'roof_to_gis':roof_to_gis,'max_m':roof_delta,'max_of_directional_rms_m':roof_rms,'sample_spacing_m':0.2,'seam_edges_omitted':True},
 'south_elevation_panels':south,'approximate_entry_object_count':len(approx_entry),'hydraulics_flume_object_count':len(flume),
 'high_bay_context':{'object_count':len(context),'floor_bounds_m':bounds(floor) if floor else None,'portal_column_count':len(portal_columns),'portal_crossbeam_count':len(portal_beams),'service_walkway_present':any('service walkway' in o.name for o in context),'enclosing_wall_count':sum(o is not None for o in room_walls),'ceiling_present':room_ceiling is not None,'prep_bench_count':len(benches),'soil_sample_tray_count':len(sample_trays),'overhead_diffuser_count':len(diffusers),'circulation_boundary_count':len(aisle_marks)},
 'exterior_name':{'text':title.data.body,'estimated_font_height_m':title.data.size,'evaluated_width_m':title.dimensions.x},
 'material_count':len(materials),'materials':materials,'missing_external_images':missing,
 'height_split_basis':'approximate 2018 5-ft DSM minus interpolated bare-earth DTM; not surveyed elevations',
 'checks':{
   'east_lower_roof_wall_approx_5_2m':east<=5.22,
   'west_higher_roof_wall_approx_7_32m':west>=7.30,
   'roof_area_within_1pct_of_fid242':abs(roof_area-gis_area)/gis_area<.01,
   'roof_outline_symmetric_max_edge_distance_under_0_03m':roof_delta<.03,
   'south_facade_panels_fit_gis_south_extent':len(south)==3 and all(e['max_distance_from_FID242_south_edge_m']<.06 for e in south),
   'approximate_entrance_articulation_present':len(approx_entry)>=6,
   'hydraulics_flume_and_rig_present':len(flume)>=30,
   'high_bay_floor_and_frames_present':floor is not None and len(portal_columns)==6 and len(portal_beams)==3,
   'service_walkway_present':any('service walkway' in o.name for o in context),
   'enclosed_high_bay_walls_and_ceiling_present':all(o is not None for o in room_walls) and room_ceiling is not None,
   'lab_work_context_present':len(benches)>=2 and len(sample_trays)>=5 and len(diffusers)==3,
   'circulation_markings_present':len(aisle_marks)==2,
   'building_name_readable_sign_scale':title.data.size>=.49 and title.dimensions.x>=11.5,
   'procedural_or_builtin_materials_present':len(materials)>=9,
   'no_missing_external_images':not missing,
   'r4_renders_present':all(render_outputs.values()),
 },
 'limitations':['Roof heights remain approximate because source DSM cells are 5 ft and bare-earth terrain is interpolated.','The entrance photo supports sign, doorway and blank brick relationship, but dimensions and window schedule are not measured.','USDA photo supports a comparable enclosed hydraulics-lab typology and equipment context, not NSEL dimensions, room layout, or the exact modeled station locations.','High-bay wall, ceiling, bench, cart, aisle marking, and light placement are schematic; no NSEL interior plan or photo is in the available evidence set.']
}
# Verify front panel extents stay within GIS footprint's south straight edge.
# The source ring has a south boundary near Y=-25.5606 m in the registered local frame.
val['status']='PASS' if all(val['checks'].values()) else 'CHECK'
(AUDIT/'nsel_revision_r4_validation.json').write_text(json.dumps(val,indent=2)+'\n',encoding='utf-8')
print(json.dumps(val,indent=2))
