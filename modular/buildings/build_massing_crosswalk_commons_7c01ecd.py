import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'audit' / 'crosswalk_commons'
SRC = EVIDENCE / 'sources' / 'osm_way_231217849_full.json'
ASSET = ROOT / 'modular' / 'buildings' / 'massing_crosswalk_commons_7c01ecd.blend'
OBJECT_NAME = 'Crosswalk Commons'
COLLECTION_NAME = 'Asset_massing_crosswalk_commons_7c01ecd'
SCENE_NAME = 'Building_massing_crosswalk_commons_7c01ecd'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137

# Source-supported campus outline from OSM way 231217849. This uses the project’s
# approximate local conversion and intentionally keeps the original world frame.
def read_footprint():
    data = json.loads(SRC.read_text(encoding='utf-8-sig'))
    way = next(e for e in data['elements'] if e['type'] == 'way' and e['id'] == 231217849)
    nodes = {e['id']: e for e in data['elements'] if e['type'] == 'node'}
    points = []
    for node_id in way['nodes'][:-1]:
        n = nodes[node_id]
        x = (n['lon'] + 86.9137) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
        y = (n['lat'] - ORIGIN_LAT) * 111040.0
        points.append((x, y))
    return points, way

class MeshBuilder:
    def __init__(self):
        self.verts=[]; self.faces=[]; self.material_ids=[]
    def face(self, pts, mat):
        start=len(self.verts); self.verts.extend(tuple(p) for p in pts)
        self.faces.append(tuple(range(start,start+len(pts))))
        self.material_ids.append(mat)
    def oriented_box(self, center, u, n, dims, mat):
        # local axes: u along wall, n outward, z vertical
        c=Vector(center); u=Vector((u[0],u[1],0)).normalized(); n=Vector((n[0],n[1],0)).normalized()
        hu,hn,hz=(dims[0]/2,dims[1]/2,dims[2]/2)
        pts=[]
        for zsgn in (-1,1):
            z=c.z+zsgn*hz
            for usgn,nsgn in ((-1,-1),(1,-1),(1,1),(-1,1)):
                q=c + usgn*hu*u + nsgn*hn*n
                pts.append((q.x,q.y,z))
        self.face((pts[0],pts[1],pts[2],pts[3]),mat)
        self.face((pts[4],pts[7],pts[6],pts[5]),mat)
        for i in range(4): self.face((pts[i],pts[(i+1)%4],pts[(i+1)%4+4],pts[i+4]),mat)
    def prism(self, ring, z0, z1, side_mat, top_mat):
        n=len(ring)
        for i in range(n):
            a=ring[i]; b=ring[(i+1)%n]
            self.face(((a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)),side_mat)
        self.face([(x,y,z1) for x,y in ring],top_mat)
        self.face([(x,y,z0) for x,y in reversed(ring)],side_mat)

def mat(name,color,roughness=0.75,metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1.0); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1.0)
    bs.inputs['Roughness'].default_value=roughness; bs.inputs['Metallic'].default_value=metallic
    return m

def main():
    # Start from an asset-only scene; retain the stable scene/collection contract.
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing, do_unlink=True)
    ring, way=read_footprint()
    # Signed-area winding: for CCW rings, the exterior is to the right of each edge.
    area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
    ccw=area>0
    b=MeshBuilder()
    # A three-level residential envelope (height is estimated from visible storeys,
    # not measured). Roof and parapet stay simple because the source images show no
    # roof equipment or detailed roof silhouette.
    floor0, floor1, floor2, roof = 0.0, 3.25, 6.20, 9.15
    b.prism(ring,floor0,floor1,1,1)  # stone-heavy ground level visible in operator photos
    b.prism(ring,floor1,floor2,2,1)  # siding middle level
    b.prism(ring,floor2,roof,2,1)    # siding upper level
    # Add the architect/operator-photo-supported brick panels, stone entry portal,
    # dark canopy, and repetitive white-trimmed windows along the longer facades.
    long_edges=[]
    for i in range(len(ring)):
        a=ring[i]; c=ring[(i+1)%len(ring)]
        dx,dy=c[0]-a[0],c[1]-a[1]; length=math.hypot(dx,dy)
        if length<6.0: continue
        u=(dx/length,dy/length)
        n=(u[1],-u[0]) if ccw else (-u[1],u[0])
        long_edges.append((a,c,u,n,length,i))
        # Dark metal fascia line wraps the primary block above the ground floor.
        b.oriented_box(((a[0]+c[0])/2+n[0]*0.06,(a[1]+c[1])/2+n[1]*0.06,3.30),u,n,(length,0.14,0.24),6)
        # Select vertical window modules; avoid corner offsets and retain even rhythm.
        count=max(3,int((length-4.0)//4.1)+1)
        margin=(length-(count-1)*4.1)/2
        for k in range(count):
            s=margin+k*4.1
            center=(a[0]+u[0]*s+n[0]*0.055,a[1]+u[1]*s+n[1]*0.055)
            for zc,wh in ((1.92,(1.35,1.55)),(4.80,(1.30,1.55)),(7.72,(1.30,1.55))):
                ww,hh=wh
                # Ground floor combines tall storefront-like lounge glazing with
                # smaller windows on the opposite/service facade.
                if zc<2.5: ww,hh=2.25,2.25
                b.oriented_box((center[0],center[1],zc),u,n,(ww+0.22,0.10,hh+0.22),3)
                b.oriented_box((center[0],center[1],zc),u,n,(ww,0.13,hh),4)
        # Narrow brick accent panels between selected upper windows, supported by
        # operator images showing red-brick facade blocks amongst light siding.
        for frac in (0.27,0.73):
            s=length*frac
            center=(a[0]+u[0]*s+n[0]*0.035,a[1]+u[1]*s+n[1]*0.035)
            b.oriented_box((center[0],center[1],6.0),u,n,(2.1,0.08,5.9),1)
        # Brick pilasters frame portions of the glazed public-facing ground level.
        for frac in (0.18,0.38,0.62,0.82):
            s=length*frac
            center=(a[0]+u[0]*s+n[0]*0.04,a[1]+u[1]*s+n[1]*0.04)
            b.oriented_box((center[0],center[1],1.68),u,n,(0.52,0.12,3.12),0)
    # Main entry is represented as a modest stone-clad portal and flat canopy on a
    # long facade. Its precise side/position is not documented, so this is marked
    # approximate in the evidence record and kept visually subordinate.
    a,c,u,n,length,edge_index=max(long_edges,key=lambda e:e[4])
    s=length*0.28
    ec=(a[0]+u[0]*s,a[1]+u[1]*s)
    b.oriented_box((ec[0]+n[0]*0.22,ec[1]+n[1]*0.22,1.65),u,n,(4.2,0.48,3.25),5)
    b.oriented_box((ec[0]+n[0]*0.50,ec[1]+n[1]*0.50,3.35),u,n,(5.2,1.55,0.30),6)
    b.oriented_box((ec[0]+n[0]*0.52,ec[1]+n[1]*0.52,1.45),u,n,(1.55,0.14,2.4),4)
    # Small dark parapet edge as a 0.35 m band around roof perimeter.
    b.prism(ring,roof,roof+0.35,6,1)

    mesh=bpy.data.meshes.new('Crosswalk_Commons_SourceDriven_Mesh')
    mesh.from_pydata(b.verts,[],b.faces); mesh.update()
    obj=bpy.data.objects.new(OBJECT_NAME,mesh)
    materials=[
      mat('Warm red brick',(.43,.16,.13)),
      mat('Neutral light stone',(.57,.52,.43)),
      mat('Warm beige horizontal siding',(.70,.65,.55)),
      mat('Pale window trim',(.82,.82,.77)),
      mat('Reflective dark glazing',(.12,.22,.27),.27),
      mat('Dark entry frame',(.13,.15,.16),.35),
      mat('Dark metal canopy and parapet',(.19,.20,.20),.42,.15),
    ]
    for m in materials: mesh.materials.append(m)
    for p,mid in zip(mesh.polygons,b.material_ids): p.material_index=mid
    # Ensure exactly one named building mesh in its stable exported collection.
    for col in list(bpy.data.collections):
        if col.name != 'Collection': bpy.data.collections.remove(col)
    col=bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    col.objects.link(obj)
    sc=bpy.context.scene; sc.name=SCENE_NAME
    sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1.0
    sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1000; sc.render.resolution_y=800; sc.render.resolution_percentage=100
    # Render an evidence preview, then remove camera/lights before saving the modular asset.
    cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
    bpy.ops.object.camera_add(location=(cx-82,cy-100,46)); cam=bpy.context.object
    cam.name='Crosswalk_preview_camera'; cam.data.lens=56
    direction=Vector((cx,cy,4.3))-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); sc.camera=cam
    bpy.ops.object.light_add(type='AREA', location=(cx-45,cy-50,65)); light=bpy.context.object; light.data.energy=18000; light.data.shape='DISK'; light.data.size=65
    light.rotation_euler=(Vector((cx,cy,4))-light.location).to_track_quat('-Z','Y').to_euler()
    sc.world.color=(0.38,0.42,0.48)
    sc.world.use_nodes=True
    background=sc.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value=(0.38,0.42,0.48,1.0)
    background.inputs['Strength'].default_value=0.8
    sc.view_settings.look='AgX - Medium High Contrast'
    sc.view_settings.exposure=1.2
    sc.render.filepath=str(EVIDENCE/'previews'/'crosswalk_commons_three_quarter.png')
    bpy.ops.render.render(write_still=True)
    # A second exterior view makes the approximate entrance treatment inspectable.
    entry_target=Vector((ec[0],ec[1],4.4))
    bpy.ops.object.camera_add(location=(ec[0]+n[0]*72,ec[1]+n[1]*72,30)); entry_cam=bpy.context.object
    entry_cam.name='Crosswalk_entry_preview_camera'; entry_cam.data.lens=56
    entry_cam.rotation_euler=(entry_target-entry_cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=entry_cam
    sc.render.filepath=str(EVIDENCE/'previews'/'crosswalk_commons_entry_view.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(entry_cam,do_unlink=True)
    bpy.data.objects.remove(cam,do_unlink=True); bpy.data.objects.remove(light,do_unlink=True); sc.camera=None
    # Recreate the final empty-object presentation and save.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    dims=list(obj.dimensions)
    report={
      'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'scene':sc.name,
      'collection':col.name,'objects':[obj.name],'object_count':1,
      'footprint_osm_way':way['id'],'footprint_vertex_count':len(ring),
      'footprint_signed_area_m2_approx':round(abs(area),3),
      'footprint_bounds_world_m':[[min(x for x,y in ring),max(x for x,y in ring)],[min(y for x,y in ring),max(y for x,y in ring)]],
      'envelope_dimensions_m':dims,'estimated_floor_count':3,'estimated_roof_z_m':round(roof+0.35,2),
      'orientation':'OSM polygon orientation retained in campus world coordinates; project approximate conversion',
      'entry_orientation':'approximate placement on longest OSM edge; exact side and position unverified',
      'height_uncertainty':'estimated from three visible storeys; no measured elevation or roof height located',
      'source_timestamp':way.get('timestamp')
    }
    (EVIDENCE/'build_evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
