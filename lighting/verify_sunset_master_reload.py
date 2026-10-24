import bpy, json, os
scene=bpy.context.scene
cloud=scene.objects.get('Campus_Sunset_CloudBanks');dome=scene.objects.get('Campus Sunset Sky Dome')
libs=[bpy.path.abspath(l.filepath) for l in bpy.data.libraries]
missing=[p for p in libs if not os.path.exists(p)]
placements=[o for o in bpy.data.objects if o.name.startswith('Placement_')]
cams=list(bpy.data.cameras)
world_nodes=scene.world.node_tree.nodes if scene.world and scene.world.use_nodes else []
report={'scene':scene.name,'scene_objects':len(scene.objects),'libraries':len(libs),'missing_libraries':len(missing),'placement_markers':len(placements),'cloud':bool(cloud),'cloud_faces':len(cloud.data.polygons) if cloud else 0,'cloud_puffs':cloud.get('cloud_bank_count',0) if cloud else 0,'sky_dome':bool(dome),'world':scene.world.name if scene.world else None,'camera_count':len(cams),'min_camera_clip_end':min((c.clip_end for c in cams),default=0),'camera_ray_gradient':any(n.type=='NEW_GEOMETRY' for n in world_nodes) and any(n.type=='LIGHT_PATH' for n in world_nodes),'time':scene.get('campus_time')}
print('RELOAD_VALIDATION',json.dumps(report),flush=True)
if missing or len(libs)!=1937 or len(placements)!=39 or not cloud or dome or len(cloud.data.polygons)==0 or not report['camera_ray_gradient']:
 raise RuntimeError('Reload validation failed')
