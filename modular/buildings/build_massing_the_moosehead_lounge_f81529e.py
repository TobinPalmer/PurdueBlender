"""Build a source-grounded campus-coordinate massing for The Moosehead Lounge.

Identity is matched to OSM way 910910470 at 434 N Grant St and the named site
on the City of West Lafayette's 2026 closure map. Purdue's CampusBuilding layer
has no name match. FID 855 is excluded because it maps to the Old Purdue
Exponent Building. The Indiana LiDAR polygon 409924 overlaps but extends over
an adjacent roof; it is recorded as a conflicting/merged geometry, not used as
the target outline. The OSM outline is registered against the Indiana current
orthophoto image. That image shows multiple roof planes, modeled conservatively
as two gabled roof zones with terminal gable-end wall faces. Exact seams and
all vertical dimensions are estimates. Facade windows are omitted because no
direct facade photo or elevation was identified.
"""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_the_moosehead_lounge_f81529e"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / ASSET_ID
SOURCES = AUDIT / "sources"
RENDERS = AUDIT / "renders"
OSM = SOURCES / "osm_way_910910470_full.json"
SCENE_NAME = "Building_massing_the_moosehead_lounge_f81529e"
COLLECTION_NAME = "Asset_massing_the_moosehead_lounge_f81529e"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
EAVE_Z = 5.25  # estimate; no reliable measured elevation source found
RIDGE_Z = 7.60  # estimate retained from the inherited massing ceiling

class MeshBuilder:
    def __init__(self):
        self.v=[]; self.f=[]; self.mi=[]; self.cache={}
    def face(self, pts, mat):
        ids=[]
        for p in pts:
            key=tuple(round(float(q),6) for q in p)
            i=self.cache.get(key)
            if i is None:
                i=len(self.v); self.cache[key]=i; self.v.append(key)
            ids.append(i)
        if len(set(ids))>=3:
            self.f.append(tuple(ids)); self.mi.append(mat)
    def box(self,center, width,depth,height, angle, mats, material=0):
        # rectangular detail aligned to its wall; the front is displaced along local +Y
        c=Vector(center); t=Vector((math.cos(angle), math.sin(angle),0)); n=Vector((-t.y,t.x,0))
        dx,dy,dz=width/2,depth/2,height/2
        corners=[c+t*(sx*dx)+n*(sy*dy)+Vector((0,0,sz*dz)) for sx,sy,sz in
                 ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
        for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            self.face([corners[j] for j in face],material)

def local_xy(lon,lat):
    return ((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)),(lat-ORIGIN_LAT)*111040.0)

def mat(name,color,roughness=.82,metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*color,1); s.inputs['Roughness'].default_value=roughness
    if 'Metallic' in s.inputs: s.inputs['Metallic'].default_value=metallic
    return m

def clip_half(poly,ymid,keep_south):
    # Sutherland-Hodgman clipping against the north/south half-plane.
    out=[]
    def inside(p): return p[1] <= ymid+1e-8 if keep_south else p[1] >= ymid-1e-8
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia,ib=inside(a),inside(b)
        if ia and ib: out.append(b)
        elif ia and not ib:
            t=(ymid-a[1])/(b[1]-a[1]); out.append((a[0]+t*(b[0]-a[0]),ymid))
        elif not ia and ib:
            t=(ymid-a[1])/(b[1]-a[1]); out.append((a[0]+t*(b[0]-a[0]),ymid)); out.append(b)
    # dedupe adjacent points
    clean=[]
    for p in out:
        if not clean or math.dist(p,clean[-1])>1e-6: clean.append(p)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-6: clean.pop()
    return clean

def clip_x(poly,xmid,keep_west):
    """Clip a polygon at a west/east split while preserving its source outline."""
    out=[]
    def inside(p): return p[0] <= xmid+1e-8 if keep_west else p[0] >= xmid-1e-8
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia,ib=inside(a),inside(b)
        if ia and ib: out.append(b)
        elif ia and not ib:
            t=(xmid-a[0])/(b[0]-a[0]); out.append((xmid,a[1]+t*(b[1]-a[1])))
        elif not ia and ib:
            t=(xmid-a[0])/(b[0]-a[0]); out.append((xmid,a[1]+t*(b[1]-a[1]))); out.append(b)
    clean=[]
    for p in out:
        if not clean or math.dist(p,clean[-1])>1e-6: clean.append(p)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-6: clean.pop()
    return clean

def main():
    raw=json.loads(OSM.read_text(encoding='utf-8'))
    elems=raw['elements']; nodes={e['id']:e for e in elems if e['type']=='node'}
    way=next(e for e in elems if e['type']=='way' and e['id']==910910470)
    tags=way.get('tags',{})
    assert tags.get('name')=='The Moosehead Lounge' and tags.get('addr:housenumber')=='434'
    ring=[local_xy(nodes[i]['lon'],nodes[i]['lat']) for i in way['nodes'][:-1]]
    # Remove repeated points if present.
    pts=[]
    for p in ring:
        if not pts or math.dist(p,pts[-1])>0.0001: pts.append(p)
    if len(pts)>2 and math.dist(pts[0],pts[-1])<0.0001: pts.pop()
    if len(pts)<3: raise ValueError('OSM footprint ring is degenerate')
    minx,maxx=min(x for x,y in pts),max(x for x,y in pts); miny,maxy=min(y for x,y in pts),max(y for x,y in pts)
    cx,cy=(minx+maxx)/2,(miny+maxy)/2

    # Start with a clean file and preserve the existing scene/collection identity.
    bpy.ops.wm.read_homefile(use_empty=True)
    scene=bpy.context.scene; scene.name=SCENE_NAME
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0; scene.unit_settings.length_unit='METERS'
    scene['building_id']=ASSET_ID; scene['official_name']='The Moosehead Lounge'
    scene['address']='434 North Grant Street, West Lafayette, IN 47906'
    scene['identity_source']='OpenStreetMap way 910910470; City of West Lafayette BPW map dated 2026-02-19 labels Moosehead Lounge at this location.'
    scene['excluded_candidate']='Assignment-queue FID 855 resolves to Old Purdue Exponent Building; excluded. Purdue campus GIS name query returned no Moosehead record.'
    scene['height_status']='Estimated: 5.25 m eave and 7.60 m ridge. No measured height or elevation source found.'
    scene['roof_status']='Two-zone gabled roof silhouette (west/north body and east/south wing) follows visible roof-plane breaks in 2022-2025 Indiana orthophoto and OSM footprint projections. Gable-end wall faces close west and east terminal profiles. Exact roof seam positions, ridge directions, and all heights remain interpreted estimates, not survey measurements.'
    scene['geometry_iteration']='r2: removed unsupported repeated windows, sill bands, and trim; retained only three OSM-mapped level-0 entry positions as schematic plain doors; split broad single roof into west/north and east/south gabled zones; added west/east gable-end wall faces; preserved exact OSM 910910470 structural ring.'
    scene['footprint_status']='OSM way 910910470 at 434 N Grant St agrees with assigned manifest bbox and city named-site map. In the documented local projection, Indiana 2018 polygon 409924 overlaps 228.73 m2 of the OSM outline area (242.12 m2; 94.45%), but the Indiana polygon is 601.70 m2 overall and only 38.01% is shared; it includes adjacent southern roof and is not treated as the exact target footprint.'
    coll=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(coll)
    mb=MeshBuilder()
    wall_mat=mat('Muted warm masonry — generic material, facade unverified',(0.40,0.30,0.24),.9)
    roof_mat=mat('Weathered charcoal roof',(0.12,0.14,0.16),.88)
    door_mat=mat('Entry doors — schematic',(0.20,0.12,0.075),.74)
    # Exposed wall shell follows the OSM ring exactly.
    for a,b in zip(pts,pts[1:]+pts[:1]):
        mb.face([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],EAVE_Z),(a[0],a[1],EAVE_Z)],0)
    # The orthophoto shows distinct roof-plane zones. Split at the projected
    # break beside the east/south wing; the exact seam and both ridge heights
    # remain estimates. Preserve the source polygon as the outer roof limit.
    roof_split_x=310.95
    roof_sections=[]
    for section_name,keep_west in (("west_north",True),("east_south",False)):
        roofpoly=clip_x(pts,roof_split_x,keep_west)
        if len(roofpoly)<3: continue
        sec_min_y=min(y for x,y in roofpoly); sec_max_y=max(y for x,y in roofpoly)
        ridge_y=(sec_min_y+sec_max_y)/2
        half=max(ridge_y-sec_min_y,sec_max_y-ridge_y)
        roof_sections.append({"name":section_name,"plan_vertices":len(roofpoly),"plan_y_bounds_local_m":[sec_min_y,sec_max_y],"ridge_y_local_m_estimated":ridge_y,"eave_z_m_estimated":EAVE_Z,"ridge_z_m_estimated":RIDGE_Z})
        for south in (True,False):
            roof_half=clip_half(roofpoly,ridge_y,south)
            if len(roof_half)<3: continue
            vectors=[Vector((x,y,0)) for x,y in roof_half]
            for tri in tessellate_polygon([vectors]):
                face=[]
                for i in tri:
                    x,y=roof_half[i]
                    z=EAVE_Z+(RIDGE_Z-EAVE_Z)*(1.0-min(1.0,abs(y-ridge_y)/max(half,1e-6)))
                    face.append((x,y,z))
                mb.face(face,1)

    # Close the roof-step seam where the orthophoto-based roof zones change
    # ridge position. This narrow vertical party/gable volume fills only the
    # height difference between the two roof profiles at their shared split.
    west_sec,east_sec=roof_sections
    def roof_profile_z(y,sec):
        lo,hi=sec["plan_y_bounds_local_m"]
        ridge_y=sec["ridge_y_local_m_estimated"]
        half=max(ridge_y-lo,hi-ridge_y)
        return EAVE_Z+(RIDGE_Z-EAVE_Z)*(1.0-min(1.0,abs(y-ridge_y)/max(half,1e-6)))
    cut_y=[]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if abs(a[0]-b[0])<1e-9:
            if abs(a[0]-roof_split_x)<1e-6: cut_y.extend((a[1],b[1]))
        elif min(a[0],b[0])-1e-8 <= roof_split_x <= max(a[0],b[0])+1e-8:
            t=(roof_split_x-a[0])/(b[0]-a[0]); cut_y.append(a[1]+t*(b[1]-a[1]))
    cut_y=sorted(set(round(y,8) for y in cut_y))
    for interval in range(0,len(cut_y)-1,2):
        lo,hi=cut_y[interval],cut_y[interval+1]
        seam_y=sorted(set([lo,hi]+[sec["ridge_y_local_m_estimated"] for sec in (west_sec,east_sec) if lo<sec["ridge_y_local_m_estimated"]<hi]))
        for y0,y1 in zip(seam_y,seam_y[1:]):
            w0,w1=roof_profile_z(y0,west_sec),roof_profile_z(y1,west_sec)
            e0,e1=roof_profile_z(y0,east_sec),roof_profile_z(y1,east_sec)
            if max(abs(w0-e0),abs(w1-e1))>1e-5:
                mb.face([(roof_split_x,y0,w0),(roof_split_x,y1,w1),(roof_split_x,y1,e1),(roof_split_x,y0,e0)],0)

    # Add gable-end wall faces above the eaves at the outer west and east ends.
    # End shapes follow the OSM ring and are schematic volume closures.
    west_points=[p for p in pts if abs(p[0]-minx)<0.05]
    west_low=min(west_points,key=lambda p:p[1]); west_high=max(west_points,key=lambda p:p[1])
    west_mid_y=(west_low[1]+west_high[1])/2
    mb.face([(minx,west_low[1],EAVE_Z),(minx,west_high[1],EAVE_Z),(minx,west_mid_y,RIDGE_Z)],0)
    east_i=max(range(len(pts)),key=lambda i:pts[i][0])
    east_corner=pts[east_i]
    east_neighbors=[pts[(east_i-1)%len(pts)],pts[(east_i+1)%len(pts)]]
    east_end_neighbor=max(east_neighbors,key=lambda p:p[0])
    east_mid=((east_corner[0]+east_end_neighbor[0])/2,(east_corner[1]+east_end_neighbor[1])/2)
    mb.face([(east_corner[0],east_corner[1],EAVE_Z),(east_end_neighbor[0],east_end_neighbor[1],EAVE_Z),(east_mid[0],east_mid[1],RIDGE_Z)],0)

    # No generic windows, facade rhythm, sill bands, or trim without direct
    # facade evidence. Retain only the three OSM-mapped level-0 entrances.
    # OSM main-entrance nodes are the only doorway positions represented. Door construction remains schematic.
    for n in elems:
        if n.get('type')!='node' or n.get('tags',{}).get('entrance')!='main' or n.get('tags',{}).get('level')!='0': continue
        x,y=local_xy(n['lon'],n['lat'])
        # Snap the projected point to nearest outline segment; orient with the local wall tangent.
        best=None
        for a,b in zip(pts,pts[1:]+pts[:1]):
            vx,vy=b[0]-a[0],b[1]-a[1]; l2=vx*vx+vy*vy
            t=max(0,min(1,((x-a[0])*vx+(y-a[1])*vy)/l2))
            q=(a[0]+t*vx,a[1]+t*vy); d=math.dist((x,y),q)
            if best is None or d<best[0]: best=(d,q,math.atan2(vy,vx))
        if best and best[0]<0.7:
            _,q,angle=best
            mb.box((q[0],q[1],1.1),.92,.12,2.2,angle,None,2)
    # One mesh object, matching the assigned simple-massing export convention.
    mesh=bpy.data.meshes.new('Moosehead Lounge source-grounded shell')
    mesh.from_pydata(mb.v,[],mb.f); mesh.update()
    obj=bpy.data.objects.new('The Moosehead Lounge',mesh); coll.objects.link(obj)
    for m in (wall_mat,roof_mat,door_mat): mesh.materials.append(m)
    for poly,mi in zip(mesh.polygons,mb.mi): poly.material_index=mi
    obj['source_footprint']='OSM way 910910470; projected using project approximate origin/scale'
    obj['source_height']='Estimated only; eave 5.25 m, ridge 7.60 m'
    obj['facade_detail_status']='Only three OSM-tagged level-0 entrance positions are represented as plain schematic doors. No windows, facade rhythm, bands, or trim are claimed because no direct facade photo or elevation was identified.'
    obj['roof_sections_json']=json.dumps(roof_sections,sort_keys=True)
    obj['gable_end_faces']=2
    # Render-only environment; excluded from assigned asset collection.
    render_coll=bpy.data.collections.new('00_Render_Only'); scene.collection.children.link(render_coll)
    ground_mat=mat('Render ground',(0.68,0.70,0.70),.95)
    gmesh=bpy.data.meshes.new('Render ground mesh'); gmesh.from_pydata([(cx-25,cy-22,-.18),(cx+25,cy-22,-.18),(cx+25,cy+22,-.18),(cx-25,cy+22,-.18)],[],[(0,1,2,3)]); gmesh.materials.append(ground_mat)
    ground=bpy.data.objects.new('Render ground only',gmesh); render_coll.objects.link(ground)
    def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    cam_data=bpy.data.cameras.new('Inspection camera'); cam=bpy.data.objects.new('Inspection camera',cam_data); render_coll.objects.link(cam); cam_data.type='ORTHO'; cam_data.ortho_scale=46
    scene.camera=cam
    def area(name,loc,energy,size):
        d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size
        o=bpy.data.objects.new(name,d); render_coll.objects.link(o); o.location=loc; aim(o,(cx,cy,3)); return o
    area('Key softbox',(cx-20,cy-20,28),24000,16); area('Fill softbox',(cx+18,cy+12,20),14000,14); area('Rear softbox',(cx+2,cy-22,16),9000,12)
    world=bpy.data.worlds.new('Soft studio') if bpy.data.worlds.get('Soft studio') is None else bpy.data.worlds['Soft studio']; scene.world=world; world.color=(0.22,0.22,0.22)
    scene.render.engine='BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples=48
    scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
    views=[
      ('01_top',(cx,cy,45),(cx,cy,0),42),
      ('02_nw_isometric',(cx-30,cy-32,27),(cx,cy,3),42),
      ('03_grant_street_west',(cx-32,cy,12),(cx,cy,3),40),
      ('04_roof_east',(cx+30,cy+20,22),(cx,cy,3),42),
    ]
    RENDERS.mkdir(parents=True,exist_ok=True)
    for name,loc,target,scale in views:
        cam.location=loc; aim(cam,target); cam_data.ortho_scale=scale; scene.render.filepath=str(RENDERS/f'{name}.png'); bpy.ops.render.render(write_still=True)
    # Save file with view setup, render-only environment separate from asset collection.
    scene.render.filepath='//'
    ASSET_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    result={'building_id':ASSET_ID,'asset':str(ASSET_PATH.relative_to(ROOT)),'scene':SCENE_NAME,'collection':COLLECTION_NAME,'objects_in_asset_collection':len(coll.objects),'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'footprint_vertices':len(pts),'source_way':'OSM way 910910470','campus_bbox_m':[[minx,maxx],[miny,maxy],[0,RIDGE_Z]],'eave_height_m':EAVE_Z,'ridge_height_m':RIDGE_Z,'height_status':'estimated','geometry_iteration':'r2','roof_split_x_local_m_estimated':roof_split_x,'roof_sections':roof_sections,'gable_end_faces':2,'facade_detail_status':'Only OSM-tagged level-0 entrances retained; unsupported windows, facade rhythm, bands, and trim removed.','views':[str((RENDERS/f'{name}.png').relative_to(ROOT)) for name,_,_,_ in views]}
    (AUDIT/'build_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__': print(json.dumps(main(),indent=2))
