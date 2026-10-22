import bpy,json,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');m=json.loads((p/'modular/manifest.json').read_text());out={}
for id in ['elliott_hall_of_music','knoy_hall','bell_tower']:
 a=next(a for a in m['assets'] if a['id']==id);bpy.ops.wm.open_mainfile(filepath=str(p/'modular'/a['file']));c=bpy.data.collections[a['collection']];out[id]={'count':len(c.all_objects),'objects':[o.name for o in c.all_objects],'materials':[{'name':x.name,'color':list(x.diffuse_color)} for x in bpy.data.materials]}
(p/'audit/finishing_north/inspection.json').write_text(json.dumps(out,indent=2))
