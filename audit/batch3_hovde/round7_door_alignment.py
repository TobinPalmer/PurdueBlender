import bpy

p = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)

# East-elevation doors were modeled edge-on: their 1.56m leaf width ran in X,
# while the entrance wall openings are in the Y-Z plane. Turn each assembly to face east.
for i in (1, 2, 3):
    for prefix in ('HOVD_Door_Bronze_', 'HOVD_Door_Transom_', 'HOVD_Door_Frame_', 'HOVD_Door_Handle_'):
        obj = bpy.data.objects[prefix + str(i)]
        obj.rotation_euler.z += 1.57079632679

# Replace each solid limestone cuboid with four reveal/frame bars and a transom rail.
for i in (1, 2, 3):
    obj = bpy.data.objects[f'HOVD_Door_Frame_{i}']
    old = obj.data
    xs = [(-.935, -.78, -2.1, 2.1), (.78, .935, -2.1, 2.1),
          (-.935, .935, -2.1, -1.95), (-.935, .935, 1.95, 2.1),
          (-.78, .78, .66, .74)]
    verts, faces = [], []
    for x0, x1, z0, z1 in xs:
        y0, y1 = -.075, .075
        b = len(verts)
        verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                      (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        faces.extend([(b,b+3,b+2,b+1),(b+4,b+5,b+6,b+7),(b,b+1,b+5,b+4),
                      (b+1,b+2,b+6,b+5),(b+2,b+3,b+7,b+6),(b+3,b,b+4,b+7)])
    mesh = bpy.data.meshes.new(f'HOVD_Door_Frame_{i}_OpenFrameMesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if old.materials:
        for mat in old.materials:
            mesh.materials.append(mat)
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)

bpy.ops.wm.save_as_mainfile(filepath=p)
print('East entrance leaves, transoms, handles, and hollow limestone frames aligned to facade openings.')
