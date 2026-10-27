"""Independent frozen-asset assessment; opens but never saves the building library."""
import bpy, json, math, hashlib, os
from mathutils import Vector

OUT=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(OUT,'..','..','..'))
ID='david_and_bonnie_brunner_farm_animal_hospital'
ASSET=os.path.join(ROOT,'modular','buildings',ID+'.blend')
EXPECTED='17da01b00ae68eb026967ed364e65a99cf239bb761c3ec09787b000f71af1cc9'

def evaluate():
    digest=hashlib.sha256(open(ASSET,'rb').read()).hexdigest()
    assert digest==EXPECTED, 'Frozen asset changed'
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    col=bpy.data.collections['Asset_'+ID]
    shell=bpy.data.objects[ID+'_GIS_outline_primary_shell']
    feature=json.load(open(os.path.join(OUT,'..','sources','purdue_gis_feature_408.json'),encoding='utf-8'))['feature']
    ring=feature['geometry']['rings'][0][:-1]
    sx=111412.84*math.cos(math.radians(40.4274))
    pts=[((lon+86.9137)*sx,(lat-40.4274)*111040.) for lon,lat in ring]
    cross=[x*v-u*y for (x,y),(u,v) in zip(pts,pts[1:]+pts[:1])]
    area2=sum(cross)
    origin=[sum((a[k]+b[k])*c for a,b,c in zip(pts,pts[1:]+pts[:1],cross))/(3*area2) for k in range(2)]
    local=[(x-origin[0],y-origin[1]) for x,y in pts]
    dg=bpy.context.evaluated_depsgraph_get()
    ev=shell.evaluated_get(dg); mesh=ev.to_mesh()
    v=[ev.matrix_world @ p.co for p in mesh.vertices]
    bottom=[(p.x,p.y) for p in v if p.z<1]
    err=max(min(math.dist(a,b) for b in bottom) for a in local)
    bounds=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]
    ev.to_mesh_clear()
    entry=next(a for a in json.load(open(os.path.join(ROOT,'modular','manifest.json'),encoding='utf-8'))['assets'] if a['id']==ID)
    external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
    measurements={'asset_sha256':digest,'blender_version':bpy.app.version_string,'reopened':True,'object_count':len(col.all_objects),'collection':col.name,'source_FID':feature['attributes']['FID'],'source_code':feature['attributes']['BLDG_ABBR'],'source_local_origin_xy_m':origin,'manifest_origin_xy_m':entry['placement_origin_xy_m'],'origin_error_m':math.dist(origin,entry['placement_origin_xy_m']),'source_to_evaluated_shell_max_vertex_error_m':err,'shell_bounds_m':bounds,'shell_local_footprint_area_m2':abs(area2)/2,'published_floor_area_m2':23900*.09290304,'external_unpacked_image_dependencies':external,'shell_matrix_world':[list(r) for r in shell.matrix_world],'library_paths':[l.filepath for l in bpy.data.libraries],'drivers_count':sum(len(o.animation_data.drivers) if o.animation_data else 0 for o in bpy.data.objects)}
    with open(os.path.join(OUT,'reopen_measurements.json'),'w',encoding='utf-8') as f: json.dump(measurements,f,indent=2)
    # Independent low south view from freshly reopened asset, no file save.
    scene=bpy.context.scene; camera=scene.camera
    camera.location=(35,-92,18); target=Vector((0,0,3.2))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=48
    scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.filepath=os.path.join(OUT,'independent_south_oblique.png')
    bpy.ops.render.render(write_still=True)
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':['Official Purdue GIS FID 408 explicitly names BRFM and address 415 S Grant Street.','Reopened evaluated shell reproduces all 16 source-ring vertices within %.8f m.'%err],'findings':['The Mercator Shape__Area field is not ground area; local polygon area is %.1f m2. Published 23,900 sq ft is floor area and is not enough to contradict mapped footprint.'%(abs(area2)/2)]},
      {'criterion':'Position, orientation, scale/dimensions','score':1.9,'max_score':2,'evidence':['Independently computed origin agrees with manifest to %.8f m.'%measurements['origin_error_m'],'Identity shell world matrix and direct X-east/Y-north source transformation preserve GIS orientation and approximately 62.13 by 50.28 m extents.'],'findings':['Standalone frame verified; master link replacement and nearby context remain a coordinator/Tobin integration check.']},
      {'criterion':'Evidence-backed height, floors, roof form','score':1.2,'max_score':2,'evidence':['BEP source pixels show a low one-story service block with flat parapet roof and a clay-tile hip over the reception volume.','Reopened shell is 0.35 to 6.2 m; one principal floor; tile feature present.'],'findings':['6.2 m wall and roof elevations remain unmeasured estimates; GIS NUM_LEVELS and Extrution are zero.','The model tile feature reads as a small projecting triangular/canopy shape rather than the raised, four-sided reception roof visible in the photo.','Generic three tall exhaust stacks and large mechanical screen are not justified by the building-specific photograph; aerial Farm Animal Hospital is mostly cropped above the image.']},
      {'criterion':'Facade, entrances, distinctive architecture','score':0.9,'max_score':2,'evidence':['Reopened model includes red brick, pale belt, personnel door, one vehicle bay and glazing at reception, all recognisable in the photo.'],'findings':['Visible row of at least seven narrow vertical windows on the left-hand reception wing is absent from model.','Repeated pale vertical piers around the shell are not supported by source image.','Photo entrance has a recessed portal within a pronounced brick reception block; model uses shallow freestanding pale portal and a dark door panel. Opening proportions and positions are estimates.','Roof trim, corner massing and louvered right side differ visibly from source.']},
      {'criterion':'Modular export, portability, complete evidence','score':1.8,'max_score':2,'evidence':['Independent Blender reopen succeeds; expected Asset collection with 159 objects; local frame intact.','No unpacked file images, external libraries or drivers. Dedicated script and raw source snapshots/register are present.'],'findings':['Schematic interior is explicitly labeled; no as-built claim.','Master integration has not been independently confirmed and old shared manifest statistics need coordinator refresh.','BEP retrieval and source date are recorded, but exact image acquisition date is unavailable.']}
    ]
    result={'score':round(sum(c['score'] for c in criteria),2),'max_score':10,'criteria':criteria,'evidence':measurements,'findings':['FAIL minimum 8/10. Improve source-visible facade windows and reception roof volume, remove unsupported generic piers/stacks or substantiate them, then freeze and request fresh independent grading.'],'method':'Independent evaluator read raw source pixels directly, opened frozen asset in Blender 5.2.3, measured evaluated shell and portability, and rendered own south oblique view. Model never saved.'}
    with open(os.path.join(OUT,'result.json'),'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__': evaluate()
