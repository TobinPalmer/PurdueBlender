import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
audit=root/'audit'/'phi_kappa_psi_fid856'
urls=[
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23378/size_m/23262.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23379/size_m/23263.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23380/size_m/23264.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23381/size_m/23265.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23382/size_m/23266.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23383/size_m/23267.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23384/size_m/23268.jpg',
 'https://presenter-production.s3.us-west-1.amazonaws.com/photos/23385/size_m/23269.jpg']
roles=['front portico and pediment','front elevation duplicate angle','rear elevation with central bay','rear oblique elevation','lounge/common room interior','entry lobby and staircase','rear elevation landscape context','side view of portico, lower level and landscaping']
obj={
 'retrieved':'2026-10-27',
 'sources':[
  {'provider':'Phi Kappa Psi Indiana Delta chapter','url':'https://purdue.phikappapsi.com/contact','type':'official current chapter contact page','local_snapshot':'sources/official_chapter_contact_2026-10-27.html','relevant_fact':'Lists 1307 Tower Dr, West Lafayette, IN 47906.'},
  {'provider':'Phi Kappa Psi national fraternity','url':'https://www.phikappapsi.com/wp-content/uploads/2019/07/pages-13.pdf','type':'official national magazine PDF; The Shield of Phi Kappa Psi, Summer 2010, printed page 28','local_snapshot':'sources/national_phipsi_page174.jpg','relevant_fact':'Indiana Delta chapter report identifies its new house at 1307 Tower Drive.'},
  {'provider':'C.F. Jones Group via Project Presenter','url':'https://www.projectpresenter.com/cf-jones-group/projects/phi-kappa-psi-fraternity-at-purdue-university/30006/show','type':'construction-management company project portfolio','relevant_fact':'Completed Purdue project; source photos show front, rear and interior.'},
  {'provider':'Pennington & Company','url':'https://www.penningtonco.com/campaigns/phi-kappa-psi-purdue-university','type':'campaign/construction history','relevant_fact':'Describes new Indiana Delta chapter-house construction in Tower Acres.'},
  {'provider':'Purdue ArcGIS campus building layer','url':'https://purdueuniversity.maps.arcgis.com/','type':'GIS feature snapshot','feature_id':856,'source_crs':'EPSG:3857','local_snapshot':'sources/purdue_gis_fid856_2026-10-26.json','relevant_fact':'Address 1307 TOWER DR, owner GREEK, legacy building label Phi Kappa Tau; wall ring used for geometry.'},
  {'provider':'OpenStreetMap','url':'https://www.openstreetmap.org/way/301841257','type':'OSM building way snapshot','feature_id':301841257,'source_crs':'WGS84','local_snapshot':'sources/osm_map_2026-10-27.xml','relevant_fact':'Nearby building outline tagged generically as school; used only to compare eaves/roof outline, not as wall footprint.'},
  {'provider':'Esri World Imagery','url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer','type':'aerial image export','source_crs':'EPSG:3857','retrieved':'2026-10-27','local_snapshot':'sources/esri_aerial_1307_tower.jpg','relevant_fact':'Overhead context; acquisition date not exposed in the retrieved response.'},
  {'provider':'Tippecanoe County assessor service','url':'https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/69/query','type':'parcel assessor record','local_snapshot':'sources/tippecanoe_assessor_1307_tower.json','relevant_fact':'Address corroboration; year, grade, and area are blank/zero and not used for dimensions.'}
 ],
 'contractor_gallery_photos':[{'file':f'sources/contractor_photos/photo_{i+1}.jpg','url':u,'visual_role':roles[i],'license_or_capture_date':'not stated on project page'} for i,u in enumerate(urls)],
 'transform':'Purdue GIS Web Mercator EPSG:3857 -> inverse Web Mercator WGS84 -> repository local approximation X=(lon+86.9137)*111412.84*cos(40.4274 degrees); Y=(lat-40.4274)*111040.0; local origin at polygon area centroid.',
 'confidence':{'identity':'high','wall_plan':'high relative to campus GIS; local CRS is approximate','exterior_materials_and_major_features':'moderate-high from contractor photos','height_and_story_count':'estimated; GIS level count conflicts with photographs','interior_plan':'unverified; geometry explicitly schematic'}
}
(audit/'source_register.json').write_text(json.dumps(obj,indent=2),encoding='utf-8')
