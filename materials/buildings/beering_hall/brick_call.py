sys.path.insert(0,os.path.join(ROOT,'materials'))
import pbr_upgrade as pbr
for mn in ['Beering_Purdue_Red_Brick','Beering_Plaza_Brick_Pavers']:
 pbr.upgrade_brick(bpy.data.materials[mn],tint=(1.05,.90,.80,1),tile_m=1.1)
for o in c.all_objects:
 if o.type=='MESH' and any(m and m.name in ['Beering_Purdue_Red_Brick','Beering_Plaza_Brick_Pavers'] for m in o.data.materials):pbr.metric_uv(o,1.1)
pbr.pack_textures()
