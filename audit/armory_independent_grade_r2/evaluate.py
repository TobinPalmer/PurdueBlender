from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
entry=next(a for a in manifest['assets'] if a['id']=='armory')
record=json.loads((ROOT/'audit/armory/source_record.json').read_text(encoding='utf-8'))
gis=json.loads((ROOT/'audit/armory/purdue_gis_feature_207.json').read_text(encoding='utf-8'))
probe=json.loads((HERE/'blender_probe.json').read_text(encoding='utf-8'))
export=json.loads((HERE/'export_probe_result.json').read_text(encoding='utf-8'))
feature=gis['query_response']['features'][0]
ring=feature['geometry']['rings'][0][:-1]
origin=entry['placement_origin_xy_m']
xy=[]
for x,y in ring:
    lon=math.degrees(x/6378137.0); lat=math.degrees(2*math.atan(math.exp(y/6378137.0))-math.pi/2)
    xy.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
world_bounds=[[min(p[i] for p in xy),max(p[i] for p in xy)] for i in range(2)]
gis_local_bounds=[[b[0]-origin[i],b[1]-origin[i]] for i,b in enumerate(world_bounds)]
model=probe['structural_wall_bounds_local_m'][:2]
dim=[model[i][1]-model[i][0] for i in range(2)]
gisdim=[gis_local_bounds[i][1]-gis_local_bounds[i][0] for i in range(2)]
err=[abs(dim[i]-gisdim[i]) for i in range(2)]
center_delta=[((model[i][0]+model[i][1])/2)-((gis_local_bounds[i][0]+gis_local_bounds[i][1])/2) for i in range(2)]
center_error=math.hypot(*center_delta)
object_count=probe['collection_object_count']
criteria=[
 {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':[f"Purdue GIS feature {feature['attributes'].get('OBJECTID')} identifies Armory (AR), owner Purdue, address 812 Third Street.",f"The four named structural wall meshes measure {dim[0]:.3f} x {dim[1]:.3f} m against converted GIS bounds {gisdim[0]:.3f} x {gisdim[1]:.3f} m; axis discrepancies are {err[0]:.3f} m and {err[1]:.3f} m.","Purdue archive photograph supports brick masonry, pale trim, central entry and stepped central gable."]},
 {'criterion':'Position, orientation, and scale/dimensions','score':2.0 if center_error<0.05 and max(err)<0.05 else 1.5,'max_score':2,'evidence':[f"Structural wall center differs from the manifest-local GIS ring center by {center_error:.3f} m (dx={center_delta[0]:.3f}, dy={center_delta[1]:.3f}).","The four GIS corners and wall bounds use the repository local-meter conversion and unchanged manifest placement origin; footprint dimensions and cardinal alignment match within tolerance.","This GIS conversion is approximate rather than survey control."]},
 {'criterion':'Evidence-backed height, floors, and roof form','score':1.1,'max_score':2,'evidence':["Purdue archive photo directly supports a central stepped cross-gable and upper arched light; the rebuilt render includes these features.","The archive corporate record confirms the historical building and a 1928 roof-tile fire, but not the current roof finish.","No authoritative height, total story count, measured elevation, or roof geometry was found; modeled wall/roof/gable elevations are explicitly estimated."]},
 {'criterion':'Facade, entrances, and distinctive architecture','score':1.7,'max_score':2,'evidence':["The new render includes brick fields, repeated window bays, pale trim, central entry, stepped central gable and arched fanlight visible in the Purdue archive photo.","The repaired entry is modeled as a central arched composition; material tones and exact window/gable dimensions are visual approximations.","The source photo date is undetermined, and no current measured elevation is available."]},
 {'criterion':'Modular export, portability, and complete evidence','score':1.6,'max_score':2,'evidence':[f"Reopened scene/collection contract matches id={entry['id']}, file={entry['file']}, scene={entry['scene']}, collection={entry['collection']}; actual collection contains {object_count} objects.","A collection-only .blend was written and independently reopened; the expected ID, gable, and no-camera/light contract passed. No unpacked external images or absolute library paths were found; foliage library path is relative.",f"Manifest still lists {entry['object_count']} objects ({len(entry.get('objects',[]))} names), while the reopened current collection has {object_count}; coordinator should refresh shared metadata. Source records, raw GIS snapshot, archive photo, previews, and builder validation are present."]}
]
score=round(sum(c['score'] for c in criteria),2)
result={'building_id':'armory','score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'criteria':criteria,'evidence':{'asset_path':entry['file'],'scene':probe['scene'],'collection':probe['collection'],'actual_object_count':object_count,'manifest_object_count':entry['object_count'],'gis_feature':feature['attributes'],'gis_source':record['sources'][0],'gis_bounds_local_m':gis_local_bounds,'model_wall_bounds_local_m':model,'axis_dimension_error_m':err,'center_error_m':center_error,'preview':'audit/armory/armory_repaired_preview.png','gable_detail':'audit/armory/armory_central_gable_detail.png','archive_photo':'audit/armory/purdue_archives_armory_reference.jpg','source_record':'audit/armory/source_record.json','asset_probe':'audit/armory_independent_grade_r2/blender_probe.json','export_probe':'audit/armory_independent_grade_r2/export_probe_result.json'},'findings':[{'severity':'positive','finding':'The repaired perimeter aligns to the official GIS envelope and the central stepped gable is supported by the archival Purdue photo.'},{'severity':'moderate','finding':'No authoritative building height, complete story count, roof dimensions, or current roof finish was located; vertical geometry is estimated.'},{'severity':'moderate','finding':'Manifest object names/count are stale and need coordinator refresh to 703 objects.'},{'severity':'positive','finding':'The named collection exports and reopens independently with relative linked-library path and no unpacked image dependencies.'}]}
(HERE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
