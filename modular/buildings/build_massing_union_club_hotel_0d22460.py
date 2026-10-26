from __future__ import annotations
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_union_club_hotel_0d22460'
ASSET = ROOT / 'modular' / 'buildings' / (ASSET_ID + '.blend')
GIS = ROOT / 'audit' / 'official_purdue_buildings_wgs84.json'
COLLECTION = 'Asset_' + ASSET_ID
SCENE = 'Building_' + ASSET_ID

# Convert Purdue GIS WGS84 ring into the project local campus coordinate frame.
def xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)

def material(name, color, roughness=0.82, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return m

def mesh_object(name, verts, faces, mat, coll):
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob

def box(name, center, size, mat, coll, rotation=0.0):
    x,y,z = center; sx,sy,sz = size
    co = [(-sx/2,-sy/2,-sz/2),(sx/2,-sy/2,-sz/2),(sx/2,sy/2,-sz/2),(-sx/2,sy/2,-sz/2),
          (-sx/2,-sy/2,sz/2),(sx/2,-sy/2,sz/2),(sx/2,sy/2,sz/2),(-sx/2,sy/2,sz/2)]
    c=math.cos(rotation); s=math.sin(rotation)
    verts=[]
    for a,b,d in co:
        verts.append((x+a*c-b*s,y+a*s+b*c,z+d))
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    return mesh_object(name,verts,faces,mat,coll)

def merge_group(coll, prefix, joined_name):
    group=[ob for ob in coll.objects if ob.name.startswith(prefix)]
    if len(group)<2: return
    bpy.ops.object.select_all(action='DESELECT')
    for ob in group: ob.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    bpy.ops.object.join()
    group[0].name=joined_name

def main():
    data=json.loads(GIS.read_text(encoding='utf-8'))
    feat=next(f for f in data['features'] if f['attributes'].get('FID')==663)
    attrs=feat['attributes']
    ring=feat['geometry']['rings'][0]
    points=[]
    for lon,lat in ring:
        p=xy(lon,lat)
        if not points or (Vector(p)-Vector(points[-1])).length>0.001:
            points.append(p)
    if len(points)>2 and (Vector(points[0])-Vector(points[-1])).length<0.001: points.pop()
    # Preserve campus placement and exact GIS footprint. GIS gives seven levels, R=63.1,
    # Extrution=72 and floor elevations; their units are undocumented. Interpreting R/Extrution
    # as feet yields an estimated roof at 19.23 m and overall top near 21.95 m.
    old=bpy.data.collections.get(COLLECTION)
    if old:
        for ob in list(old.objects): bpy.data.objects.remove(ob,do_unlink=True)
        if old.users==0: bpy.data.collections.remove(old)
    coll=bpy.data.collections.new(COLLECTION)
    bpy.context.scene.collection.children.link(coll)
    brick=material('UCH_Brick_WarmRed',(0.32,0.105,0.067))
    brick_light=material('UCH_Brick_Accent',(0.42,0.16,0.10))
    stone=material('UCH_Limestone',(0.72,0.67,0.54))
    roof=material('UCH_Roof_Slate',(0.16,0.19,0.22))
    glass=material('UCH_Window_Glass',(0.075,0.13,0.17),0.24,0.18)
    dark=material('UCH_Window_Frame',(0.10,0.09,0.075))
    metal=material('UCH_Portico_Metal',(0.14,0.14,0.13),0.38,0.55)
    floor_z=[0,2.75,5.55,8.35,11.15,13.95,16.75,19.23]
    # Main shell consists of floor bands to preserve legibility when zoomed to the campus.
    verts=[]
    n=len(points)
    for z in floor_z: verts.extend([(x,y,z) for x,y in points])
    faces=[]
    for level in range(len(floor_z)-1):
        for i in range(n):
            j=(i+1)%n
            faces.append((level*n+i,level*n+j,(level+1)*n+j,(level+1)*n+i))
    top_face=list(range((len(floor_z)-1)*n,len(floor_z)*n))
    # GIS exterior ring is clockwise, so reverse the roof cap for an upward normal.
    faces.append(tuple(reversed(top_face)))
    body=mesh_object('Union Club Hotel',verts,faces,brick,coll)
    body['GIS_FID']=663; body['GIS_Name']='Purdue Memorial Union Club'; body['Official_Name']='Union Club Hotel'
    body['Height_Evidence']='GIS R=63.1 and Extrution=72; units undocumented. If feet, they imply about 21.95 m overall. Modeled gable ridge reaches about 21.35 m from qualitative roof photo evidence; both are estimates, not survey.'
    body['Floor_Evidence']='GIS NUM_LEVELS=7; seven above-grade levels modeled; floor elevations estimated.'
    body['Plan_Source']='Purdue official building GIS FID 663; current WGS84 polygon converted by project approximation.'
    body['Roof_Evidence']='Current Marriott Union Club Hotel exterior gallery shows slate pitched roof planes and repeated gable projections; qualitative only. Roof plan, pitch and heights remain estimated.'
    body['Facade_Evidence']='Current Marriott gallery confirms red brick, pale stone trim, paired punched windows and a broad covered hotel entry; exact dimensions and bay positions remain estimated.'
    body['Entrance_Tower_Evidence']='Circle Design Group / Union Club Hotel exterior image directly shows a pale stone projecting tower and tall arched window beside the hotel porte-cochere; its model position and dimensions are estimated from perspective.'
    # Make modest belt courses at every story level on each exterior segment.
    for lev,z in enumerate(floor_z[1:-1],1):
        for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
            dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
            if L<1.2: continue
            # Clockwise GIS exterior ring: the left-hand edge normal points out.
            nx=-dy/L; ny=dx/L
            mid=((a[0]+b[0])/2+nx*.09,(a[1]+b[1])/2+ny*.09,z)
            box(f'UCH_Story_Belt_{lev}_{i}',mid,(L+0.05,.18,.14),stone,coll,math.atan2(dy,dx))
    # Repeated punched windows; first floor slightly taller, upper floors narrow paired openings.
    for edge,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
        if L<4.0: continue
        ux,uy=dx/L,dy/L; nx,ny=-uy,ux
        count=max(1,int(L//6.8))
        step=L/count
        for lev in range(7):
            z0=floor_z[lev]; z1=floor_z[lev+1]
            win_h=min(1.72,(z1-z0)*.54) if lev else 1.85
            paired=L>14.0
            win_w=min(1.22 if paired else 1.55,step*(.24 if paired else .46))
            zc=z0+(z1-z0)*(.55 if lev else .53)
            for k in range(count):
                center=(k+.5)*step
                offsets=(-.77,.77) if paired else (0.0,)
                for sub,offset in enumerate(offsets):
                    along=center+offset
                    cx=a[0]+ux*along+nx*.10; cy=a[1]+uy*along+ny*.10
                    # stone reveals surround paired and single punched openings,
                    # matching the varied historic brick bays visible in the photos.
                    tag=f'{edge}_{lev}_{k}_{sub}'
                    box(f'UCH_Window_{tag}',(cx,cy,zc),(win_w,.12,win_h),stone,coll,math.atan2(uy,ux))
                    box(f'UCH_Glazing_{tag}',(cx+nx*.07,cy+ny*.07,zc),(win_w*.76,.055,win_h*.78),glass,coll,math.atan2(uy,ux))
                    box(f'UCH_Sill_{tag}',(cx+nx*.11,cy+ny*.11,zc-win_h*.48),(win_w+.13,.16,.09),stone,coll,math.atan2(uy,ux))
                    box(f'UCH_Mullion_{tag}',(cx+nx*.11,cy+ny*.11,zc),(0.07,.075,win_h*.74),dark,coll,math.atan2(uy,ux))
                    box(f'UCH_Transom_{tag}',(cx+nx*.11,cy+ny*.11,zc+win_h*.10),(win_w*.70,.075,.06),dark,coll,math.atan2(uy,ux))
    # Photo evidence shows a slate, pitched roofline with repeated gabled projections
    # and different ridge heights, not a continuous flat cap. GIS does not describe
    # the roof plan, so use a restrained segmented gable/hip massing, explicitly estimated.
    def cross_sections(y):
        xs=[]
        for p,q in zip(points,points[1:]+points[:1]):
            x1,y1=p; x2,y2=q
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1+(y-y1)*(x2-x1)/(y2-y1))
        xs.sort()
        return list(zip(xs[0::2],xs[1::2]))
    def gable_roof(name,x0,x1,y0,y1,z_eave,z_ridge,hip_ends=True):
        # Two pitched slate planes plus brick triangular gable end walls.
        xm=(x0+x1)/2
        v=[(x0,y0,z_eave),(xm,y0,z_ridge),(x1,y0,z_eave),
           (x0,y1,z_eave),(xm,y1,z_ridge),(x1,y1,z_eave)]
        mesh_object(name,v,[(0,1,4,3),(1,2,5,4)],roof,coll)
        if hip_ends:
            mesh_object(name+'_Brick_Gable_Ends',v,[(0,2,1),(3,4,5)],brick_light,coll)
    y_min=min(y for x,y in points); y_max=max(y for x,y in points)
    segment=18.0; idx=0; y0=y_min
    while y0 < y_max:
        y1=min(y_max,y0+segment); ym=(y0+y1)/2
        for xa,xb in cross_sections(ym):
            if xb-xa<3.8: continue
            pad=min(.35,(xb-xa)*.025)
            xa+=pad; xb-=pad
            # Visible roofs are low-pitched and vary in height by section; exact
            # ridges/eave elevations cannot be measured from perspective photos.
            peak=20.15 + (0.75 if idx%3==1 else (0.30 if idx%3==2 else 0.0))
            gable_roof(f'UCH_Roof_Slate_Gable_{idx}',xa,xb,y0,y1,19.23,peak,True)
            # Cross-gables interrupt the long eaves at intervals, as in the photo.
            if (idx%2==1) and xb-xa>8.0:
                yc=(y0+y1)/2; d=min(12.0,(y1-y0)*.72)
                z0=19.85; zpeak=min(21.85,peak+.85)
                cv=[(xa,yc-d/2,z0),(xb,yc-d/2,z0),(xb,yc,zpeak),(xa,yc,zpeak),
                    (xa,yc+d/2,z0),(xb,yc+d/2,z0)]
                mesh_object(f'UCH_Roof_Dormer_Gable_{idx}',cv,
                            [(0,1,2,3),(3,2,5,4)],roof,coll)
                mesh_object(f'UCH_Roof_Dormer_Gable_Walls_{idx}',cv,
                            [(0,3,4),(1,5,2)],brick_light,coll)
            idx+=1
        y0=y1
    # Landmark hotel porte-cochere on the Grant Street frontage (GIS east edge). Exact bay placement inferred from image/frontage.
    # use longest east-facing exterior edge to set a centered entry canopy.
    east_edges=[]
    for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
        if L>8 and abs(dx)<0.25 and ((a[0]+b[0])/2)>max(x for x,y in points)-8.0: east_edges.append((i,a,b,L))
    if east_edges:
        i,a,b,L=max(east_edges,key=lambda q:q[3]); ymid=(a[1]+b[1])/2; x=(a[0]+b[0])/2
        # A broad brick-and-limestone porte-cochere is clearly visible in the
        # Marriott exterior photographs. Bay size and exact location are estimated.
        for q,offset in enumerate((-8.0,8.0)):
            box(f'UCH_Entry_Pier_{q}',(x+1.3,ymid+offset,2.7),(1.0,1.0,5.4),brick_light,coll)
        box('UCH_Entry_Canopy',(x+3.6,ymid,4.9),(8.0,20.0,.72),roof,coll)
        box('UCH_Entry_Lintel',(x+3.6,ymid,5.24),(8.2,20.2,.30),stone,coll)
        box('UCH_Entry_Glazed_Lobby',(x+.25,ymid,2.4),(.22,10.5,4.5),glass,coll)
        # a small inscription plaque communicates hotel entrance without relying on raster signage
        box('UCH_Entry_Sign',(x+7.5,ymid,5.45),(.08,8.5,.48),dark,coll)
        # Historic collegiate gable over the porte-cochere, visible in Purdue's event listing photo.
        x0=x+.05; x1=x+8.0; half=10.0; eave=5.55; peak=7.7
        v=[(x0,ymid-half,eave),(x0,ymid+half,eave),(x0,ymid,peak),
           (x1,ymid-half,eave),(x1,ymid+half,eave),(x1,ymid,peak)]
        mesh_object('UCH_Entry_Gabled_Porte_Cochere',v,[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],roof,coll)
        curve=bpy.data.curves.new('UCH_Entry_Hotel_Lettering_Data','FONT')
        curve.body='UNION CLUB HOTEL'; curve.size=.82; curve.extrude=.008; curve.align_x='CENTER'
        lettering=bpy.data.objects.new('UCH_Entry_Hotel_Lettering',curve); coll.objects.link(lettering)
        lettering.location=(x+8.12,ymid,5.36)
        lettering.rotation_euler=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_euler()
        lettering.data.materials.append(stone)
        # Photo-confirmed projecting stone entrance tower beside the porte-cochere.
        # Exact footprint, bay spacing and elevations are not dimensioned by any source.
        tower_y=ymid-13.0; tower_len=15.0; tower_depth=5.0; tower_top=20.5
        tower_x=x+tower_depth/2
        box('UCH_Entrance_Stone_Tower',(tower_x,tower_y,tower_top/2),
            (tower_depth,tower_len,tower_top),stone,coll)
        # Strong vertical stone piers and floor cornices make the tower read separately
        # from the long brick hotel wing in the high-resolution exterior photos.
        for side,offset in enumerate((-tower_len/2+.45,tower_len/2-.45)):
            box(f'UCH_Entrance_Tower_Corner_Pier_{side}',
                (x+tower_depth+.06,tower_y+offset,tower_top/2),(.28,.42,tower_top),stone,coll)
        for lev in range(1,7):
            zz=lev*2.8
            box(f'UCH_Entrance_Tower_Stringcourse_{lev}',
                (x+tower_depth+.10,tower_y,zz),(.22,tower_len+.14,.18),stone,coll)
        # A tall central arched bay and three upper paired window levels echo the
        # distinctive entrance tower; exact window dimensions are not published.
        arch_z=4.9; arch_h=5.2; arch_w=2.85
        box('UCH_Entrance_Tower_Arched_Glazing',
            (x+tower_depth+.16,tower_y,arch_z),(.12,arch_w,arch_h),glass,coll)
        box('UCH_Entrance_Tower_Arched_Mullion',
            (x+tower_depth+.24,tower_y,arch_z),(.10,.08,arch_h-.25),dark,coll)
        arch_verts=[(x+tower_depth+.24,tower_y-arch_w/2,arch_z+arch_h/2-.25),
                    (x+tower_depth+.24,tower_y+arch_w/2,arch_z+arch_h/2-.25),
                    (x+tower_depth+.24,tower_y,arch_z+arch_h/2+.95)]
        mesh_object('UCH_Entrance_Tower_Arched_Transom',arch_verts,[(0,1,2)],dark,coll)
        for lev,zz in enumerate((11.2,14.2,17.15)):
            for bay,offset in enumerate((-3.1,3.1)):
                wy=tower_y+offset
                box(f'UCH_Entrance_Tower_Glazing_{lev}_{bay}',
                    (x+tower_depth+.16,wy,zz),(.12,1.58,2.0),glass,coll)
                box(f'UCH_Entrance_Tower_Mullion_{lev}_{bay}',
                    (x+tower_depth+.24,wy,zz),(.10,.07,1.88),dark,coll)
                box(f'UCH_Entrance_Tower_Transom_{lev}_{bay}',
                    (x+tower_depth+.24,wy,zz+.12),(.10,1.45,.07),dark,coll)
        box('UCH_Entrance_Tower_Cornice',(x+tower_depth+.1,tower_y,20.0),
            (.4,tower_len+.6,.55),stone,coll)
        # A restrained overhanging slate cap distinguishes the tower crown; elevation is estimated.
        box('UCH_Entrance_Tower_Slate_Crown',(tower_x,tower_y,20.72),
            (tower_depth+.75,tower_len+.75,.36),roof,coll)
    # No roof penthouse was corroborated by the available current exterior photos;
    # retain it as absent rather than adding unsupported rooftop equipment.
    # Consolidate repeated details into a few editable meshes while retaining a clear shell/entry/roof split.
    merge_group(coll,'UCH_Window_','UCH_Facade_Stone_Window_Reveals')
    merge_group(coll,'UCH_Glazing_','UCH_Facade_Glazing')
    merge_group(coll,'UCH_Sill_','UCH_Facade_Stone_Sills')
    merge_group(coll,'UCH_Mullion_','UCH_Facade_Window_Mullions')
    merge_group(coll,'UCH_Transom_','UCH_Facade_Window_Transoms')
    merge_group(coll,'UCH_Story_Belt_','UCH_Story_Belt_Courses')
    merge_group(coll,'UCH_Roof_Coping_','UCH_Roof_Coping')
    merge_group(coll,'UCH_Roof_Slate_Gable_','UCH_Roof_Slate_Gables')
    merge_group(coll,'UCH_Roof_Dormer_Gable_','UCH_Roof_Dormer_Gables')
    merge_group(coll,'UCH_Entrance_Tower_Glazing_','UCH_Entrance_Tower_Glazing')
    merge_group(coll,'UCH_Entrance_Tower_Mullion_','UCH_Entrance_Tower_Mullions')
    merge_group(coll,'UCH_Entrance_Tower_Transom_','UCH_Entrance_Tower_Transoms')
    merge_group(coll,'UCH_Entrance_Tower_Stringcourse_','UCH_Entrance_Tower_Stringcourses')
    merge_group(coll,'UCH_Entrance_Tower_Corner_Pier_','UCH_Entrance_Tower_Corner_Piers')
    # metadata-bearing scene and build log properties on collection.
    coll['stable_building_id']=ASSET_ID; coll['export_collection']=COLLECTION
    coll['identity_reconciliation']='GIS FID 663 PMUC is the separate hotel wing/Union Club Hotel addition; it is not the main PMU. Purdue identifies it as a 1929-1953 hotel addition; official map labels PMU and PMUC separately.'
    scene=bpy.data.scenes.get(SCENE) or bpy.context.scene
    # ensure scene exists by using the named scene if carried by source file
    scene.name=SCENE
    scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world.color=(0.055,0.055,0.055)
    scene.render.film_transparent=False
    # build inventory and geometry metadata, before save.
    bpy.context.view_layer.update()
    scene['asset_id']=ASSET_ID; scene['source_fid']=663; scene['source_name']=attrs.get('BUILDING_N')
    scene['estimated_height_m']=21.75; scene['source_height_interpretation']='Extrution=72 may indicate about 21.95 m if feet; units undocumented; model ridge is an estimate.'; scene['story_count_from_gis']=7
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps({'saved':str(ASSET),'vertices':n,'objects':len(coll.objects),'source_footprint_bounds_m':[[min(x for x,y in points),max(x for x,y in points)],[min(y for x,y in points),max(y for x,y in points)]],'estimated_modeled_z_bounds_m':[0,21.75],'floor_levels_m':floor_z,'source_fid':attrs['FID']}))

if __name__=='__main__': main()
