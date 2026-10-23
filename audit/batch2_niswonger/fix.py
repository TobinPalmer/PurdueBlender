import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
c=bpy.data.collections['Asset_niswonger_aviation_tech']
for o in c.all_objects:
 if o.name.startswith('NISW_Room157_') or o.name.startswith('NISW_Classroom157'):o.location.x-=2.2
for n in ['NISW_GroundFloor_North','NISW_GroundFloor_Hangar']:
 o=bpy.data.objects.get(n);bpy.data.objects.remove(o,do_unlink=True)
s=Path('build_niswonger_aviation_tech_attempt3.py').read_text();tree=ast.parse(s)
pts=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NISW_PTS' for t in n.targets))[:-1]
# Current local origin inferred from unchanged structural foundation bound: originalmin -1364.5977 maps -39.5978, originalminY-1258.5913 maps -29.0913.
vs=[(x+1325,y+1229.5,0) for x,y in pts];me=bpy.data.meshes.new('NISW_Official_GroundFloor');me.from_pydata(vs,[],[list(range(len(vs)))]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new('NISW_Official_GroundFloor',me);c.objects.link(o);me.materials.append(bpy.data.materials['NISW_Terrazzo_Tile_MetreScale']);mod=o.modifiers.new('Ground slab thickness','SOLIDIFY');mod.thickness=.12
for v in bpy.data.objects['NISW_Foundation_WaterTable'].data.vertices:
 if v.co.z>0:v.co.z=0
j=json.load(open('audit/batch2_niswonger/changes.json'));j['rooms'][1]['center'][0]=-29.5;j['fixes']=['Room157 shifted2.2mwest to remove partition overlap','Official polygon ground slab replaces partial rectangular slabs','Foundation upper surface lowered to0m to remove interior occlusion'];json.dump(j,open('audit/batch2_niswonger/changes.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
