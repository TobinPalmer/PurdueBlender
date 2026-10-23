import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_hovde_hall']
# Build facade wall mesh with through openings at the existing modeled glazing cadence.
def facade(name):
    o=bpy.data.objects[name]; old=o.data; mat=old.materials[0] if old.materials else None
    # wall-centered local coordinates
    xs=(-.35,.35); ys=(-35.5,35.5); zlo=-8.25; zhi=8.25
    win_centers=[-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30]
    win_half=.97
    # Window openings are the extents of the existing 1.94 x 2.16 m panes.
    zintervals=[(2.6-1.08-8.25,2.6+1.08-8.25),(6.4-1.08-8.25,6.4+1.08-8.25),(10.5-1.08-8.25,10.5+1.08-8.25),(14.6-1.08-8.25,14.6+1.08-8.25)]
    boxes=[]
    # full-height masonry piers between successive window bays and at ends
    intervals=[]; cursor=ys[0]
    for y in win_centers:
        a,b=y-win_half,y+win_half
        if a>cursor: intervals.append((cursor,a))
        cursor=b
    if cursor<ys[1]: intervals.append((cursor,ys[1])
    )
    for a,b in intervals: boxes.append((xs[0],xs[1],a,b,zlo,zhi))
    # masonry spandrels below/between/above openings in each window bay
    for y in win_centers:
        ya,yb=y-win_half,y+win_half; cursor=zlo
        for za,zb in zintervals:
            if za>cursor: boxes.append((xs[0],xs[1],ya,yb,cursor,za))
            cursor=zb
        if cursor<zhi: boxes.append((xs[0],xs[1],ya,yb,cursor,zhi))
    verts=[]; faces=[]
    for x0,x1,y0,y1,z0,z1 in boxes:
        b=len(verts); verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        faces.extend([(b+0,b+3,b+2,b+1),(b+4,b+5,b+6,b+7),(b+0,b+1,b+5,b+4),(b+1,b+2,b+6,b+5),(b+2,b+3,b+7,b+6),(b+3,b+0,b+4,b+7)])
    mesh=bpy.data.meshes.new(name+'_OpeningsMesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    if mat: mesh.materials.append(mat)
    o.data=mesh; o.location=(10.45 if name.endswith('East') else -10.45,0,8.25)
    if old.users==0: bpy.data.meshes.remove(old)
    print(name,'masonry-boxes',len(boxes),'window openings',len(win_centers)*len(zintervals))
for n in ('HOVD_Wall_East','HOVD_Wall_West'): facade(n)
# Recess every modeled ribbon glazing panel into wall thickness; retain current repeated layout.
for o in c.all_objects:
    if o.name.startswith('HOVD_Win_E_'): o.location.x=10.45
    elif o.name.startswith('HOVD_Win_W_'): o.location.x=-10.45
# Sash is a single joined mesh; move its facade-side vertices inward by 0.25 m while retaining detail.
sash=bpy.data.objects.get('HOVD_Window_Sash_Detail')
if sash:
    for v in sash.data.vertices:
        if v.co.x>9.9: v.co.x-=.25
        elif v.co.x< -9.9: v.co.x+=.25
    print('Sash recessed vertex bounds', min(v.co.x for v in sash.data.vertices), max(v.co.x for v in sash.data.vertices))
# Further reduce the portico canopy/pediment span and column spacing to reveal more adjacent window bays.
for name,factor in [('HOVD_Portico_Entablature',.84),('HOVD_Portico_Cornice',.84),('HOVD_Portico_Pediment_Base',.90),('HOVD_Portico_Pediment_Crown',.90)]:
    o=bpy.data.objects[name]; o.scale.x*=factor
for i in range(1,7):
    for prefix in ('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_','HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_'):
        o=bpy.data.objects.get(prefix+str(i))
        if o: o.location.y=-.255+(o.location.y+.255)*.84
# Save canonical asset only; master placement/root untouched.
bpy.ops.wm.save_as_mainfile(filepath=p)
print('ROUND6 saved',p,'root',tuple(bpy.data.objects['HOVD_Root'].location),tuple(bpy.data.objects['HOVD_Root'].rotation_euler))
