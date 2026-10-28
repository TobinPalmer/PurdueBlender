import json, hashlib
from pathlib import Path
A=Path(__file__).parent
ROOT=A.parents[1]
asset=ROOT/'modular/buildings/massing_house_301836574_fff1661.blend'
fresh=json.loads((A/'fresh_open_validation.json').read_text())
geo=json.loads((A/'geometry_reconciliation.json').read_text())
def file_info(rel):
 p=A/rel
 return {'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
packet={
 'building':'Phi Mu','feature_id':772,'stable_asset_id':'massing_house_301836574_fff1661',
 'asset_path':'modular/buildings/massing_house_301836574_fff1661.blend',
 'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'status':'awaiting_independent_grade','independent_grade':None,'finished':False,
 'retrieved_utc_date':'2026-10-28','provider':'Purdue University shared ArcGIS BuildingShapesZip4 FeatureServer layer 0',
 'identity_attributes':{k:v for k,v in json.loads((A/'purdue_gis_fid772_2026-10-28_4326.json').read_text())['features'][0]['attributes'].items() if k in ['FID','BUILDING_N','BLDG_ABBR','OTHER_ABBR','OWNER','ADDRESS','NUM_LEVELS','Extrution','Shape__Area','Shape__Length','GlobalID']},
 'identity_resolution':{'result':'GIS name and address agree with Phi Mu Delta Epsilon chapter page for 201 Waldron Street.','conflict_found':False},
 'sources':[
  {'provider':'Purdue University ArcGIS','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson','purpose':'Layer metadata; native spatial reference EPSG:102100/latestWkid 3857.'},
  {'provider':'Purdue University ArcGIS','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D772&outFields=*&returnGeometry=true&outSR=4326&f=pjson','purpose':'Exact feature identity and footprint; queried as EPSG:4326.'},
  {'provider':'Purdue University ArcGIS','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D772&outFields=*&returnGeometry=true&outSR=3857&f=pjson','purpose':'Native projected feature geometry and Shape__Area / Shape__Length comparison.'},
  {'provider':'Phi Mu Delta Epsilon Purdue chapter','url':'https://purdue.phimu.org/about','purpose':'Official identity and chapter address (201 Waldron Street).'},
  {'provider':'C.M. Kelham WordPress blog','url':'https://cmkelham.wordpress.com/2010/08/09/phi-mu-pink-letters-201/','purpose':'2010 chapter-specific exterior photo; clearly documents one visible facade only.'},
  {'provider':'C.M. Kelham WordPress media','url':'https://cmkelham.wordpress.com/wp-content/uploads/2010/08/img003.jpg','purpose':'Saved property-specific exterior image; red brick, white pediment/cornice, columns, tall window bays, centered letters.'},
  {'provider':'Waze','url':'https://www.waze.com/live-map/directions/phi-mu-sorority-waldron-st-201-west-lafayette?to=place.w.178979220.1789661131.4902948','purpose':'Address cross-check only; low-resolution listing photo not used for fine facade details.'}
 ],
 'source_files':[
  file_info('purdue_gis_fid772_2026-10-28_4326.json'),file_info('purdue_gis_fid772_2026-10-28_3857.json'),
  file_info('purdue_gis_layer_0_metadata_2026-10-28.json'),file_info('source_phi_mu_blog_page.html'),
  file_info('source_phi_mu_purdue_2010.jpg'),file_info('source_waze_listing_photo.jpg'),
  file_info('source_purdue_panhellenic_phi_mu.jpg')
 ],
 'geometry_reconciliation':geo,
 'method_and_edits':[
  'Replaced the starter approximate 15-vertex bottom outline with the official 18-vertex FID 772 ring transformed from EPSG:4326 using the project README local approximation.',
  'Rebuilt the wall mass with red-brown brick, light cornice/pediment, portico columns, door and window assemblies; added a dark simple gable roof and centered hand-built Phi Mu badge based only on clearly visible 2010 facade features.',
  'Added an interpretative second window level at coordinator direction. It is not established by the 2010 crop and conflicts with GIS NUM_LEVELS=1; keep this prominent in review.',
  'Modeled ridge at 9.4m as an estimate. GIS Extrution=12 has undocumented units and is not claimed as measured height.',
  'No source-derived interior geometry is represented; no campus placement check or orientation survey was performed.'
 ],
 'before_after':{
  'starter':{'asset_sha256':'unrecorded before builder overwrite','mesh_vertices':30,'mesh_faces':41,'bounds_m':[27.0037,40.8627,16.0],'outline_vertices':15,'outline_hausdorff_from_source_m':geo['starter_geometry']['symmetric_boundary_hausdorff_m']},
  'revised':{'asset_sha256':fresh['asset_sha256'],'mesh_vertices':fresh['mesh_vertex_count'],'mesh_faces':fresh['mesh_face_count'],'full_object_bounds_m':fresh['mesh_dimensions_xyz_m'],'footprint_boundary_hausdorff_from_source_m':0.0,'material_count':fresh['material_count']}
 },
 'fresh_open_validation':fresh,
 'evidence_images':['fresh_open_exterior.png','fresh_open_top.png','exterior_preview.png','top_preview.png','exterior_rear_oblique.png','footprint_overlay.png'],
 'limitations':['Exterior photo is from 2010 and is cropped; current facade/roof condition may differ.','Only one facade is directly documented; compass orientation and unseen sides remain unverified.','Two-level reading is interpretative and conflicts with GIS NUM_LEVELS=1.','Ridge height and roof profile are estimates; GIS Extrution=12 units are undocumented.','No source-derived interior plan or verified room layout is available.','Source footprint conversion uses project local approximation and does not independently verify absolute campus placement.'],
 'grade':{'status':'pending','score':None,'independent_reviewer':None}
}
(A/'evidence.json').write_text(json.dumps(packet,indent=2),encoding='utf-8')
print('Wrote evidence.json with asset SHA256',packet['asset_sha256'])
