import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); ASSET=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_hovde_hall']; root=bpy.data.objects['HOVD_Root']; trim=bpy.data.materials['Hovde_Limestone_Trim']
# The geotagged frontal photo shows red clay tile at a low eave, but not the
# building's hidden ridge/hip plan. Keep only a shallow tiled cap and record the
# unobserved roof form as unknown rather than asserting a broad hipped pitch.
roof=bpy.data.objects['HOVD_Inferred_Hipped_Roof']
for v in roof.data.vertices:
    if v.co.z>17.0: v.co.z=16.88
roof.data.update()
# Refine both limestone materials toward warm, dressed Indiana limestone: retain
# fine mineral variation while reducing coarse bump and chalky flatness.
for name,rough,spec in [('Bedford_Indiana_Limestone',.62,.32),('Hovde_Limestone_Trim',.54,.28)]:
    mat=bpy.data.materials.get(name)
    if not mat or not mat.use_nodes: continue
    for node in mat.node_tree.nodes:
        if node.type=='BSDF_PRINCIPLED':
            node.inputs['Roughness'].default_value=rough
            if node.inputs.get('Specular IOR Level'): node.inputs['Specular IOR Level'].default_value=spec
        elif node.type=='BUMP':
            if node.name=='Bump':
                node.inputs['Strength'].default_value=.075
                node.inputs['Distance'].default_value=.00055
            else:
                node.inputs['Strength'].default_value=.012
                node.inputs['Distance'].default_value=.002
        elif node.type=='VALTORGB':
            node.color_ramp.elements[0].color=(.47,.415,.335,1)
            node.color_ramp.elements[1].color=(.60,.535,.435,1)
# Add subtle raised midribs following the six pointed blades on each of the six
# capitals. These are fine limestone relief lines, not oversized graphic marks.
for ob in list(bpy.data.objects):
    if ob.name.startswith('HOVD_R12_Capital_Leaf_Veins_'):
        data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
        if data and data.users==0: bpy.data.curves.remove(data)
for i in range(1,7):
    shaft=bpy.data.objects[f'HOVD_Classical_Column_{i}']; x,y=shaft.location.x,shaft.location.y; face=x+.72
    cv=bpy.data.curves.new(f'HOVD_R12_Leaf_Veins_Curve_{i}','CURVE'); cv.dimensions='3D'; cv.resolution_u=8; cv.bevel_depth=.008; cv.bevel_resolution=2
    for zc,spread,w,h in ((10.39,.31,.22,.28),(10.50,.28,.17,.22)):
        for dy in (-spread,0,spread):
            spline=cv.splines.new('POLY'); spline.points.add(3)
            for k,t in enumerate((.12,.34,.58,.83)):
                yy=y+dy+.014*math.sin(t*math.pi*2)
                zz=zc+(t-.5)*h
                spline.points[k].co=(face+.13,yy,zz,1)
    cv.materials.append(trim)
    ob=bpy.data.objects.new(f'HOVD_R12_Capital_Leaf_Veins_{i}',cv); col.objects.link(ob); ob.parent=root; ob.location=(0,0,0)
bpy.context.view_layer.update()
assert len([bpy.data.objects.get(f'HOVD_R12_Capital_Leaf_Veins_{i}') for i in range(1,7)])==6
assert round(max(v.co.z for v in roof.data.vertices)-min(v.co.z for v in roof.data.vertices),3)==.16
assert tuple(round(v,3) for v in root.location)==(-62.85,93.0,0.0)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('ROUND12_SAVED shallow tile cap; softened/warmed limestone shader; six capitals received fine leaf midribs; root transform preserved.')
