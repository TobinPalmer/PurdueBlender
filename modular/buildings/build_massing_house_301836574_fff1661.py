import bpy, json, math
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'audit/phi_mu/sources/purdue_gis_fid772_raw.json'
OUT=ROOT/'modular/buildings/massing_house_301836574_fff1661.blend'
D=json.load(open(RAW,encoding='utf8'))
f=D['features'][0]
assert f['attributes']['FID']==772 and f['attributes']['BUILDING_N']=='Phi Mu'
ring=f['geometry']['rings'][0][:-1]
lat0=40.4274; lon0=-86.9137
pts=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
assert len(pts)==18
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
# Rebuild the one-object massing library in the original campus coordinate frame.
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
for col in list(bpy.data.collections):
    if col.users==0: bpy.data.collections.remove(col)
scene=bpy.context.scene
scene.name='Building_massing_house_301836574_fff1661'
asset=bpy.data.collections.new('Asset_massing_house_301836574_fff1661'); scene.collection.children.link(asset)
# Materials

def mat(name,color,rough=0.82):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    return m
brick=mat('Warm red brick',(.43,.115,.075)); brick2=mat('Brick variation',(.55,.17,.115)); mortar=mat('Dark mortar',(.28,.22,.19)); trim=mat('Painted ivory trim',(.90,.87,.79)); roofmat=mat('Slate charcoal roof',(.095,.115,.14)); glass=mat('Deep blue window glass',(.025,.075,.105),.32); door_mat=mat('Dark wood entrance',(.19,.08,.045)); foundation=mat('Foundation stone',(.36,.34,.30))
materials=[brick,brick2,mortar,trim,roofmat,glass,door_mat,foundation]
V=[]; F=[]; MI=[]
def face(coords,mi):
    ids=[]
    for c in coords: ids.append(len(V)); V.append(tuple(c))
    F.append(ids); MI.append(mi)
def box(cx,cy,cz,sx,sy,sz,mi):
    x0,x1=cx-sx/2,cx+sx/2; y0,y1=cy-sy/2,cy+sy/2; z0,z1=cz-sz/2,cz+sz/2
    a=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: face([a[i] for i in ids],mi)
def prism(poly,z0,z1,mi):
    n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],mi if i%5 else 1)
    # Fill caps; mesh ngon preserves the exact projected perimeter.
    face([(x,y,z1) for x,y in poly],mi)
    face([(x,y,z0) for x,y in reversed(poly)],mi)
def cylinder(cx,cy,z0,z1,r,mi,n=12):
    poly=[(cx+r*math.cos(2*math.pi*i/n),cy+r*math.sin(2*math.pi*i/n)) for i in range(n)]
    prism(poly,z0,z1,mi)
# Exact GIS wall perimeter, stacked main levels and modest string courses.
prism(pts,0,0.55,7)
prism(pts,0.55,4.25,0)
prism(pts,4.25,4.43,3)
prism(pts,4.43,8.2,0)
# Roof: hipped planes over approximate primary roof rectangle inside GIS envelope.
rx0,rx1=minx+1.0,maxx-1.0; ry0,ry1=miny+1.0,maxy-1.0; cx=(rx0+rx1)/2
z0=8.2; zr=13.2; inset=min((ry1-ry0)*0.22,(rx1-rx0)*0.22)
ls=(cx,ry0+inset,zr); rs=(cx,ry1-inset,zr)
face([(rx0,ry0,z0),(rx1,ry0,z0),rs,ls],4)
face([(rx1,ry0,z0),(rx1,ry1,z0),rs],4)
face([(rx1,ry1,z0),(rx0,ry1,z0),ls,rs],4)
face([(rx0,ry1,z0),(rx0,ry0,z0),ls],4)
# Fascia band around roof eaves.
box(cx,ry0,8.05,rx1-rx0,.35,.32,3); box(cx,ry1,8.05,rx1-rx0,.35,.32,3)
# Windowed exterior: repeated openings around simplified primary facades, with white surrounds.
def window(x,y,z,w=1.55,h=1.85,side='south'):
    # y is exterior plane: south-facing pieces protrude to y<wall; north to y>wall
    out=-1 if side=='south' else 1
    # dark pane, then white casing strips
    box(x,y+out*.04,z,w,.10,h,5)
    for xx in (x-w/2-.10,x+w/2+.10): box(xx,y+out*.11,z,.18,.20,h+.28,3)
    for zz in (z-h/2-.12,z+h/2+.12): box(x,y+out*.11,zz,w+.38,.20,.18,3)
    box(x,y+out*.16,z, w*.78,.10,.07,3)
# south facade, aligned to likely chapter-house frontage (bearing unverified)
front_y=miny+.06
for z in (2.35,6.2):
    for x in (cx-9,cx-5.8,cx+5.8,cx+9): window(x,front_y,z,1.65,1.85,'south')
# side-facing elevation: representative repeated windows on east and west envelope
for side_x,side in ((minx+.05,'west'),(maxx-.05,'east')):
    for yy in [miny+5,miny+11,miny+17,miny+23,miny+29,miny+35]:
        for z in (2.35,6.2):
            # side windows face east/west; make pane and simple trim with x-normal
            out=-1 if side=='west' else 1
            box(side_x+out*.04,yy,z,.10,1.45,1.85,5)
            for xx in (side_x+out*.11,):
                box(xx,yy-.83,z,.20,.16,2.08,3); box(xx,yy+.83,z,.20,.16,2.08,3)
                box(xx,yy,z-.97,.20,1.82,.16,3); box(xx,yy,z+.97,.20,1.82,.16,3)
# Central colonial portico on southern edge, shallow projection with four columns and pediment.
port_y=miny-2.0; port_w=12.4
for x in [cx-5.0,cx-1.7,cx+1.7,cx+5.0]:
    cylinder(x,port_y,0.55,7.15,.24,3)
    cylinder(x,port_y,7.12,7.34,.40,3)
box(cx,port_y,7.52,port_w,1.05,.42,3)
# Classical pediment as triangular solid.
def wedge_front(x0,x1,y,basez,peakz,depth,mi):
    # triangulated triangular-prism front/back with side caps
    a=(x0,y,basez); b=(x1,y,basez); c=(cx,y,peakz)
    a2=(x0,y+depth,basez); b2=(x1,y+depth,basez); c2=(cx,y+depth,peakz)
    face([a,b,c],mi); face([a2,c2,b2],mi)
    face([a,a2,b2,b],mi); face([b,b2,c2,c],mi); face([c,c2,a2,a],mi)
wedge_front(cx-port_w/2,cx+port_w/2,port_y-.55,7.72,9.55,.40,3)
# Main entry centered behind portico; entry side is illustrative, not georeferenced.
box(cx,front_y-.16,2.05,2.25,.22,3.15,6)
box(cx,front_y-.30,3.8,3.5,.34,.24,3)
# Four roof dormers on south slope: modeled gable fronts, cheeks, and small slate caps.
for i,x in enumerate([cx-10.5,cx-5.25,cx,cx+5.25,cx+10.5]):
    y=ry0+2.4
    base=9.0; top=11.2
    box(x,y,10.0,2.8,1.25,2.0,0)
    # pale dormer gable front toward south
    wedge_front(x-1.5,x+1.5,y-.68,10.75,11.85,.22,3)
    box(x,y-.78,10.15,1.38,.10,1.22,5)
    for xx in (x-.78,x+.78): box(xx,y-.89,10.15,.12,.18,1.42,3)
    for zz in (9.48,10.84): box(x,y-.89,zz,1.68,.18,.14,3)
    # small pitched cap polygon approximated by stacked box/triangular front
    wedge_front(x-1.72,x+1.72,y-.94,10.95,11.95,.26,4)
# Mesh into exactly one expected object in the asset collection.
mesh=bpy.data.meshes.new('Phi Mu source-backed massing mesh'); mesh.from_pydata(V,[],F); mesh.update()
obj=bpy.data.objects.new('House_301836574',mesh); asset.objects.link(obj)
for m in materials: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,MI): p.material_index=mi
obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
obj['building_name']='Phi Mu, Delta Epsilon Chapter'; obj['source_fid']=772; obj['footprint_source']='Purdue BuildingShapesZip4 FID 772'; obj['height_status']='Estimated from 1965 Debris photo; GIS NUM_LEVELS=1 conflicts'; obj['front_bearing_status']='Illustrative; not georeferenced'; obj['campus_coordinate_frame']='X east, Y north, Z up; local project approximation'
# Pack any generated data and save.
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=900; scene.render.resolution_y=700; scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('SAVED',OUT,'vertices',len(mesh.vertices),'faces',len(mesh.polygons),'bounds',minx,maxx,miny,maxy)
