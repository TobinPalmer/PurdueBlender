import bpy, os, json
p=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_rawls_hall']; root=bpy.data.objects['AssetRoot_rawls_hall']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
mat=bpy.data.materials['RAWL_Purdue_Red_Brick'];pr=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
brick=next(l.from_node for l in pr.inputs['Base Color'].links if l.from_node.type=='TEX_BRICK')
glass=bpy.data.materials['RAWL_CurtainWall_Glass'];gs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
base=json.load(open('audit/batch4_rawls/round5_checks.json'))
report={'asset':p,'blender_version':bpy.app.version_string,'round':6,'objects':len(c.all_objects),'mesh_objects':sum(o.type=='MESH' for o in c.all_objects),'missing_images':missing,'root_parent':root.parent.name if root.parent else None,'root_location':list(root.location),'root_scale':list(root.scale),'wall_faces':len(bpy.data.objects['RAWL_Masonry_Exterior_Walls'].data.polygons),'north_glass_quads':len(bpy.data.objects['RAWL_North_Windows_Glass'].data.polygons),'north_frame_faces':len(bpy.data.objects['RAWL_North_Windows_BronzeMullions'].data.polygons),'south_glass_quads':len(bpy.data.objects['RAWL_South_Windows_South_Glass'].data.polygons),'south_frame_faces':len(bpy.data.objects['RAWL_South_Windows_South_BronzeMullions'].data.polygons),'brick_width_m':brick.inputs['Brick Width'].default_value,'brick_course_height_m':brick.inputs['Row Height'].default_value,'brick_mortar_color':list(brick.inputs['Mortar'].default_value),'brick_mortar_size':brick.inputs['Mortar Size'].default_value,'glass_base_color':list(gs.inputs['Base Color'].default_value),'glass_transmission':gs.inputs['Transmission Weight'].default_value,'glass_roughness':gs.inputs['Roughness'].default_value,'round5_rays_reused_as_saved_geometry_ray_checks':base['rays'],'notes':'Reopened the saved blend. Render-only cuts/cameras/lights are excluded from the saved model. Round5 rays remain applicable because round6 changed materials only.'}
with open('audit/batch4_rawls/round6_checks.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='round5_rays_reused_as_saved_geometry_ray_checks'},indent=2))
