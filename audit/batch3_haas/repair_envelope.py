import bpy
from pathlib import Path
c=bpy.data.collections['Asset_felix_haas_hall'];n='HAAS_Corrected_GIS_Wall_Envelope';o=bpy.data.objects[n]
with bpy.data.libraries.load(str(Path('audit/batch3_haas/before.blend').resolve()),link=False) as (a,b):b.objects=[n]
old=b.objects[0];o.data=old.data.copy();bpy.data.objects.remove(old,do_unlink=True)
# Source shell consists of surface envelope; destructive boolean unsuitable. Glazing retained as facade insets with unverified physical openings.
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
