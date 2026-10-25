import bpy, math, json, os
from mathutils import Vector, Matrix
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
OUT=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lawson_hall'];root=bpy.data.objects['AssetRoot_lawson_hall']
# Re-register the earlier plan trace using same-point controls from the north-up Purdue PDF and official GIS FID 59.
# New controls: plan NW wall corner (323,86)->GIS(-13.209,40.611), NE wall corner (627,86)->GIS(14.791,40.547),
# SW wall corner (298,986)->GIS(-15.553,-42.493), all in meters relative to Placement_lawson_hall (-282.5,44).
SX=0.092105; X0=-13.209-SX*323
SY=(40.611-(-42.493))/(986-86); Y0=40.611+SY*86
OLD_S=0.0944

def remap(x,y):
    # Existing xy(xpx,ypx) from improve.py and the independently registered GIS/PDF axis fit.
    px=327.0+(x+15.55)/OLD_S
    py=88.0+(42.27-y)/OLD_S
    return (X0+SX*px, Y0-SY*py)

# Remove R3 public-entry geometry incorrectly placed along the straight south wall.
removed=[]
for o in list(asset.objects):
    if o.name=='LWSN_R3_Curved_Limestone_Main_Entry_Canopy' or o.name=='LWSN_R3_Entrance_Sign_Text' or o.name.startswith('LWSN_R3_Entry_') or o.name.startswith('LWSN_R3_Entry_'):
        removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)

# Re-register every mesh whose footprint or location was traced/placed from the plan.
# Keep the source-sized 4x4 display modules unchanged in size; remap only their position.
prefixes=('LWSN_Plan_Partition','LWSN_1142_','LWSN_Office_','LWSN_Commons_','LWSN_Stair_Flight','LWSN_R3_Plan_','LWSN_R3_Stair_','LWSN_R5_Echo_','LWSN_R5_Kurz_')
updated=[]
for o in list(asset.objects):
    if o.type!='MESH': continue
    is_wall=o.name=='LWSN_1130_Harris_Video_Wall' or o.name.startswith('LWSN_R5_VideoWall_')
    if not is_wall and not o.name.startswith(prefixes): continue
    mw=o.matrix_world.copy(); inv=mw.inverted()
    if o.data.users>1: o.data=o.data.copy()
    for v in o.data.vertices:
        p=mw @ v.co
        nx,ny=remap(p.x,p.y)
        if is_wall:
            v.co=inv @ Vector((p.x+(nx-p.x),p.y+(ny-p.y),p.z))
        else:
            v.co=inv @ Vector((nx,ny,p.z))
    o.data.update()
    o['plan_registration']='R7 two-axis registration to same-feature controls on Purdue first-floor plan and Purdue GIS FID 59'
    o['plan_registration_scale_m_per_pixel']=[SX,SY]
    o['plan_registration_source']='audit/batch2_lawson/lawson_1.pdf; audit/batch2_lawson/gis_fid59_live.json'
    o['plan_registration_uncertainty_m']='Approx. 0.3 m at matched raster corners; original PDF line width and raster edge picks limit precision.'
    updated.append(o.name)

# Photo-supported approximated glass/material set; footprint vertices exactly follow the six
# GIS boundary segments absent from the prior structural wall baseline around the southeast vestibule.
gis=json.load(open(OUT+'/gis_fid59_live.json',encoding='utf8'))['features'][0]['geometry']['rings'][0]
# Use saved project-local GIS polygon points, which are the direct FID 59 snapshot transformed
# through Purdue project's documented tangent-plane approximation, then relative to placement marker.
site=json.load(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/target_buildings_gis.json',encoding='utf8'))['LWSN']['world_polygon']
marker=(-282.5,44.0)
ring=[(p[0]-marker[0],p[1]-marker[1]) for p in site]
# The GIS-only vestibule contour is the ordered source ring from vertices 42-52.
# Do not shortcut intermediate vertices: two prior hand-entered chords crossed
# the exact FID 59 outline by up to roughly two meters.
segments=list(zip(ring[42:52],ring[43:53]))

# One-storey vestibule height is estimated from the Purdue entrance photograph; not a surveyed elevation.
Z0=0.80; ZTOP=3.55; ZCANOPY=3.78; CANOPY_T=0.28

def mesh_object(name,vertices,faces,mat,props):
    me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(vertices,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me);asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4)
    for k,v in props.items(): ob[k]=v
    return ob

def panel(name,a,b,z0,z1,mat,props):
    ax,ay=a;bx,by=b
    return mesh_object(name,[(ax,ay,z0),(bx,by,z0),(bx,by,z1),(ax,ay,z1)],[(0,1,2,3)],mat,props)

props={'source':'Purdue CS first-floor plan and Purdue GIS FID 59','source_urls':'https://www.cs.purdue.edu/resources/docs/lawson_1.PDF; https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query','footprint_status':'Plan and GIS matched; vertices follow GIS boundary segments omitted by prior wall shell','height_status':'Approximate one-storey vestibule height estimated from Purdue entrance photograph; not measured','uncertainty':'GIS footprint supports plan only; elevation, glazing type, mullion cadence and exact door positions are not dimensioned.'}
glass=bpy.data.materials['LWSN_Curtain_Glass'];bronze=bpy.data.materials['LWSN_Dark_Aluminum_Bronze'];stone=bpy.data.materials['LWSN_Bedford_Limestone']
# Locate long opening segment in official GIS outline and place paired glazed leaves there.
door_a,door_b=segments[4]
L=math.dist(door_a,door_b);ux=(door_b[0]-door_a[0])/L;uy=(door_b[1]-door_a[1])/L
opening=2.1;t0=(1-opening/L)/2;t1=1-t0
def lerp(a,b,t):return(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
for i,(a,b) in enumerate(segments):
    if a==door_a and b==door_b:
        panel('LWSN_R7_Vestibule_Glass_Left_Sidelight',a,lerp(a,b,t0),Z0,ZTOP,glass,props)
        panel('LWSN_R7_Vestibule_Glass_Right_Sidelight',lerp(a,b,t1),b,Z0,ZTOP,glass,props)
        panel('LWSN_R7_Vestibule_Door_Leaf_L',lerp(a,b,t0),lerp(a,b,(t0+t1)/2),Z0,ZTOP,glass,{**props,'opening':'paired entrance; exact door location inferred from plan swing marks'})
        panel('LWSN_R7_Vestibule_Door_Leaf_R',lerp(a,b,(t0+t1)/2),lerp(a,b,t1),Z0,ZTOP,glass,{**props,'opening':'paired entrance; exact door location inferred from plan swing marks'})
    else:
        panel(f'LWSN_R7_Vestibule_Glass_Panel_{i+1}',a,b,Z0,ZTOP,glass,props)

# GIS FID 59 includes a north-edge closure between vertices 6 and 7 absent
# from the prior brick baseline. The horizontal edge is source-backed; the
# vertical height is inherited from the neighboring schematic wall and remains
# explicitly unverified because no north elevation was found.
na,nb=ring[6],ring[7]
dx,dy=nb[0]-na[0],nb[1]-na[1];ll=math.hypot(dx,dy);nx,ny=dy/ll,-dx/ll;th=.14;zlo=.80;zhi=14.55
wallverts=[(na[0],na[1],zlo),(nb[0],nb[1],zlo),(nb[0]+nx*th,nb[1]+ny*th,zlo),(na[0]+nx*th,na[1]+ny*th,zlo),(na[0],na[1],zhi),(nb[0],nb[1],zhi),(nb[0]+nx*th,nb[1]+ny*th,zhi),(na[0]+nx*th,na[1]+ny*th,zhi)]
wallfaces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
mesh_object('LWSN_R7_North_GIS_Footprint_Closure',wallverts,wallfaces,bpy.data.materials['LWSN_Purdue_Red_Brick'],{'source':'Purdue GIS FID 59 and Purdue CS first-floor plan','footprint_status':'Follows source GIS boundary edge 6->7; 3.965 m plan length.','height_status':'14.55 m top copied from neighboring schematic exterior wall; unverified, not measured.','facade_status':'North-edge opening cadence unavailable; no windows inferred.'})

# Photo-supported limestone canopy sits over the entrance wall only; do not
# carry it around the full vestibule boundary. The entrance edge is GIS-matched,
# while the canopy extension/projection are explicitly visual estimates.
L=math.dist(door_a,door_b);tx=(door_b[0]-door_a[0])/L;ty=(door_b[1]-door_a[1])/L;nx,ny=-ty,tx
side=.70;projection=1.20;sagitta=.40;start=(door_a[0]-tx*side,door_a[1]-ty*side);end=(door_b[0]+tx*side,door_b[1]+ty*side)
inner=[(start[0]+(end[0]-start[0])*i/8,start[1]+(end[1]-start[1])*i/8) for i in range(9)]
outer=[(p[0]+nx*(projection+sagitta*math.sin(math.pi*i/8)),p[1]+ny*(projection+sagitta*math.sin(math.pi*i/8))) for i,p in enumerate(inner)]
poly=inner+list(reversed(outer));count=len(poly);canopyverts=[(x,y,3.43) for x,y in poly]+[(x,y,3.78) for x,y in poly]
canopyfaces=[tuple(count+i for i in range(count)),tuple(reversed(range(count)))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
mesh_object('LWSN_R7_Entrance_Canopy',canopyverts,canopyfaces,stone,{**props,'feature':'Shallow curved limestone entrance canopy visible in Purdue exterior photograph.','footprint_status':'Centered on GIS/plan entrance wall; side extensions 0.70 m, projection 1.20 m and convex bow 0.40 m are visual estimates.'})

# Bronze vertical joints articulate the plan/GIS-defined glazed perimeter. Spacing is illustrative.
for i,(a,b) in enumerate(segments):
    x,y=a
    # small square vertical mullion at each GIS break
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,(Z0+ZTOP)/2))
    ob=bpy.context.object;ob.name=f'LWSN_R7_Vestibule_Mullion_{i+1}';ob.dimensions=(.075,.075,ZTOP-Z0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.data.materials.append(bronze)
    ob['evidence_status']='Illustrative mullion on GIS/plan-supported vestibule edge; spacing and profile are not dimensioned.'

# Three restrained exterior treads and rails at the new entrance; location is illustrative within the plan/GIS projection.
mid=lerp(door_a,door_b,.5); dx=door_b[0]-door_a[0];dy=door_b[1]-door_a[1];dl=math.hypot(dx,dy);tx=dx/dl;ty=dy/dl
# outward direction from vestibule centroid
nx=mid[0]-ctr[0];ny=mid[1]-ctr[1];nl=math.hypot(nx,ny);nx/=nl;ny/=nl
rot=math.atan2(ty,tx)
for i in range(3):
    dist=.50+i*.34; center=(mid[0]+nx*dist,mid[1]+ny*dist,.70-i*.18)
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);ob=bpy.context.object;ob.name=f'LWSN_R7_Vestibule_Approach_Tread_{i+1}';ob.dimensions=(5.4,.34,.16);ob.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.data.materials.append(stone)
    ob['evidence_status']='Steps visible in Purdue entrance photograph; dimensions/position estimated from plan/GIS vestibule geometry.'

# Preserve identity, collection and placement. Save and reopen the individual source only.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
reopened_asset=bpy.data.collections.get('Asset_lawson_hall')
print(json.dumps({'saved_source':bpy.data.filepath,'reopened_source':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(ASSET)),'re_registered_plan_objects':len(updated),'removed_misplaced_entry_objects':len(removed),'new_vestibule_panels':sum(o.name.startswith('LWSN_R7_Vestibule_Glass_') for o in reopened_asset.objects),'vestibule_canopy':bpy.data.objects.get('LWSN_R7_Entrance_Canopy') is not None,'north_gis_footprint_closure':bpy.data.objects.get('LWSN_R7_North_GIS_Footprint_Closure') is not None,'plan_scales_m_per_pixel':[SX,SY],'plan_pixel_to_local_origin':[X0,Y0]},indent=2))
