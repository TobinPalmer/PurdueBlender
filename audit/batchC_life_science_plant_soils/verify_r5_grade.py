import bpy
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=f)
root=bpy.data.collections['Asset_life_science_plant_and_soils_laboratory']
def walk(c):
 yield from c.objects
 for child in c.children: yield from walk(child)
objs=list(walk(root))
print('asset',len(objs),'meshes',sum(o.type=='MESH' for o in objs))
print('frames',[o.name for o in objs if o.name=='LSPS R5 | window frame and transom detail'])
print('doors',[o.name for o in objs if o.name=='LSPS R4 | insulated seed-room door'])
print('stale boxes',[o.name for o in objs if 'R3 | cold room' in o.name])
print('material count',len({m.name for o in objs if o.type=='MESH' for m in o.data.materials if m}))
