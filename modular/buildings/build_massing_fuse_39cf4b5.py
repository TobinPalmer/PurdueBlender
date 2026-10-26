import bpy, math, os
from mathutils import Vector
ROOT = os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_fuse_39cf4b5.blend')
COLL = bpy.data.collections['Asset_massing_fuse_39cf4b5']; BASE = bpy.data.objects['FUSE']; PREFIX='FUSE_R1_'
for o in list(COLL.objects):
    if o.name.startswith(PREFIX): bpy.data.objects.remove(o, do_unlink=True)

def mat(name,color,rough=0.7,metallic=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    return m
brick=mat('FUSE_R1_Brick_Warm_Red',(0.42,0.105,0.065)); panel=mat('FUSE_R1_Light_Metal_Panel',(0.72,0.73,0.69),0.48); glass=mat('FUSE_R1_Window_Glass_BlueGray',(0.055,0.13,0.17),0.22,0.18); frame=mat('FUSE_R1_Window_Frame_Dark_Bronze',(0.095,0.09,0.075),0.4,0.35); store=mat('FUSE_R1_Storefront_Glass',(0.025,0.09,0.115),0.18,0.2); roof=mat('FUSE_R1_Roof_Membrane',(0.13,0.14,0.14),0.9); quad=mat('FUSE_R1_Courtyard_Green',(0.18,0.29,0.13),0.92); signmat=mat('FUSE_R1_Sign_Amber',(0.92,0.31,0.055),0.42,0.08); concrete=mat('FUSE_R1_Basement_Concrete',(0.32,0.34,0.34),0.85)
# Get the legacy massing shell bounds. Existing footprint and 16 m height are retained as estimates.
bpy.context.view_layer.update(); bb=[BASE.matrix_world@Vector(c) for c in BASE.bound_box]; x0=min(v.x for v in bb); x1=max(v.x for v in bb); y0=min(v.y for v in bb); y1=max(v.y for v in bb); z0=min(v.z for v in bb); z1=max(v.z for v in bb); cx=(x0+x1)/2; cy=(y0+y1)/2
batches={}
def add_box(material,center,size):
    vs,fs=batches.setdefault(material,([],[])); x,y,z=center; sx,sy,sz=[v/2 for v in size]; k=len(vs)
    vs.extend([(x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),(x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)])
    fs.extend([(k+0,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k+0,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k+0,k+4,k+7)])
# Courtyard opening: retain ground-level retail podium, cut the documented interior quad from upper floors.
retail_h=3.15; court_w,court_d=23.0,21.0; cut_mesh=bpy.data.meshes.new(PREFIX+'CutterMesh'); cut_mesh.from_pydata([(-court_w/2,-court_d/2,-0.5),(court_w/2,-court_d/2,-0.5),(court_w/2,court_d/2,-0.5),(-court_w/2,court_d/2,-0.5),(-court_w/2,-court_d/2,0.5),(court_w/2,-court_d/2,0.5),(court_w/2,court_d/2,0.5),(-court_w/2,court_d/2,0.5)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
cutter=bpy.data.objects.new(PREFIX+'TEMP_Cutter',cut_mesh); COLL.objects.link(cutter); cutter.location=(cx,cy,(retail_h+z1+2.0)/2); cutter.dimensions=(court_w,court_d,z1-3.15+2); bpy.context.view_layer.objects.active=cutter; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=BASE.modifiers.new(PREFIX+'Courtyard_Opening_Estimated','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cutter
bpy.context.view_layer.objects.active=BASE
try: bpy.ops.object.modifier_apply(modifier=mod.name)
except Exception as e: print('BOOLEAN_WARNING',repr(e))
bpy.data.objects.remove(cutter,do_unlink=True)
# Street-facing podium and upper apartment window rhythm, schematic due unavailable elevations.
eps=0.16
for axis,fixed,lo,hi,outward in [('y',y0,x0,x1,-1),('y',y1,x0,x1,1),('x',x0,y0,y1,-1),('x',x1,y0,y1,1)]:
    length=hi-lo
    if axis=='y':
        add_box(brick,((lo+hi)/2,fixed+outward*eps,retail_h/2),(length,0.22,retail_h)); add_box(store,((lo+hi)/2,fixed+outward*(eps+0.13),1.72),(length*0.77,0.10,2.15))
        # A clearly legible double-leaf entry interrupts the retail glazing at each street elevation.
        entry_t=(lo+hi)/2; door_y=fixed+outward*(eps+0.19)
        add_box(frame,(entry_t,door_y,1.10),(1.65,0.14,2.25)); add_box(glass,(entry_t,door_y+outward*0.09,1.10),(1.42,0.07,2.00)); add_box(frame,(entry_t,door_y+outward*0.14,1.10),(0.055,0.04,2.0))
    else:
        add_box(brick,(fixed+outward*eps,(lo+hi)/2,retail_h/2),(0.22,length,retail_h)); add_box(store,(fixed+outward*(eps+0.13),(lo+hi)/2,1.72),(0.10,length*0.77,2.15))
        entry_t=(lo+hi)/2; door_x=fixed+outward*(eps+0.19)
        add_box(frame,(door_x,entry_t,1.10),(0.14,1.65,2.25)); add_box(glass,(door_x+outward*0.09,entry_t,1.10),(0.07,1.42,2.00)); add_box(frame,(door_x+outward*0.14,entry_t,1.10),(0.04,0.055,2.0))
    bays=max(8,int(length/3.5)); step=length/bays
    for i in range(bays+1):
        t=lo+i*step
        if axis=='y': add_box(brick,(t,fixed+outward*(eps+0.09),(retail_h+z1)/2),(0.33,0.20,z1-retail_h-0.22))
        else: add_box(brick,(fixed+outward*(eps+0.09),t,(retail_h+z1)/2),(0.20,0.33,z1-retail_h-0.22))
    for floor in range(4):
        z=retail_h+1.68+floor*3.10
        if axis=='y': add_box(panel,((lo+hi)/2,fixed+outward*(eps+0.13),retail_h+floor*3.10+0.15),(length,0.10,0.22))
        else: add_box(panel,(fixed+outward*(eps+0.13),(lo+hi)/2,retail_h+floor*3.10+0.15),(0.10,length,0.22))
        for i in range(bays):
            t=lo+(i+0.5)*step; ww=min(1.85,step*0.62)
            if axis=='y':
                add_box(glass,(t,fixed+outward*(eps+0.22),z),(ww,0.08,1.65))
                for s in (-1,1): add_box(frame,(t+s*(ww/2+0.045),fixed+outward*(eps+0.27),z),(0.08,0.07,1.77))
                for s in (-1,1): add_box(frame,(t,fixed+outward*(eps+0.27),z+s*0.86),(ww+0.08,0.07,0.08))
            else:
                add_box(glass,(fixed+outward*(eps+0.22),t,z),(0.08,ww,1.65))
                for s in (-1,1): add_box(frame,(fixed+outward*(eps+0.27),t+s*(ww/2+0.045),z),(0.07,0.08,1.77))
                for s in (-1,1): add_box(frame,(fixed+outward*(eps+0.27),t,z+s*0.86),(0.07,ww+0.08,0.08))
# Quad-facing windows. Dimension and floor elevation are estimates.
for axis,fixed,lo,hi,outward in [('y',cy-court_d/2,x0,x1,1),('y',cy+court_d/2,x0,x1,-1),('x',cx-court_w/2,y0,y1,1),('x',cx+court_w/2,y0,y1,-1)]:
    length=hi-lo; bays=max(5,int(length/5.0)); step=length/bays
    for floor in range(4):
        z=retail_h+1.68+floor*3.10
        for i in range(bays):
            t=lo+(i+0.5)*step
            if axis=='y': add_box(glass,(t,fixed+outward*0.18,z),(1.4,0.08,1.5))
            else: add_box(glass,(fixed+outward*0.18,t,z),(0.08,1.4,1.5))
# Courtyard finish and low roof edge; all placements approximate.
add_box(quad,(cx,cy,retail_h+0.10),(court_w-0.7,court_d-0.7,0.16));
# Split the roof membrane around the open interior quad.
outer_w=x1-x0-0.4; outer_d=y1-y0-0.4; rw=(outer_w-court_w)/2; rd=(outer_d-court_d)/2;
add_box(roof,(cx-(court_w+rw)/2,cy,z1-0.20),(rw,outer_d,0.18)); add_box(roof,(cx+(court_w+rw)/2,cy,z1-0.20),(rw,outer_d,0.18));
add_box(roof,(cx,cy-(court_d+rd)/2,z1-0.20),(court_w,rd,0.18)); add_box(roof,(cx,cy+(court_d+rd)/2,z1-0.20),(court_w,rd,0.18))
for axis,fixed,lo,hi in [('y',y0,x0,x1),('y',y1,x0,x1),('x',x0,y0,y1),('x',x1,y0,y1)]:
    if axis=='y': add_box(panel,((lo+hi)/2,fixed,z1-0.32),(hi-lo,0.4,0.5))
    else: add_box(panel,(fixed,(lo+hi)/2,z1-0.32),(0.4,hi-lo,0.5))
# Pierce Engineers documents two below-grade heated parking levels. Show them as a
# simplified, deliberately schematic structural study beneath the inherited grade.
# These do not claim verified ramp, stall, or column locations.
for level,z in enumerate((-3.15,-6.30),1):
    add_box(concrete,(cx,cy,z),(x1-x0-1.0,y1-y0-1.0,0.24))
    for px in (x0+4.0,cx,x1-4.0):
        for py in (y0+4.0,cy,y1-4.0):
            add_box(concrete,(px,py,z+1.50),(0.32,0.32,2.76))
# Build one mesh per material batch for fast loading and portable, compact libraries.
for material,(verts,faces) in batches.items():
    mesh=bpy.data.meshes.new(PREFIX+material.name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update(); ob=bpy.data.objects.new(PREFIX+material.name,mesh); COLL.objects.link(ob)
# The dated exterior photo shows FUSE branding on two adjacent upper corner faces.
# Sign size/offset are visual approximations; this camera-visible corner uses +X/-Y.
for suffix,location,rotation in [('SoutheastSouthFace',(x1-5.0,y0-0.42,z1-0.05),(math.pi/2,0,0)),('SoutheastEastFace',(x1+0.42,y0+5.0,z1-0.05),(math.pi/2,0,math.pi/2))]:
    font=bpy.data.curves.new(PREFIX+suffix+'_SignText','FONT'); font.body='FUSE'; font.size=3.0; font.extrude=0.05; font.align_x='CENTER'; font.align_y='CENTER'
    text=bpy.data.objects.new(PREFIX+suffix+'_FUSE_Sign',font); COLL.objects.link(text); text.location=location; text.rotation_euler=rotation; font.materials.append(signmat)
BASE['source_footprint']='Legacy shell XY ring matches OSM way 256639574 (name=FUSE, building=residential) within saved-mesh precision; comparison from rounded vertices has mean nearest-vertex deviation 0.0000154 m and maximum 0.0000301 m. OSM is community-mapped, not a survey.'; BASE['height_status']='16 m inherited from the massing asset; not independently measured.'; BASE['architecture_status']='One commercial level, four residential levels, interior quad, and two schematic below-grade parking levels per Pierce Engineers; facade rhythm and entrances remain approximate.'; BASE['building_source_url']='https://www.housing.purdue.edu/my-housing/options/apartments/fuse.html'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('FUSE_R1_SAVED',ASSET,'objects',len(COLL.objects),'new_vertices',sum(len(o.data.vertices) for o in COLL.objects if o.type=='MESH' and o.name.startswith(PREFIX)))



