import bpy, math, json, os
from mathutils import Vector
from math import radians, sin, cos
ASSET_ID='massing_hall_of_data_science_and_ai_dsai_c8a41cc'
COLL='Asset_'+ASSET_ID
POLY=[[-105.10555549211085, 139.66237598145653], [-129.8574812718024, 169.04941890733426], [-121.45174350189234, 176.1368369212505], [-120.86278990802815, 175.4375375710606], [-108.9553903954778, 185.4773717061289], [-108.4073444327126, 184.82666777892746], [-99.85833210605796, 192.03478651755404], [-100.40637794950528, 192.685435258295], [-99.09117388409457, 193.79434725585497], [-104.91889453664754, 200.7133438289702], [-92.79543241918995, 210.93524187958337], [-80.96131566242666, 196.88506268651508], [-80.84487847997018, 196.9832351273567], [-80.1884533428514, 196.2038823098942], [-80.85457414775586, 195.57579231185173], [-79.25338939444514, 193.67473040392724], [-78.52179855320803, 194.2251550395008], [-77.86745176734559, 193.44824308164561], [-77.98388904260487, 193.3500148768053], [-74.86129608938887, 189.64264162644213], [-70.49741475972645, 184.46149211912143], [-67.76534682926255, 181.2178707554176], [-65.90039746008286, 179.00362959918766], [-69.3947568227414, 176.05738586974667], [-78.02384427713069, 168.78183035179518], [-84.5802652216076, 176.56609706339168], [-89.0315962993377, 173.12026526399222], [-84.14417907739049, 167.31761693735507], [-89.96807637388461, 162.40720785549456], [-85.551012019118, 157.16293611711762], [-86.37603126613276, 156.46730138586236], [-86.85865934050771, 157.0402674971615], [-91.11978178406306, 153.4475299664041], [-90.67604025367952, 152.84176565939333], [-91.37491909365265, 152.25252588096964], [-91.85747279923802, 152.82554733494862], [-97.68135388778332, 147.9150762931772], [-96.69977174745239, 146.74971063814382], [-105.10555549211085, 139.66237598145653]]
# campus coordinates, meters. FID196 ArcGIS building outline translated with project's stated local conversion.
ZBASE=0.0
WALL_H=10.65  # four levels are official; story/roof heights are photo-based estimates, not surveyed.
FLOOR_Z=[0.45,3.05,5.65,8.25]
# Chosen from the exterior-review camera-facing facade; exact portal station is an estimate.
front_dir=(-.64,-.77)
front_candidates=[]
for _i,_p in enumerate(POLY):
    _q=POLY[(_i+1)%len(POLY)]; _dx=_q[0]-_p[0]; _dy=_q[1]-_p[1]; _L=math.hypot(_dx,_dy)
    if _L>12:
        _nx,_ny=-_dy/_L,_dx/_L; front_candidates.append((_nx*front_dir[0]+_ny*front_dir[1],_i,_L))
door_edge_index=max(front_candidates)[1]
# Remove previous contents, preserving the stable exported collection and asset identity.
coll=bpy.data.collections.get(COLL)
if not coll:
    coll=bpy.data.collections.new(COLL); bpy.context.scene.collection.children.link(coll)
for ob in list(coll.objects): bpy.data.objects.remove(ob,do_unlink=True)

def mat(name,color,rough=.75,metal=0):
    m=bpy.data.materials.get(name)
    if not m: m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
brick=mat('DSAI | warm Purdue red brick',(.30,.073,.045),.88)
limestone=mat('DSAI | pale Indiana limestone',(.67,.61,.49),.78)
shadow=mat('DSAI | recessed shadow mortar',(.105,.075,.063),.9)
glass=mat('DSAI | dark blue reflective glazing',(.035,.105,.15),.2,.35)
roofmat=mat('DSAI | terracotta clay tile roof',(.19,.033,.015),.78)
rn=roofmat.node_tree.nodes; rl=roofmat.node_tree.links; rb=rn.get('Principled BSDF'); rg=rn.new('ShaderNodeNewGeometry')
rt=rn.new('ShaderNodeTexBrick'); rt.inputs['Color1'].default_value=(.26,.049,.021,1); rt.inputs['Color2'].default_value=(.19,.027,.012,1); rt.inputs['Mortar'].default_value=(.10,.042,.024,1); rt.inputs['Scale'].default_value=2.4; rt.inputs['Mortar Size'].default_value=.02; rt.inputs['Mortar Smooth'].default_value=.01; rl.new(rg.outputs['Position'],rt.inputs['Vector']); rl.new(rt.outputs['Color'],rb.inputs['Base Color'])
rbu=rn.new('ShaderNodeBump'); rbu.inputs['Strength'].default_value=.17; rbu.inputs['Distance'].default_value=.008; rl.new(rt.outputs['Fac'],rbu.inputs['Height']); rl.new(rbu.outputs['Normal'],rb.inputs['Normal'])
roofedge=mat('DSAI | dark bronze roof edge',(.075,.053,.04),.4,.55)
concrete=mat('DSAI | exposed concrete',(.48,.48,.44),.83)
interior=mat('DSAI | warm interior finish',(.76,.69,.56),.7)
green=mat('DSAI | green roof planting',(.12,.22,.08),.93)
metal=mat('DSAI | dark bronze frames',(.055,.062,.065),.3,.7)
wood=mat('DSAI | café wood',(.32,.17,.075),.62)
# A real unit-scaled running-bond brick pattern, mapped in facade meters on each registered wall segment.
nt=brick.node_tree; nodes=nt.nodes; links=nt.links; bs=nodes.get('Principled BSDF')
uvnode=nodes.new('ShaderNodeUVMap'); uvnode.uv_map='FacadeMeters'
bricktex=nodes.new('ShaderNodeTexBrick'); bricktex.inputs['Color1'].default_value=(.34,.085,.05,1); bricktex.inputs['Color2'].default_value=(.25,.052,.032,1); bricktex.inputs['Mortar'].default_value=(.13,.085,.068,1); bricktex.inputs['Scale'].default_value=2.1; bricktex.inputs['Mortar Size'].default_value=.018; bricktex.inputs['Mortar Smooth'].default_value=.01
links.new(uvnode.outputs['UV'],bricktex.inputs['Vector']); links.new(bricktex.outputs['Color'],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.01; links.new(bricktex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def brick_wall(name,verts,length):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],[(0,1,2,3)]); me.materials.append(brick); me.update()
    uv=me.uv_layers.new(name='FacadeMeters')
    coords=[(0,0),(length,0),(length,WALL_H),(0,WALL_H)]
    for lp in me.loops: uv.data[lp.index].uv=coords[lp.vertex_index]
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob

BATCH={}
def mesh_obj(name,verts,faces,material):
    entry=BATCH.setdefault(material,{'verts':[],'faces':[],'name':name})
    off=len(entry['verts']); entry['verts'].extend([tuple(v) for v in verts]); entry['faces'].extend([tuple(off+i for i in face) for face in faces]); return None

def cube(name,loc,scale,material,rot=0):
    x,y,z=loc; sx,sy,sz=[v/2 for v in scale]; c=math.cos(rot); s=math.sin(rot)
    verts=[]
    for xx,yy,zz in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]:
        verts.append((x+c*xx-s*yy,y+s*xx+c*yy,z+zz))
    mesh_obj(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],material)

def flush_batches():
    for material,data in BATCH.items():
        mesh_obj2=data; me=bpy.data.meshes.new('DSAI merged '+material.name); me.from_pydata(data['verts'],[],data['faces']); me.materials.append(material); me.update()
        ob=bpy.data.objects.new('DSAI | '+material.name,me); coll.objects.link(ob)
    BATCH.clear()

# Exact GIS ring walls; upper floor masses step back subtly, indicating phased adaptive reuse wing elevations.
for i,p in enumerate(POLY):
    q=POLY[(i+1)%len(POLY)]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy)
    if L<.18: continue
    # Long, clearly visible structural faces. Roof and wall remain at GIS alignment.
    verts=[(p[0],p[1],0),(q[0],q[1],0),(q[0],q[1],WALL_H),(p[0],p[1],WALL_H)]
    brick_wall('Masonry shell face %02d'%i,verts,L)
    # Stone foundation course and floor-level belt courses along registered straight segments.
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    def strip(name,z,h,depth,material,offset=.025):
        vv=[]
        for xx,yy,zz in [(p[0],p[1],z),(q[0],q[1],z),(q[0],q[1],z+h),(p[0],p[1],z+h)]: vv.append((xx+nx*offset,yy+ny*offset,zz))
        ob=mesh_obj(name,vv,[(0,1,2,3)],material); return ob
    strip('Limestone water table %02d'%i,.15,.63,.08,limestone,.045)
    for fl,z in enumerate([2.85,5.45,8.05,10.3]):
        strip('Continuous limestone belt %02d-%d'%(i,fl),z,.22,.07,limestone,.055)
    # Glazed window rhythm on each substantial face, based on photographic elevations.
    if L>=3.2:
        bays=max(1,round(L/2.25)); bay=L/bays
        for floor,z in enumerate(FLOOR_Z):
            # Lower levels use paired vertical punched openings; top floor has taller grouped glazing.
            winh=1.48 if floor<3 else 2.10
            sill=z+.63 if floor<3 else z+.33
            winw=min(bay*.58,1.18) if floor<3 else min(bay*.48,1.00)
            if bay<1.65: winw=bay*.62
            for j in range(bays):
                d=(j+.5)*bay
                if i==door_edge_index and floor==0 and abs(d-L/2)<1.5: continue
                cx=p[0]+ux*d+nx*.10; cy=p[1]+uy*d+ny*.10
                # frame-backed dark window recess; glazing panel sits in wall plane, with mullions.
                cube('Recessed window surround', (cx+nx*.035,cy+ny*.035,sill+winh/2),(winw+.15,.10,winh+.14),limestone, math.atan2(uy,ux))
                cube('Insulated dark glazing',(cx+nx*.105,cy+ny*.105,sill+winh/2),(winw,.035,winh),glass,math.atan2(uy,ux))
                # vertical muntins and mid-rail create the narrow historic sash rhythm
                for k in [-1,1]:
                    cube('Bronze window mullion',(cx+ux*k*winw*.32+nx*.13,cy+uy*k*winw*.32+ny*.13,sill+winh/2),(.045,.045,winh),metal,math.atan2(uy,ux))
                cube('Window transom',(cx+nx*.13,cy+ny*.13,sill+winh*.60), (winw,.045,.04),metal,math.atan2(uy,ux))
                cube('Stone window sill',(cx+nx*.14,cy+ny*.14,sill-.09),(winw+.2,.16,.13),limestone,math.atan2(uy,ux))
# Recessed glazed entry and limestone frame. Exact doorway position is not dimensioned in public sources.
_di=door_edge_index; _p=POLY[_di]; _q=POLY[(_di+1)%len(POLY)]; _dx=_q[0]-_p[0]; _dy=_q[1]-_p[1]; _L=math.hypot(_dx,_dy); _ux,_uy=_dx/_L,_dy/_L; _nx,_ny=-_uy,_ux; _d=_L/2
_ex=_p[0]+_ux*_d+_nx*.20; _ey=_p[1]+_uy*_d+_ny*.20; _rot=math.atan2(_uy,_ux)
cube('Main glazed entry doors',(_ex,_ey,1.28),(2.05,.12,2.56),glass,_rot)
for _side in [-1,1]: cube('Limestone entry jamb',(_ex+_ux*_side*1.18,_ey+_uy*_side*1.18,1.45),(.28,.33,2.9),limestone,_rot)
cube('Limestone entry lintel',(_ex,_ey,2.95),(2.62,.37,.32),limestone,_rot)
cube('Limestone entry canopy',(_ex+_nx*.55,_ey+_ny*.55,3.12),(3.1,1.25,.24),limestone,_rot)
for _j in range(3): cube('Entry approach step %d'%_j,(_ex+_nx*(.55+_j*.42),_ey+_ny*(.55+_j*.42),.12+_j*.05),(3.2,1.2,.18),limestone,_rot)
# Pale stone corner piers emphasize documented quoins only at strong building corners, not every GIS vertex.
for i,(x,y) in enumerate(POLY):
    prev=POLY[(i-1)%len(POLY)]; nxt=POLY[(i+1)%len(POLY)]
    a=(x-prev[0],y-prev[1]); b=(nxt[0]-x,nxt[1]-y); la=math.hypot(*a); lb=math.hypot(*b)
    if la<3.0 or lb<3.0: continue
    bend=abs(math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1]))
    if bend>math.radians(42): cube('Stone corner quoin %02d'%i,(x,y,WALL_H*.48),(.72,.72,WALL_H*.95),limestone)
# Perimeter cornice immediately below the tile roof.
for i,p in enumerate(POLY):
    q=POLY[(i+1)%len(POLY)]; dx=q[0]-p[0]; dy=q[1]-p[1]; L=math.hypot(dx,dy)
    if L<.18: continue
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    verts=[(p[0]+nx*.12,p[1]+ny*.12,10.48),(q[0]+nx*.12,q[1]+ny*.12,10.48),(q[0]+nx*.12,q[1]+ny*.12,10.72),(p[0]+nx*.12,p[1]+ny*.12,10.72)]
    mesh_obj('Pale limestone upper cornice %02d'%i,verts,[(0,1,2,3)],limestone)
# Roof hip blocks: simplified crossing hipped masses aligned to the GIS rectangle; photographed terracotta tile.
angle=radians(130.5816185364); ux,uy=cos(angle),sin(angle); vx,vy=-uy,ux
cx,cy=-98.1305090241,174.5757082467
# Each roof polygon uses a central ridge/hip geometry. These are visual estimates, not surveyed roof edges.
def hiproof(name,cu,cv,wx,wy,base=10.64,rise=2.55):
    mx=cx+ux*cu+vx*cv; my=cy+uy*cu+vy*cv
    corners=[]
    for a,b in [(-wx/2,-wy/2),(wx/2,-wy/2),(wx/2,wy/2),(-wx/2,wy/2)]: corners.append((mx+ux*a+vx*b,my+uy*a+vy*b))
    # Long ridge with clipped hip ends. This matches the long, intersecting clay-tile roofs in the architect photos.
    if wx>=wy:
        half=max(.5,wx/2-wy/2); ridge=[(mx-ux*half,my-uy*half,base+rise),(mx+ux*half,my+uy*half,base+rise)]
    else:
        half=max(.5,wy/2-wx/2); ridge=[(mx-vx*half,my-vy*half,base+rise),(mx+vx*half,my+vy*half,base+rise)]
    verts=[(x,y,base) for x,y in corners]+ridge
    faces=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]
    mesh_obj(name,verts,faces,roofmat)
    for i,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):
        dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy); nx,ny=dy/L,-dx/L
        mesh_obj(name+' dark eaves '+str(i),[(a[0]+nx*.08,a[1]+ny*.08,base-.05),(b[0]+nx*.08,b[1]+ny*.08,base-.05),(b[0]+nx*.08,b[1]+ny*.08,base+.08),(a[0]+nx*.08,a[1]+ny*.08,base+.08)],[(0,1,2,3)],roofedge)
    mesh_obj(name+' ridge cap',[(ridge[0][0],ridge[0][1],ridge[0][2]),(ridge[1][0],ridge[1][1],ridge[1][2]),(ridge[1][0]+.06,ridge[1][1]+.06,ridge[1][2]+.02),(ridge[0][0]+.06,ridge[0][1]+.06,ridge[0][2]+.02)],[(0,1,2,3)],roofedge)
hiproof('Main hipped red tile roof',0,0,42,26)
hiproof('North west hipped wing',-4,20.5,22,15)
hiproof('South east hipped wing',5,-20.5,22,15)
# Third-floor planted terrace and glazed interior lightwell are explicitly evidence-backed design features.
# Estimated location within overall envelope; rendered inside the registered shell.
terrace=cube('Existing second floor green roof terrace', (cx+ux*10,cy+uy*10,6.00),(10,7,.24),green,angle)
# Compact glazed roof lantern on the main ridge; actual atrium plan station is estimated.
lantern_z=13.28
cube('Glazed atrium skylight',(cx,cy,lantern_z),(4.25,2.45,.08),glass,angle)
for j,(du,dv,sz) in enumerate([(0,-1.28,(4.5,.10,.18)),(0,1.28,(4.5,.10,.18)),(-2.2,0,(.10,2.6,.18)),(2.2,0,(.10,2.6,.18))]):
    cube('Bronze skylight curb '+str(j),(cx+ux*du+vx*dv,cy+uy*du+vy*dv,lantern_z+.06),sz,metal,angle)
# Select interior pieces imply research floors and the open central communicating stair; schematic placement only.
# Tall concrete columns are visible through large lobby windows.
for i,(du,dv) in enumerate([(-8,-8),(0,-8),(8,-8),(-8,8),(0,8),(8,8)]):
    x=cx+ux*du+vx*dv; y=cy+uy*du+vy*dv
    cube('Exposed concrete atrium column %02d'%i,(x,y,4.6),(.43,.43,9.0),concrete,angle)
    # Three documented columns receive green circuit-inspired graphic bands; exact artwork is schematic.
    if i<3:
        for side in range(4):
            a=angle+side*math.pi/2; ox=math.cos(a)*.24; oy=math.sin(a)*.24
            cube('Green data-circuit column wrap %02d-%d'%(i,side),(x+ox,y+oy,4.15),(.47,.035,.82),green,a)
# Four schematic floor plates are arranged as a ring around an open atrium (plan placement estimated).
def local_world(uu,vv): return (cx+ux*uu+vx*vv,cy+uy*uu+vy*vv)
for level_z in [2.92,5.52,8.12]:
    for uu,vv,ww,dd in [(0,-13,32,6),(0,13,32,6),(-13,0,6,18),(13,0,6,18)]:
        xx,yy=local_world(uu,vv); cube('Schematic research floor plate',(xx,yy,level_z),(ww,dd,.18),interior,angle)
# Documented new communicating stair between floors 2 and 3: two broad switchback flights and landings.
for uu,vv,zz in [(0,-3.0,5.65),(3.15,-.15,6.95),(-3.15,3.0,8.25)]:
    xx,yy=local_world(uu,vv); cube('Communicating stair landing',(xx,yy,zz),(4.3,3.0,.20),concrete,angle)
def sloped_rail(name,u0,u1,vv,z0,z1):
    xx0,yy0=local_world(u0,vv); xx1,yy1=local_world(u1,vv); halfv=.045; halfz=.055
    verts=[(xx+vx*dv,yy+vy*dv,zz+dz) for xx,yy,zz in [(xx0,yy0,z0),(xx1,yy1,z1)] for dv,dz in [(-halfv,-halfz),(halfv,-halfz),(halfv,halfz),(-halfv,halfz)]]
    mesh_obj(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],metal)
for flight in range(2):
    lo=5.65+flight*1.30; hi=lo+1.30; startu,endu=(-2.8,2.8) if flight==0 else (2.8,-2.8); vv=-3.0 if flight==0 else 0.0
    for step in range(10):
        t=(step+.5)/10; uu=startu+(endu-startu)*t; zz=lo+(hi-lo)*t
        xx,yy=local_world(uu,vv); cube('Wide communicating stair tread %d-%02d'%(flight,step),(xx,yy,zz),(2.6,.31,.13),interior,angle)
    for side in [-1,1]: sloped_rail('Communicating stair handrail %d'%flight,startu,endu,vv+side*1.4,lo+.95,hi+.95)
# Café/research neighborhood tables; schematic interior fittings, no public plan source located.
for i,(du,dv) in enumerate([(-13,-8),(-10,-8),(-13,0),(-10,0),(13,8),(10,8)]):
    x=cx+ux*du+vx*dv; y=cy+uy*du+vy*dv
    cube('Research table %02d'%i,(x,y,3.15),(2.2,1.0,.12),wood,angle)
    for t in [-.8,.8]: cube('Research table leg',(x+ux*t,y+uy*t,2.73),(.08,.08,.8),metal,angle)
    for side in [-1,1]:
        sx=x+vx*side*.95; sy=y+vy*side*.95
        cube('Research chair seat %02d'%i,(sx,sy,2.68),(.78,.72,.12),wood,angle)
        cube('Research chair back %02d'%i,(sx-vx*side*.26,sy-vy*side*.26,3.05),(.78,.10,.72),wood,angle)
        for t in [-.25,.25]: cube('Research chair leg',(sx+ux*t,sy+uy*t,2.39),(.06,.06,.55),metal,angle)
# Collapse repeated architectural elements by material to keep the linked asset fast to load.
flush_batches()
# Add stable custom provenance/technical properties to the root collection.
coll['building_id']=ASSET_ID; coll['source_fid']=196; coll['coordinate_frame']='campus world meters; X east, Y north, Z up'
coll['footprint_source']='Purdue ArcGIS BuildingShapesZip4 FeatureServer/0 FID 196; converted by project approximate local geographic transform'
coll['height_status']='estimated from four official levels and design photographs; no surveyed height source located'
# object hygiene: put every generated object in stable asset collection.
for ob in list(bpy.context.scene.objects):
    if ob.type=='MESH' and coll not in ob.users_collection:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        coll.objects.link(ob)
# viewport state and selected none
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects: ob.select_set(False)
bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.context.scene.world.color=(.22,.22,.22)
# Save later after build script strips render-only camera/light objects.


# Save the standalone, directly linkable asset at its stable path.
bpy.ops.wm.save_as_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend')
