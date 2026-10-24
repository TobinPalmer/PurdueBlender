import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/niswonger_aviation_tech.blend'))
def walk(c,depth=0):
 print(' '*depth,c.name,'hide_render',c.hide_render,'objects',len(c.objects),'children',len(c.children))
 for x in c.children: walk(x,depth+1)
walk(bpy.context.scene.collection)
for l in bpy.context.view_layer.layer_collection.children: print('LAYER',l.name,l.exclude,l.hide_viewport,l.collection.hide_render)
