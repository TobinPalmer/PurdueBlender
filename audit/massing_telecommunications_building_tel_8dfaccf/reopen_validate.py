import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parents[2]
bid='massing_telecommunications_building_tel_8dfaccf'
audit=root/'audit'/bid
manifest=json.loads((root/'modular'/'manifest.json').read_text(encoding='utf-8-sig'))
entry=next(x for x in manifest['assets'] if x['id']==bid)
scene=bpy.context.scene
colls=[c for c in bpy.data.collections if c.name==entry['collection']]
coll=colls[0] if len(colls)==1 else None
objects=list(coll.objects) if coll else []
checks=[]
def check(name,passed,detail): checks.append({'check':name,'passed':bool(passed),'detail':detail})
check('blender_version',bpy.app.version_string.startswith('4.5.15'),bpy.app.version_string)
check('scene_identity',scene.name==entry['scene'],{'actual':scene.name,'expected':entry['scene']})
check('collection_identity_and_unique',len(colls)==1,{'matches':len(colls),'expected':entry['collection']})
check('object_count',len(objects)==entry['object_count'],{'actual':len(objects),'expected':entry['object_count']})
check('object_names',[o.name for o in objects]==entry['objects'],{'actual':[o.name for o in objects],'expected':entry['objects']})
check('object_types',all(o.type=='MESH' for o in objects),[o.type for o in objects])
check('no_external_libraries',len(bpy.data.libraries)==0,[l.filepath for l in bpy.data.libraries])
check('no_external_images',all(not im.filepath or im.packed_file for im in bpy.data.images),[im.filepath for im in bpy.data.images if im.filepath and not im.packed_file])
if objects:
 o=objects[0]; bpy.context.view_layer.update(); world=o.matrix_world
 pts=[world@v.co for v in o.data.vertices]
 bounds=[[min(getattr(p,k) for p in pts) for k in ('x','y','z')],[max(getattr(p,k) for p in pts) for k in ('x','y','z')]]
 loc=list(o.location); rot=[math.degrees(a) for a in o.rotation_euler]; scale=list(o.scale)
 check('identity_transform',all(abs(a-b)<1e-6 for a,b in zip(loc,[0,0,0])) and all(abs(a-b)<1e-6 for a,b in zip(rot,[0,0,0])) and all(abs(a-b)<1e-6 for a,b in zip(scale,[1,1,1])),{'location':loc,'rotation_degrees':rot,'scale':scale})
 checks_geo=json.loads((audit/'sources'/'purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]['geometry']['rings'][0]
 gis_xy=[]
 for lon,lat in checks_geo:
  gis_xy.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
 if math.dist(gis_xy[0],gis_xy[-1])<1e-8: gis_xy.pop()
 mesh_base=[(v.co.x,v.co.y) for v in o.data.vertices if abs(v.co.z)<1e-5]
 missing=[p for p in gis_xy if min((math.hypot(p[0]-q[0],p[1]-q[1]) for q in mesh_base),default=float('inf'))>0.0001]
 check('official_footprint_ring_vertices_present',not missing,{'source_vertices':len(gis_xy),'mesh_base_vertices':len(mesh_base),'max_tolerance_m':0.0001,'missing_vertices':missing[:5]})
 z0=min(p.z for p in pts); z1=max(p.z for p in pts)
 check('base_and_roof_elevation',abs(z0)<1e-5 and z1>9.0 and z1<10.0,{'z_min':z0,'z_max_including_equipment':z1,'estimated_shell_height_m':o.get('roof_height_estimate_m')})
 check('no_modifiers',len(o.modifiers)==0,[m.name for m in o.modifiers])
 report={'asset':str(Path(bpy.data.filepath).relative_to(root)),'reopen_app':'Blender 4.5.15 LTS','scene':scene.name,'collection':coll.name if coll else None,'object_count':len(objects),'objects':[o.name for o in objects],'mesh':{'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials],'world_bounds_m':bounds,'object_transform':{'location':loc,'rotation_degrees':rot,'scale':scale},'modifiers':[m.name for m in o.modifiers]} if objects else None,'checks':checks,'passed':all(c['passed'] for c in checks),'limitations':['Facade, window pattern, and exact entrance dimensions remain unverified from available source imagery.','GIS polygon and footprint source are map features, not structural survey.','Roof height is an estimate from class-1 LiDAR returns; tile lacks class-6 building returns.','Roof-equipment dimensions/heights are schematic proxies.']}
(audit/'reopen_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

