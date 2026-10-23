import bpy,math,json
from pathlib import Path
c=bpy.data.collections['Asset_felix_haas_hall'];m=bpy.data.materials.new('HAAS_GooglePhotos_RedClayTiles_estimated');m.use_nodes=True;m.diffuse_color=(.26,.075,.035,1);nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.7
tex=nt.nodes.new('ShaderNodeTexCoord');brick=nt.nodes.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.3;brick.inputs['Row Height'].default_value=.22;brick.inputs['Mortar Size'].default_value=.008;brick.inputs['Color1'].default_value=(.32,.085,.035,1);brick.inputs['Color2'].default_value=(.17,.035,.015,1);brick.inputs['Mortar'].default_value=(.09,.035,.02,1);nt.links.new(tex.outputs['Object'],brick.inputs['Vector']);nt.links.new(brick.outputs['Color'],p.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.015;bump.inputs['Strength'].default_value=.4;nt.links.new(brick.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
def roof(name,x0,x1,y0,y1,z,ridge):
 # hipped rectangular roof, no invented dormers
 inset=min(x1-x0,y1-y0)/2
 v=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]
 if (y1-y0)>(x1-x0):v += [((x0+x1)/2,y0+inset,ridge),((x0+x1)/2,y1-inset,ridge)];f=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)]
 else:v += [(x0+inset,(y0+y1)/2,ridge),(x1-inset,(y0+y1)/2,ridge)];f=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(m);o['height_status']='eave11.7m ridge14m estimated; red hip morphology Google Maps parent photographic review 2026-10-23'
roof('HAAS_Photo_Main_Hipped_Roof',-26.5,2.5,-26.3,27,11.7,14)
roof('HAAS_Photo_Entrance_Hipped_Roof',2.25,13.3,-12.3,12.9,11.7,13.2)
# Existing cupola stays visible above newly inferred roof but its base now aligned.
for o in c.all_objects:
 if o.name.startswith('HAAS_Cupola_'):o.location.z+=2.3
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/final_count.json').write_text(json.dumps({'count':len(c.all_objects),'roof_heights_estimated':True}))
