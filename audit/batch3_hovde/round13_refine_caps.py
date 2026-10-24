import bpy, math
from pathlib import Path

PROJECT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=PROJECT/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_hovde_hall']
root=bpy.data.objects['HOVD_Root']
stone=bpy.data.materials['Hovde_Limestone_Trim']

# Replace the faceted round-11 leaf panels with gently sculpted, smooth leaf
# blades. The frontal 2016 photograph supports acanthus-like foliage at the
# six portico capitals; the model keeps the carving shallow because no
# close-up construction detail is available.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('HOVD_R11_Corinthian_Acanthus_Leaves_',
                           'HOVD_R12_Capital_Leaf_Veins_',
                           'HOVD_R13_Corinthian_Acanthus_Leaves_',
                           'HOVD_R13_Capital_Midribs_')):
        data=ob.data
        bpy.data.objects.remove(ob,do_unlink=True)
        if data and data.users==0:
            if data.bl_rna.identifier=='Mesh': bpy.data.meshes.remove(data)
            elif data.bl_rna.identifier=='Curve': bpy.data.curves.remove(data)

def make_leaf(v, f, xface, yc, zc, width, height):
    # Rows create a soft lanceolate contour with restrained side lobes;
    # seven columns form a shallow domed carving around a raised midrib.
    ts=(0.0,.07,.15,.23,.31,.39,.47,.55,.63,.71,.79,.87,.94,1.0)
    taper=(.015,.30,.52,.70,.84,.94,1.0,.98,.92,.84,.72,.57,.36,.015)
    cols=(-1.0,-.68,-.36,0,.36,.68,1.0)
    start=len(v); front=[]; back=[]
    for i,(t,fac) in enumerate(zip(ts,taper)):
        z=zc+(t-.5)*height
        for s in cols:
            edge_lobe=(.012*math.sin(2*math.pi*(t*3.0+.08))*math.sin(math.pi*t)) if abs(s)>.99 else 0.0
            y=yc+s*(width*fac*.5+edge_lobe)
            dome=.011 + .076*(1-abs(s)**1.55)*math.sin(math.pi*t)
            shallow_fold=.004*math.sin(t*math.pi*6)*abs(s)
            front.append((xface+dome+shallow_fold,y,z))
            back.append((xface-.038,y,z))
    v.extend(front);v.extend(back)
    rows=len(ts);cols_n=len(cols);back_start=start+rows*cols_n
    for j in range(rows-1):
        for k in range(cols_n-1):
            a=start+j*cols_n+k
            f.append((a,a+1,a+cols_n+1,a+cols_n))
            a=back_start+j*cols_n+k
            f.append((a,a+cols_n,a+cols_n+1,a+1))
    for j in range(rows-1):
        for k in (0,cols_n-1):
            a=start+j*cols_n+k;b=back_start+j*cols_n+k
            f.append((a,b,b+cols_n,a+cols_n))
    for k in range(cols_n-1):
        a=start+k;b=back_start+k
        f.append((a,a+1,b+1,b))
        a=start+(rows-1)*cols_n+k;b=back_start+(rows-1)*cols_n+k
        f.append((a,b,b+1,a+1))

for i in range(1,7):
    shaft=bpy.data.objects[f'HOVD_Classical_Column_{i}']
    x,y=shaft.location.x,shaft.location.y
    xface=x+.72
    verts=[];faces=[]
    for zc,spread,w,h in ((10.39,.31,.22,.28),(10.50,.28,.17,.22)):
        for dy in (-spread,0,spread):
            make_leaf(verts,faces,xface,y+dy,zc,w,h)
    mesh=bpy.data.meshes.new(f'HOVD_R13_AcanthusMesh_{i}')
    mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(stone)
    for poly in mesh.polygons: poly.use_smooth=True
    ob=bpy.data.objects.new(f'HOVD_R13_Corinthian_Acanthus_Leaves_{i}',mesh)
    col.objects.link(ob);ob.parent=root;ob.location=(0,0,0)
    smooth=ob.modifiers.new('Softly eased limestone carving','SUBSURF')
    smooth.subdivision_type='CATMULL_CLARK';smooth.levels=1;smooth.render_levels=1
    ob['evidence']='Shallow smooth leaf relief; acanthus-like capital foliage visible in Hovde exterior photo (2016 reference). Fine carving geometry remains interpretive.'

    # Photo-supported center ridges only. Avoid small cross-veins or corner
    # volutes that cannot be resolved in the reference image.
    cv=bpy.data.curves.new(f'HOVD_R13_Capital_Midrib_{i}','CURVE')
    cv.dimensions='3D';cv.resolution_u=12;cv.bevel_depth=.0048;cv.bevel_resolution=3
    for zc,spread,w,h in ((10.39,.31,.22,.28),(10.50,.28,.17,.22)):
        for dy in (-spread,0,spread):
            sp=cv.splines.new('BEZIER');sp.bezier_points.add(2)
            for bp,t in zip(sp.bezier_points,(.19,.53,.84)):
                bp.co=(xface+.091,y+dy,zc+(t-.5)*h)
                bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    cv.materials.append(stone)
    vein=bpy.data.objects.new(f'HOVD_R13_Capital_Midribs_{i}',cv)
    col.objects.link(vein);vein.parent=root;vein.location=(0,0,0)
    vein['evidence']='Subtle midrib relief on source-supported acanthus-like foliage; leaf vein layout is interpretive.'

bpy.context.view_layer.update()
root_loc=tuple(round(v,4) for v in root.location)
root_rot=tuple(round(v,6) for v in root.rotation_euler)
assert root_loc==(-62.85,93.0,0.0),root_loc
assert len([o for o in col.objects if o.name.startswith('HOVD_R13_Corinthian_Acanthus_Leaves_')])==6
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R13 capitals saved; root retained:',root_loc,root_rot)
