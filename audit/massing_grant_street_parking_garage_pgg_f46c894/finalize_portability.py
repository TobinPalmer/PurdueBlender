import bpy
from pathlib import Path
for image in list(bpy.data.images):
    if image.source == 'FILE' and image.users == 0:
        print('remove unused image', image.name, image.filepath)
        bpy.data.images.remove(image)
for material in list(bpy.data.materials):
    if material.users == 0:
        print('remove unused material', material.name)
        bpy.data.materials.remove(material)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
