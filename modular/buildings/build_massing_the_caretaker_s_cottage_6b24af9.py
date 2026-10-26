"""Build Rossen's Caretaker's Cottage massing from preserved named OSM and Indiana LiDAR footprints.
Run from the PurdueBlender root with Blender 5.2: blender --background --python this_file.py
Vertical dimensions and facade locations are estimates from qualitative imagery, never survey measurements.
"""
from __future__ import annotations
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'massing_the_caretaker_s_cottage_6b24af9'
SRC=AUDIT/'sources'
ASSET_ID='massing_the_caretaker_s_cottage_6b24af9'
ASSET=ROOT/'modular'/'buildings'/f'{ASSET_ID}.blend'
SCENE='Building_'+ASSET_ID
COLL='Asset_'+ASSET_ID
OBJ="The Caretaker's Cottage"
ORIGIN_LAT=40.4274; ORIGIN_LON=-86.9137

def xy(lon,lat):
    return ((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)),(lat-ORIGIN_LAT)*111040.0)

def load_osm_ring():
    data=json.loads((SRC/'osm_full_953041335.json').read_text(encoding='utf-8'))
    nodes={e['id']:(e['lon'],e['lat']) for e in data['elements'] if e['type']=='node'}
    way=next(e for e in data['elements'] if e['type']=='way' and e['id']==953041335)
    coords=[xy(*nodes[n]) for n in way['nodes']]
    if math.dist(coords[0],coords[-1])<.001: coords.pop()
    if len(coords)!=10: raise RuntimeError(f'Expected 10 OSM footprint vertices, found {len(coords)}')
    return coords

def load_lidar_ring():
    data=json.loads((SRC/'indiana_lidar_footprints_433415.json').read_text(encoding='utf-8'))
    ring=data['features'][0]['geometry']['rings'][0]
    if len(ring)>1 and ring[0]==ring[-1]: ring=ring[:-1]
    return [xy(lon,lat) for lon,lat in ring]

def triangulate_simple_polygon(points):
    """Ear-clip a simple polygon in 2D and return index triples."""
    area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2
    orient=1 if area>0 else -1;ids=list(range(len(points)));tris=[]
    def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def inside(p,a,b,c):
        q=(cross(a,b,p)*orient,cross(b,c,p)*orient,cross(c,a,p)*orient)
        return min(q)>=-1e-9
    guard=0
    while len(ids)>3 and guard<len(points)*len(points):
        guard+=1;found=False
        for k,i in enumerate(ids):
            ia=ids[k-1];ic=ids[(k+1)%len(ids)];a,b,c=points[ia],points[i],points[ic]
            if cross(a,b,c)*orient<=1e-9: continue
            if any(inside(points[j],a,b,c) for j in ids if j not in (ia,i,ic)): continue
            tris.append((ia,i,ic));ids.pop(k);found=True;break
        if not found: raise RuntimeError('LiDAR roof outline could not be triangulated')
    if len(ids)==3: tris.append(tuple(ids))
    return tris

def clear_scene():
    if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name!='Collection': bpy.data.collections.remove(c)
    base=bpy.data.collections.get('Collection')
    if base: bpy.data.collections.remove(base)
    for s in list(bpy.data.scenes):
        if s.name!='Scene': bpy.data.scenes.remove(s)
    scene=bpy.data.scenes.get('Scene') or bpy.context.scene
    scene.name=SCENE
    col=bpy.data.collections.new(COLL); scene.collection.children.link(col)
    return scene,col

def mat_stone():
    m=bpy.data.materials.new('Bedford_Limestone_Rubble');m.diffuse_color=(.42,.38,.31,1);m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.2;noise.inputs['Detail'].default_value=4.0;noise.inputs['Roughness'].default_value=.78;noise.inputs['Distortion'].default_value=.25
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.10,.085,.065,1);ramp.color_ramp.elements[1].position=.83;ramp.color_ramp.elements[1].color=(.66,.57,.45,1)
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.40;bump.inputs['Distance'].default_value=.14
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color']);l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    p.inputs['Roughness'].default_value=.82
    return m

def simple_mat(name,color,rough=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
    return m

def roof_mat():
    m=simple_mat('Terracotta_Roof_Tile',(.42,.105,.035),.66)
    n=m.node_tree.nodes;l=m.node_tree.links;p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(30,10,1)
    brick=n.new('ShaderNodeTexBrick');brick.inputs['Color1'].default_value=(.56,.16,.055,1);brick.inputs['Color2'].default_value=(.40,.085,.028,1)
    brick.inputs['Mortar'].default_value=(.22,.08,.035,1);brick.inputs['Scale'].default_value=1.0
    brick.inputs['Mortar Size'].default_value=.018;brick.inputs['Mortar Smooth'].default_value=.01
    brick.inputs['Brick Width'].default_value=.28;brick.inputs['Row Height'].default_value=.18
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.28;bump.inputs['Distance'].default_value=.04
    l.new(tex.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs['Vector'],brick.inputs['Vector'])
    l.new(brick.outputs['Color'],p.inputs['Base Color']);l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m

def mesh_obj(name,verts,faces,material,col):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob)
    return ob

def prism(name,center,axes,dims,material,col):
    # rectangular solid in local tangent/normal/vertical axes, dims=(width,depth,height)
    c=Vector(center);u=Vector(axes[0]).normalized();v=Vector(axes[1]).normalized();z=Vector((0,0,1));w,d,h=dims
    verts=[]
    for zz in (-h/2,h/2):
        for yy in (-d/2,d/2):
            for xx in (-w/2,w/2):verts.append(tuple(c+u*xx+v*yy+z*zz))
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)]
    return mesh_obj(name,verts,faces,material,col)

def box(name,center,size,material,col):
    x,y,z=center;dx,dy,dz=[v/2 for v in size]
    verts=[(x+sx*dx,y+sy*dy,z+sz*dz) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh_obj(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],material,col)

def make_roofbar(name,center,theta,xmin,xmax,ymin,ymax,eave,ridge,roofmat,col,overhang=.35):
    u=Vector((math.cos(theta),math.sin(theta),0));v=Vector((-math.sin(theta),math.cos(theta),0));c=Vector((center[0],center[1],0))
    xmin-=overhang;xmax+=overhang;ymin-=overhang;ymax+=overhang
    half=(ymax-ymin)/2
    ridge_start=xmin+half*.72;ridge_end=xmax-half*.72;ymid=(ymin+ymax)/2
    def point(x,y,z): return tuple(c+u*x+v*y+Vector((0,0,z)))
    # Hipped ends and long tiled planes approximate the intersecting historic roof; proportions are estimated.
    verts=[point(xmin,ymin,eave),point(xmax,ymin,eave),point(xmin,ymax,eave),point(xmax,ymax,eave),
           point(ridge_start,ymid,ridge),point(ridge_end,ymid,ridge)]
    faces=[(0,1,5,4),(4,5,3,2),(0,4,2),(1,3,5),(0,2,3,1)]
    ob=mesh_obj(name,verts,faces,roofmat,col)
    return ob
def main():
    footprint=load_osm_ring(); lidar_ring=load_lidar_ring()
    # Source ring signed area; ensure stable wall normal selection later.
    cx=sum(x for x,y in footprint)/len(footprint);cy=sum(y for x,y in footprint)/len(footprint)
    theta=math.radians(40.0) # OSM long roof axis approximately NE-SW, qualitative alignment from orthophoto
    u=Vector((math.cos(theta),math.sin(theta),0));v=Vector((-math.sin(theta),math.cos(theta),0));c=Vector((cx,cy,0))
    local=[((Vector((x,y,0))-c).dot(u),(Vector((x,y,0))-c).dot(v)) for x,y in footprint]
    xmin=min(x for x,y in local);xmax=max(x for x,y in local);ymin=min(y for x,y in local);ymax=max(y for x,y in local)
    scene,col=clear_scene()
    stone=mat_stone(); roof=roof_mat(); trim=simple_mat('Warm_Limestone_Trim',(.63,.56,.45)); glass=simple_mat('Smoked_Glass',(.12,.20,.22),.25); dark=simple_mat('Dark_Wood',(.16,.075,.035)); concrete=simple_mat('Restored_Concrete',(.50,.48,.43)); wood=simple_mat('Painted_Wood_Trim',(.22,.14,.08))
    wall_h=3.35; roof_eave=3.48; roof_ridge=5.55
    # Structural shell follows the named OSM perimeter: exact campus mapping, one-story stone cottage.
    verts=[]
    for z in (0.0,wall_h): verts += [(x,y,z) for x,y in footprint]
    n=len(footprint);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    body=mesh_obj(OBJ,verts,faces,stone,col)
    body['source']='OSM way 953041335, The Caretaker’s Cottage; campus coordinates from project local lon/lat conversion'
    body['height_note']='Wall top 3.35 m and roof ridge 5.55 m are visual estimates; no measured elevation found.'
    # Use the independent LiDAR outline as a stepped roof-envelope control;
    # OSM remains the structural wall/base shell. The low infill closes aerially
    # supported roof areas between the three articulated hipped roof volumes.
    lidarlocal=[((Vector((x,y,0))-c).dot(u),(Vector((x,y,0))-c).dot(v)) for x,y in lidar_ring]
    roofpts=[(cx+u.x*x+v.x*y,cy+u.y*x+v.y*y) for x,y in lidarlocal]
    apronverts=[(x,y,roof_eave-.025) for x,y in roofpts]
    mesh_obj('Terracotta_Roof_Envelope_Infill',apronverts,triangulate_simple_polygon(lidarlocal),roof,col)
    # These stepped ranges follow the two long roof wings and the narrower
    # connecting zone visible in the 2017 photograph and orthophoto outline.
    # Roof heights and intersections remain qualitative estimates.
    make_roofbar('North_Terracotta_Hipped_Roof',(cx,cy),theta,-9.75,7.82,.62,9.35,roof_eave,roof_ridge,roof,col)
    make_roofbar('South_Terracotta_Hipped_Roof',(cx,cy),theta,-6.90,3.72,-6.00,-.82,roof_eave,roof_ridge-.16,roof,col)
    make_roofbar('Stepped_Connector_Terracotta_Roof',(cx,cy),theta,-6.50,3.76,-1.08,.78,roof_eave,4.05,roof,col,overhang=.04)
    # Select the longest shell edge facing southwest (toward N Salisbury St in the aerial); porch location is qualitative.
    road=Vector((-0.84,-0.54,0)).normalized(); best=None
    for i,a in enumerate(footprint):
        b=footprint[(i+1)%n];d=Vector((b[0]-a[0],b[1]-a[1],0));length=d.length
        if length<3: continue
        tangent=d.normalized();normal=Vector((-tangent.y,tangent.x,0));mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,0));out=(mid-c).normalized()
        # prefer wall facing the access road, with length as a weak tie-breaker
        score=out.dot(road)+min(length,8)*.005
        if best is None or score>best[0]:best=(score,i,a,b,tangent,out,length)
    _,edge_i,a,b,tan,out,edge_len=best
    porch_len=min(6.4,edge_len*.84);porch_depth=1.65
    edge_mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,0));porch_center=edge_mid+out*(porch_depth/2-.12)
    # Elevated double-porch interpretation: front porch plus a short return around the adjacent wall.
    deck_z=.32
    prism('Front_Porch_Stone_Deck',(porch_center.x,porch_center.y,deck_z/2), (tuple(tan),tuple(out)),(porch_len,porch_depth,deck_z),trim,col)
    for s in (-1,0,1):
        q=porch_center+tan*(s*porch_len/2)+out*(porch_depth*.38)+Vector((0,0,1.65))
        box(f'Front_Porch_Stone_Pier_{s}',tuple(q),(.68,.68,2.72),stone,col)
    # Beam and shallow pitched cover along the porch frontage.
    beamcenter=porch_center+out*(porch_depth*.38)+Vector((0,0,2.95))
    prism('Front_Porch_Beam',tuple(beamcenter),(tuple(tan),tuple(out)),(porch_len+.35,.20,.24),trim,col)
    # Low limestone porch walls link the heavy stone piers, as seen in the library's porch image.
    for side in (-1,1):
        wallcenter=porch_center+out*(porch_depth*.38)+tan*(side*porch_len*.25)+Vector((0,0,.68))
        prism(f'Front_Porch_Low_Stone_Wall_{side}',tuple(wallcenter),(tuple(tan),tuple(out)),(porch_len*.48,.26,.72),stone,col)
    # No separate porch canopy or access ramp is asserted: the 2017 image
    # shows a broad veranda beneath deep eaves, while access details are undocumented.
    # Stone window surrounds and dark recessed panes. Opening positions are photo-guided estimates.
    center2=Vector((cx,cy,0))
    for i,p0xy in enumerate(footprint):
        p1xy=footprint[(i+1)%n];edge=Vector((p1xy[0]-p0xy[0],p1xy[1]-p0xy[1],0));length=edge.length
        if length<3.0: continue
        tangent=edge.normalized(); outward=(Vector(((p0xy[0]+p1xy[0])/2,(p0xy[1]+p1xy[1])/2,0))-center2).normalized()
        count=max(1,min(3,int(length//4.5)))
        for j in range(count):
            along=length*(j+1)/(count+1)
            pos=Vector((p0xy[0],p0xy[1],0))+tangent*along+outward*.035
            # Keep one opening off the primary porch side for an approximate entrance.
            if i==edge_i and abs(along-length/2)<1.15:
                doorc=pos+Vector((0,0,1.22));prism('Entry_Door',tuple(doorc),(tuple(tangent),tuple(outward)),(.92,.10,2.35),dark,col)
                prism('Entry_Door_Limestone_Lintel',tuple(pos+Vector((0,0,2.47))),(tuple(tangent),tuple(outward)),(1.18,.20,.20),trim,col)
                continue
            wc=pos+Vector((0,0,1.95));ww=.88;wh=1.02
            prism(f'Window_{i}_{j}_Glazing',tuple(wc),(tuple(tangent),tuple(outward)),(ww,.075,wh),glass,col)
            for dx in (-1,1):
                fc=wc+tangent*(dx*(ww/2+.055));prism(f'Window_{i}_{j}_Jamb_{dx}',tuple(fc),(tuple(tangent),tuple(outward)),(.11,.15,wh+.24),trim,col)
            for dz in (-1,1):
                fc=wc+Vector((0,0,dz*(wh/2+.055)));prism(f'Window_{i}_{j}_HeadSill_{dz}',tuple(fc),(tuple(tangent),tuple(outward)),(ww+.22,.16,.11),trim,col)
            prism(f'Window_{i}_{j}_Mullion',tuple(wc),(tuple(tangent),tuple(outward)),(.045,.10,wh),wood,col)
    # Create a second, short porch return on the adjoining edge to express the documented double porches.
    side_i=(edge_i+1)%n
    aa=footprint[side_i];bb=footprint[(side_i+1)%n];sidevec=Vector((bb[0]-aa[0],bb[1]-aa[1],0));slen=sidevec.length
    if slen>3:
        st=sidevec.normalized();so=(Vector(((aa[0]+bb[0])/2,(aa[1]+bb[1])/2,0))-center2).normalized();slen=min(3.8,slen*.56);sm=Vector(((aa[0]+bb[0])/2,(aa[1]+bb[1])/2,0))+so*.68
        prism('Return_Porch_Stone_Deck',(sm.x,sm.y,.15),(tuple(st),tuple(so)),(slen,1.35,.30),trim,col)
        for s in (-1,1): box(f'Return_Porch_Stone_Pier_{s}',tuple(sm+st*(s*slen*.42)+so*.42+Vector((0,0,1.55))),(.48,.48,2.45),stone,col)
    # Neighborhood-independent studio set, kept outside the exported asset collection.
    studio=bpy.data.collections.new('Presentation_Only');scene.collection.children.link(studio)
    world=bpy.data.worlds.new('Soft_Studio_World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.34,.38,.42,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
    def camera(name,loc,target,ortho):
        dat=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,dat);studio.objects.link(ob);ob.location=loc;direction=Vector(target)-ob.location;ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();dat.type='ORTHO';dat.ortho_scale=ortho;return ob
    def light(name,loc,power,size):
        dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;ob=bpy.data.objects.new(name,dat);studio.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((cx,cy,2.5))-ob.location).to_track_quat('-Z','Y').to_euler()
    light('Key_Area',(cx-12,cy-13,20),2200,12);light('Fill_Area',(cx+14,cy+8,14),1100,10)
    available=[item.identifier for item in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items];scene.render.engine='BLENDER_EEVEE' if 'BLENDER_EEVEE' in available else available[0];scene.render.resolution_x=1100;scene.render.resolution_y=820;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX';scene.render.resolution_percentage=100
    target=(cx,cy,2.6);renderdir=AUDIT/'renders';renderdir.mkdir(parents=True,exist_ok=True)
    views=[('top',(cx,cy,32),35),('street_oblique',(cx-18,cy-18,13),26),('north_oblique',(cx+16,cy+18,12),26),('side_oblique',(cx+20,cy-14,12),26)]
    for name,loc,scale in views:
        cam=camera('Camera_'+name,loc,target,scale);scene.camera=cam;scene.render.filepath=str(renderdir/(name+'.png'));bpy.ops.render.render(write_still=True);camdata=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
    # Keep presentation objects in scene but out of the exported asset collection; no external textures.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps({'asset':str(ASSET),'scene':SCENE,'collection':COLL,'collection_objects':len(col.objects),'wall_height_estimate_m':wall_h,'roof_ridge_estimate_m':roof_ridge,'footprint_vertices':len(footprint),'saved_renders':[str(p) for p in sorted(renderdir.glob('*.png'))]},indent=2))

if __name__=='__main__': main()







