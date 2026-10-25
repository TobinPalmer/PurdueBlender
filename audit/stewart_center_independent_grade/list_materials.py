import bpy
for m in bpy.data.materials:
 if any(k.lower() in m.name.lower() for k in ['stew','stone','brick','glass','limestone','roof']): print(m.name)
