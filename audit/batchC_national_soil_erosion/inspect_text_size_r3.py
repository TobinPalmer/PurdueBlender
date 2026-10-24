import bpy
for o in bpy.data.objects:
    if o.type=='FONT' and ('entrance sign' in o.name or 'address plaque' in o.name):
        bpy.context.view_layer.update();print(o.name,o.data.body,'size',o.data.size,'dimensions',tuple(o.dimensions),'loc',tuple(o.location))
