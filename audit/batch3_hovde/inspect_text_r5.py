import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for o in bpy.context.scene.objects:
 if o.type=='FONT' or any(k in o.name.lower() for k in ['sign','letter','inscription','name']): print(o.name,o.type, getattr(getattr(o.data,'body',None),'__str__',lambda:'')(),tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),o.parent.name if o.parent else '-')
