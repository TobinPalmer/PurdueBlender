"""Build the Alpha Kappa Lambda massing from independent Purdue and Indiana sources.

Footprint uses Indiana's 2018 LiDAR-derived building polygon (objectid 409920)
transformed with the repository's documented campus approximation. The 2022
AKL magazine photo supports brick walls, pitched roofs, gables, chimney, and
windows; 2022-2025 Indiana orthophoto imagery is used to register the footprint.
Height and the exact roof/wall segmentation remain estimates.
"""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_alpha_kappa_lambda_88dda6c"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "sources" / "purdue_gis_fid784_2026-10-25.json"
LIDAR_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "sources" / "indiana_lidar_building_footprints_at_alpha_kappa_lambda_2026-10-25.json"
PREVIEW_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "alpha_kappa_lambda_preview.png"
RESULT_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "build_result.json"
SCENE_NAME = "Building_massing_alpha_kappa_lambda_88dda6c"
COLLECTION_NAME = "Asset_massing_alpha_kappa_lambda_88dda6c"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
WALL_EAVE_M = 6.2
PRIMARY_RIDGE_M = 9.1
SECONDARY_RIDGE_M = 7.7


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def signed_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1]
                     - points[(i + 1) % len(points)][0] * points[i][1]
                     for i in range(len(points)))


def mat(name, color, roughness=0.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


class MeshBuilder:
    def __init__(self):
        self.vertices, self.faces, self.material_ids = [], [], []
        self.vertex_index = {}

    def face(self, points, material_id):
        indices = []
        for p in points:
            point = tuple(float(c) for c in p)
            # Reuse a single index at each shared coordinate. The 1e-6 m grid
            # only absorbs floating point noise from repeated mathutils.Vector
            # arithmetic; it is far below the source footprint precision.
            key = tuple(round(c, 6) for c in point)
            index = self.vertex_index.get(key)
            if index is None:
                index = len(self.vertices)
                self.vertices.append(point)
                self.vertex_index[key] = index
            indices.append(index)
        self.faces.append(tuple(indices))
        self.material_ids.append(material_id)

    def box(self, center, axes, size, material_id):
        c = Vector(center)
        ax, ay, az = (Vector(a).normalized() for a in axes)
        sx, sy, sz = (v / 2 for v in size)
        corners = [c + ax * (sx*x) + ay * (sy*y) + az * (sz*z)
                   for x, y, z in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                   (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            self.face([corners[i] for i in f], material_id)

    def gable(self, x0, x1, y0, y1, eave, ridge, roof_mat=2):
        """Closed N-S ridge roof prism; gables face the south and north."""
        xm = (x0 + x1) / 2
        # Eaves and peak points
        a=(x0,y0,eave); b=(x1,y0,eave); c=(x1,y1,eave); d=(x0,y1,eave)
        p0=(xm,y0,ridge); p1=(xm,y1,ridge)
        self.face([a,d,c,b], roof_mat)  # underside
        self.face([a,p0,p1,d], roof_mat) # west roof plane
        self.face([p0,b,c,p1], roof_mat) # east roof plane
        self.face([a,b,p0], roof_mat)    # south gable
        self.face([d,p1,c], roof_mat)    # north gable


def main():
    official=json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
    lidar=json.loads(LIDAR_PATH.read_text(encoding="utf-8"))["features"][0]
    assert official["attributes"]["FID"] == 784
    assert official["attributes"]["BUILDING_N"] == "Alpha Kappa Lambda"
    assert official["attributes"]["ADDRESS"] == "417 Waldron St"
    assert lidar["attributes"]["objectid"] == 409920
    assert lidar["attributes"]["lidaryear"] == "2018"
    raw=lidar["geometry"]["rings"][0]
    footprint=[local_xy(lon,lat) for lon,lat in raw[:-1]]
    if signed_area(footprint) < 0:
        footprint.reverse()
    n=len(footprint)
    minx,maxx=min(p[0] for p in footprint),max(p[0] for p in footprint)
    miny,maxy=min(p[1] for p in footprint),max(p[1] for p in footprint)
    cx,cy=(minx+maxx)/2,(miny+maxy)/2

    scene=bpy.context.scene
    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
    for collection in list(bpy.data.collections): bpy.data.collections.remove(collection)
    for other in list(bpy.data.scenes):
        if other != scene: bpy.data.scenes.remove(other)
    scene.name=SCENE_NAME
    asset=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(asset)
    rig=bpy.data.collections.new("Render_Setup"); scene.collection.children.link(rig)
    mats=[
        mat("Warm red-brown brick (2022 chapter-house photo)",(0.40,0.16,0.11)),
        mat("Dark foundation and shadow joints",(0.20,0.20,0.19)),
        mat("Charcoal asphalt shingle roof (photo-backed)",(0.10,0.12,0.13)),
        mat("Off-white window and eave trim",(0.84,0.82,0.76)),
        mat("Blue-gray glazing",(0.15,0.24,0.29),0.27),
        mat("Dark wood entrance door",(0.18,0.10,0.07)),
    ]
    mb=MeshBuilder()
    # GIS perimeter shell; eave is an estimate for a visibly multi-level house.
    bottom=[(x,y,0.0) for x,y in footprint]
    top=[(x,y,WALL_EAVE_M) for x,y in footprint]
    mb.face(list(reversed(bottom)),1)
    for i in range(n):
        j=(i+1)%n
        mb.face([bottom[i],bottom[j],top[j],top[i]],0)
    mb.face(top,2)  # lower roof plane beneath the distinguishable gable volumes

    # Roof placement follows the orthophoto roof envelope and the 2022 published exterior:
    # broad south house mass with a high gable, plus lower rear/side wings.
    # These roof segment boundaries are illustrative, not surveyed.
    primary_x0=max(minx+0.9,cx-8.8); primary_x1=min(maxx-0.7,cx+8.8)
    primary_y0=miny+0.8; primary_y1=min(maxy-0.8, miny+22.8)
    mb.gable(primary_x0,primary_x1,primary_y0,primary_y1,6.25,PRIMARY_RIDGE_M,2)
    # Rear/side roof masses are lower in the orthophoto; align with the main ridge.
    if maxy > primary_y1 + 4:
        mb.gable(max(minx+0.8,cx-6.5),min(maxx-0.7,cx+6.5),
                 primary_y1-0.5,maxy-0.8,6.15,SECONDARY_RIDGE_M,2)

    # Select a long southern edge as a modeling assumption for the photo-backed
    # facade; its real-world orientation and opening positions are not surveyed.
    front_edges=[]
    for i,p in enumerate(footprint):
        q=footprint[(i+1)%n]; dx,dy=q[0]-p[0],q[1]-p[1]
        length=math.hypot(dx,dy)
        if length<6: continue
        tangent=Vector((dx/length,dy/length,0))
        # CCW footprint: outward normal points to the right of each edge.
        normal=Vector((dy/length,-dx/length,0))
        if normal.y < -0.78 and (p[1]+q[1])/2 < cy:
            front_edges.append((length,i,tangent,normal,p,q))
    front=max(front_edges,key=lambda r:r[0]) if front_edges else None
    if front:
        length,idx,tangent,normal,p,q=front
        # Three restrained window bays on each visible level; glazing is framed
        # by trim and kept shallow, following the source photo's vertical rhythm.
        centers=[length*(k+1)/4 for k in range(3)]
        door_center=length/2
        axes=(tangent,normal,(0,0,1))
        for z in (2.15,4.55):
            for t in centers:
                if abs(t-door_center)<1.7 and z<3: continue
                c=(p[0]+tangent.x*t+normal.x*0.075,
                   p[1]+tangent.y*t+normal.y*0.075,z)
                mb.box(c,axes,(1.45,0.11,1.35),3)
                cglass=(c[0]+normal.x*0.075,c[1]+normal.y*0.075,c[2])
                mb.box(cglass,axes,(1.16,0.055,1.07),4)
                # Simple center mullion and cross rail like the photographed windows.
                mb.box((cglass[0],cglass[1],z),axes,(0.045,0.025,1.02),3)
                mb.box((cglass[0],cglass[1],z),axes,(1.08,0.025,0.045),3)
        # Approximate front entrance centered on the photographed facade.
        dc=(p[0]+tangent.x*door_center+normal.x*0.10,
            p[1]+tangent.y*door_center+normal.y*0.10,1.18)
        mb.box(dc,axes,(1.55,0.12,2.36),3)
        door=(dc[0]+normal.x*0.085,dc[1]+normal.y*0.085,dc[2])
        mb.box(door,axes,(1.18,0.06,2.10),5)
        # Shallow porch lintel and two supports, restrained because the image
        # does not reveal a complete entrance plan.
        porch=(dc[0]+normal.x*0.8,dc[1]+normal.y*0.8,2.55)
        mb.box(porch,axes,(2.7,1.55,0.16),3)
        for off in (-1.1,1.1):
            cc=(dc[0]+tangent.x*off+normal.x*1.45,
                dc[1]+tangent.y*off+normal.y*1.45,1.35)
            mb.box(cc,axes,(0.14,0.14,2.7),3)

    # A tall brick chimney is clearly visible near the principal roof ridge in
    # the 2022 chapter-house photograph; exact coordinates and height estimated.
    chimney=(cx-1.6,miny+12.5,9.1)
    mb.box(chimney,((1,0,0),(0,1,0),(0,0,1)),(1.15,1.05,3.0),0)
    mb.box((chimney[0],chimney[1],10.65),((1,0,0),(0,1,0),(0,0,1)),(1.35,1.22,0.16),1)

    mesh=bpy.data.meshes.new("Alpha Kappa Lambda 2018 LiDAR footprint shell with photo-backed massing")
    mesh.from_pydata(mb.vertices,[],mb.faces); mesh.update()
    # Keep the authored asset as one mesh object with shared-index, closed
    # surface components instead of face-by-face duplicate vertices.
    topo=bmesh.new(); topo.from_mesh(mesh)
    boundary_edges=sum(1 for e in topo.edges if e.is_boundary)
    nonmanifold_edges=sum(1 for e in topo.edges if not e.is_manifold)
    component_sizes=[]; seen=set()
    for seed in topo.faces:
        if seed in seen: continue
        stack=[seed]; seen.add(seed); size=0
        while stack:
            face=stack.pop(); size+=1
            for edge in face.edges:
                for other in edge.link_faces:
                    if other not in seen: seen.add(other); stack.append(other)
        component_sizes.append(size)
    topo_report={"vertices":len(topo.verts),"edges":len(topo.edges),"faces":len(topo.faces),
                 "boundary_edges":boundary_edges,"nonmanifold_edges":nonmanifold_edges,
                 "face_connected_components":len(component_sizes),
                 "largest_component_faces":max(component_sizes,default=0),
                 "component_face_counts_desc":sorted(component_sizes,reverse=True)}
    topo.free()
    assert boundary_edges == 0 and nonmanifold_edges == 0, topo_report
    obj=bpy.data.objects.new("Alpha Kappa Lambda",mesh); asset.objects.link(obj)
    for m in mats: mesh.materials.append(m)
    for poly,mi in zip(mesh.polygons,mb.material_ids):
        poly.material_index=mi; poly.use_smooth=False

    # Portable render rig outside the exported asset collection.
    target=Vector((cx,cy,4.2))
    camera_data=bpy.data.cameras.new("AKL massing preview camera")
    camera=bpy.data.objects.new("AKL massing preview camera",camera_data); rig.objects.link(camera)
    camera.location=(cx-34,cy-44,28)
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO"; camera_data.ortho_scale=54; scene.camera=camera
    light_data=bpy.data.lights.new("AKL soft key","AREA")
    light_data.energy=11000; light_data.shape="DISK"; light_data.size=35
    light=bpy.data.objects.new("AKL soft key",light_data); rig.objects.link(light)
    light.location=(cx-22,cy-28,38)
    light.rotation_euler=(Vector((cx,cy,3))-light.location).to_track_quat("-Z","Y").to_euler()
    scene.render.engine="CYCLES"; scene.cycles.samples=24
    scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(PREVIEW_PATH)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.77,0.80,0.83,1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.8
    scene.view_settings.view_transform="AgX"
    PREVIEW_PATH.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    bounds=[[min(v[i] for v in obj.bound_box),max(v[i] for v in obj.bound_box)] for i in range(3)]
    result={
        "asset_id":ASSET_ID,"asset_path":str(ASSET_PATH.relative_to(ROOT)).replace("\\","/"),
        "collection":COLLECTION_NAME,"scene":SCENE_NAME,"object":"Alpha Kappa Lambda",
        "source_geometry":"Indiana Statewide LiDAR Derived Building Footprints, objectid 409920, lidar year 2018; independently registered against Indiana current orthophoto and Purdue FID 784",
        "official_identity":{"fid":784,"name":"Alpha Kappa Lambda","abbreviation":"SOAKL","address":"417 Waldron St"},
        "coordinate_contract":"Campus X east, Y north, Z up; documented origin and local approximation; simple massing directly linked in campus coordinates",
        "lidar_vertices":n,"lidar_ring_area_projected_m2_approx":None,
        "mesh_topology":topo_report,
        "bounds_world_m":bounds,
        "estimated_eaves_m":WALL_EAVE_M,"estimated_main_ridge_m":PRIMARY_RIDGE_M,
        "height_status":"Unmeasured estimate: two visible above-grade levels and gabled attic/roof are apparent in the 2022 AKL chapter-house image; vertical scale inferred, not surveyed. GIS Extrution=12 has undocumented units.",
        "roof_status":"Photo-backed charcoal pitched gables, rear/side lower roof masses, and a prominent brick chimney; roof segment boundaries and heights are estimated from 2022 exterior photo plus 2022-2025 aerial orthophoto.",
        "facade_status":"Photo-backed red-brown masonry, light window/eave trim, repeated rectangular windows, and a front entrance/porch; exact openings and entrance position are approximate.",
        "preview":str(PREVIEW_PATH.relative_to(ROOT)).replace("\\","/"),"external_dependencies":[]
    }
    # Compute area/perimeter in the native CRS from source geometry report recorded by evidence tooling.
    report_path=ROOT/"audit"/"alpha_kappa_lambda"/"footprint_registration.json"
    if report_path.exists():
        r=json.loads(report_path.read_text(encoding="utf-8"))
        result["lidar_ring_area_projected_m2_approx"]=r["indiana_lidar_geometry"]["area_m2"]
        result["lidar_ring_perimeter_projected_m_approx"]=r["indiana_lidar_geometry"]["perimeter_m"]
    RESULT_PATH.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
