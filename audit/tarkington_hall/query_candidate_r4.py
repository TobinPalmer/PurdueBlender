import bpy,hashlib
from pathlib import Path
print('filepath',bpy.data.filepath,'objects',len(bpy.data.objects))
print('sample',sum(o.name.startswith('Tark_Program_Standard_Room_') for o in bpy.data.objects))
print('sha',hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest())
