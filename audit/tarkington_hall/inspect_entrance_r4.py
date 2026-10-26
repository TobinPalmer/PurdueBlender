import bpy
for o in sorted(bpy.data.objects,key=lambda x:x.name):
 if any(k in o.name for k in ['South_Entrance_Door','South_Door','South_Portico','South_Glass']):print(o.name,tuple(round(x,2) for x in o.matrix_world.translation),tuple(round(x,2) for x in o.dimensions),o.parent.name if o.parent else None)
