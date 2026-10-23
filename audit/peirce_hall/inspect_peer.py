import bpy,json
from pathlib import Path
p=Path(r'modular/buildings/felix_haas_hall.blend').resolve()
with bpy.data.libraries.load(str(p),link=False) as (src,dst):
 print('scenes',src.scenes,'colls',src.collections,'objects',len(src.objects))
 dst.collections=src.collections[:]
 dst.scenes=src.scenes[:]
for c in bpy.data.collections:
 print('C',c.name,'objs',len(c.objects),'children',[x.name for x in c.children],'props',[(k,c[k]) for k in c.keys()])
 for o in list(c.objects)[:3]: print(' O',o.name,o.type,list(o.location),list(o.dimensions))
for s in bpy.data.scenes: print('SCENE',s.name,'root children',[c.name for c in s.collection.children],'objects',len(s.objects))
