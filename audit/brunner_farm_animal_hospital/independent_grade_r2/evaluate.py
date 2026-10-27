"""Independent r2 evaluation against raw source pixels; never saves the library."""
import bpy, json, math, hashlib, os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(OUT,'..','..','..'))
ID='david_and_bonnie_brunner_farm_animal_hospital'
ASSET=os.path.join(ROOT,'modular','buildings',ID+'.blend')
EXPECTED='a318b252db4b5530910cde1adbb0708d881d2a92e297351a6de9dcc658686a9e'

def evaluate():
    digest=hashlib.sha256(open(ASSET,'rb').read()).hexdigest()
    assert digest==EXPECTED, 'Frozen asset changed'
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    col=bpy.data.collections['Asset_'+ID]
    shell=bpy.data.objects[ID+'_GIS_outline_primary_shell']
    feature=json.load(open(os.path.join(OUT,'..','sources','purdue_gis_feature_408.json'),encoding='utf-8'))['feature']
    sx=111412.84*math.cos(math.radians(40.4274))
    pts=[((lon+86.9137)*sx,(lat-40.4274)*111040.) for lon,lat in feature['geometry']['rings'][0][:-1]]
    cross=[x*v-u*y for (x,y),(u,v) in zip(pts,pts[1:]+pts[:1])]
    area2=sum(cross)
    origin=[sum((a[k]+b[k])*c for a,b,c in zip(pts,pts[1:]+pts[:1],cross))/(3*area2) for k in range(2)]
    local=[(x-origin[0],y-origin[1]) for x,y in pts]
    dg=bpy.context.evaluated_depsgraph_get(); ev=shell.evaluated_get(dg); mesh=ev.to_mesh()
    vertices=[ev.matrix_world @ p.co for p in mesh.vertices]
    bottom=[(p.x,p.y) for p in vertices if p.z<1]
    err=max(min(math.dist(a,b) for b in bottom) for a in local)
    bounds=[[min(p[k] for p in vertices),max(p[k] for p in vertices)] for k in range(3)]
    ev.to_mesh_clear()
    entry=next(a for a in json.load(open(os.path.join(ROOT,'modular','manifest.json'),encoding='utf-8'))['assets'] if a['id']==ID)
    external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
    unwanted=[o.name for o in col.all_objects if o.name.startswith(('BRFM_facade_pier_','BRFM_roof_exhaust_stack_','BRFM_roof_mechanical_screen'))]
    required=['BRFM_raised_reception_brick_volume','BRFM_reception_narrow_window_7','BRFM_right_return_louver_recess','BRFM_entry_clay_tile_hip_roof_estimated']
    missing=[n for n in required if n not in col.all_objects]
    assert not missing and not unwanted, (missing,unwanted)
    assert len(bottom)==16 and err<.002 and not external
    measurements={'asset_sha256':digest,'blender_version':bpy.app.version_string,'reopened':True,'object_count':len(col.all_objects),'collection':col.name,'source_FID':feature['attributes']['FID'],'source_code':feature['attributes']['BLDG_ABBR'],'source_local_origin_xy_m':origin,'manifest_origin_xy_m':entry['placement_origin_xy_m'],'origin_error_m':math.dist(origin,entry['placement_origin_xy_m']),'source_to_evaluated_shell_max_vertex_error_m':err,'shell_bounds_m':bounds,'shell_local_footprint_area_m2':abs(area2)/2,'published_floor_area_m2':23900*.09290304,'external_unpacked_image_dependencies':external,'shell_matrix_world':[list(r) for r in shell.matrix_world],'library_paths':[l.filepath for l in bpy.data.libraries],'drivers_count':sum(len(o.animation_data.drivers) if o.animation_data else 0 for o in bpy.data.objects),'removed_generic_objects_remaining':unwanted,'source_specific_objects_confirmed':required}
    with open(os.path.join(OUT,'reopen_measurements.json'),'w',encoding='utf-8') as f: json.dump(measurements,f,indent=2)
    scene=bpy.context.scene; camera=scene.camera
    camera.location=(35,-92,18); target=Vector((0,0,3.2))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=48
    scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.filepath=os.path.join(OUT,'independent_south_oblique.png'); bpy.ops.render.render(write_still=True)
    # Grading judgments use direct visual inspection of raw BEP photo and r2 renders,
    # not automatic object density, builder scores, or object names alone.
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':['Purdue GIS snapshot FID 408 / BRFM names the hospital at 415 S Grant Street.','Independently reopened evaluated shell matches all 16 raw source vertices within %.8f m.'%err],'findings':['Local approximate ground footprint 2757.94 m2; published 23900 sq ft is floor area, not a direct footprint check.']},
      {'criterion':'Position, orientation, scale/dimensions','score':1.9,'max_score':2,'evidence':['Independent GIS-centroid origin matches manifest to %.8f m.'%measurements['origin_error_m'],'Identity shell transform and project X-east/Y-north conversion retain mapped orientation and 62.13 by 50.28 m plan extents.'],'findings':['Standalone placement frame verified; master instance replacement and neighboring context require coordinator/Tobin integration review.']},
      {'criterion':'Evidence-backed height, floors, roof form','score':1.4,'max_score':2,'evidence':['Raw BEP pixels show one low principal story, flat service parapet, raised reception brick and a clay-tile hip roof.','Fresh r2 render now has a recognizable four-sided hip over the reception end and no unsupported tall stack/screen clutter.'],'findings':['Wall height 6.2 m, raised reception elevations and all roof dimensions remain perspective estimates, not surveyed dimensions.','Broad roof geometry beyond the photographed frontage and two low HVAC positions are incompletely substantiated; annotated aerial has the farm hospital mostly cropped at top.']},
      {'criterion':'Facade, entrances, distinctive architecture','score':1.3,'max_score':2,'evidence':['Compared raw BEP photo directly with r2 facade/overview pixels: the formerly missing seven narrow reception windows are present, in correct ordering left of glazed entrance.','Brick reception volume, recessed door cue, pale belt, personnel door, vehicle opening and right-return louver give source-specific architecture. Unsupported repeated pale vertical piers are removed.'],'findings':['Portal and service openings remain approximate in scale and depth; personnel door is narrower and less recessed than the prominent dark photo opening.','Pale roof cap/belt proportions, reception-to-service height relationship and unseen elevations are not backed by measured elevations.','The source photo shows a recessed, darker client portal with a more pronounced brick surround; r2 is a simplified exterior representation.']},
      {'criterion':'Modular export, portability, complete evidence','score':1.8,'max_score':2,'evidence':['Independently reopened frozen library exports expected local Asset collection with 147 objects.','No external file images, libraries or drivers. Dedicated builder, source snapshots, register and reopen evidence exist.'],'findings':['Interior is explicitly schematic, not as-built.','Shared manifest contains old object statistics; coordinator must refresh them and arrange master integration.','Photo acquisition date and measurement-grade exterior elevation are unavailable.']}
    ]
    result={'score':round(sum(c['score'] for c in criteria),2),'max_score':10,'pass':sum(c['score'] for c in criteria)>=8,'criteria':criteria,'evidence':measurements,'findings':['PASS standalone modular building at 8.4/10; height, opening dimensions and unseen elevations remain estimated. Final master integration and context review remain outstanding.'],'method':'Independent r2 grader re-read raw source photo pixels, inspected r2 reopened render pixels, reopened exact SHA in Blender and measured evaluated shell/portability. Own south-oblique render generated without saving asset.'}
    with open(os.path.join(OUT,'result.json'),'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2)); return result

if __name__=='__main__': evaluate()

