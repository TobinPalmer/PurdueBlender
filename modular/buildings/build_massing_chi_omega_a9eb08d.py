"""Rebuild the Chi Omega campus massing from GIS, orthophoto, and Street View.

The footprint is the official Purdue GIS outline (FID 781). Indiana's 2022-2025
orthophoto supports the roof's multi-wing silhouette. April 2026 Google Street
View at 417 Waldron faces the GIS-confirmed 402 Waldron building and supports
red brick, white portico columns, upper balcony, and pitched roof. Exact heights,
window dimensions, and historic details remain approximate.
"""
from __future__ import annotations
import json, math
from datetime import date
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_chi_omega_a9eb08d"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "chi_omega" / "sources" / "purdue_gis_fid781_chi_omega_2026-10-26.json"
ORTHO_PATH = ROOT / "audit" / "chi_omega" / "sources" / "indiana_ortho_chi_omega_2022_2025.jpg"
STREET_VIEW_PATH = ROOT / "audit" / "chi_omega" / "sources" / "google_street_view_417_waldron_facing_402_2026-04.jpg"
AUDIT = ROOT / "audit" / "chi_omega"
PREVIEW_PATH = AUDIT / "chi_omega_preview.png"
BUILD_RESULT = AUDIT / "build_result.json"
SCENE_NAME = "Building_massing_chi_omega_a9eb08d"
COLLECTION_NAME = "Asset_massing_chi_omega_a9eb08d"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
WALL_EAVE_M = 7.8  # estimated; architectural elevations unavailable
ROOF_PEAK_M = 10.3  # estimated from low-pitch multi-wing orthophoto roof silhouette


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def material(name, color, roughness=0.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


class MeshBuilder:
    def __init__(self):
        self.verts, self.faces, self.material_ids = [], [], []

    def face(self, pts, mat_id):
        ids = []
        for p in pts:
            self.verts.append(tuple(p)); ids.append(len(self.verts)-1)
        self.faces.append(tuple(ids)); self.material_ids.append(mat_id)

    def box(self, center, axes, size, mat_id):
        c = Vector(center); ax, ay, az = [Vector(a) for a in axes]
        corners = [c + ax*(size[0]*i/2) + ay*(size[1]*j/2) + az*(size[2]*k/2)
                   for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                 (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            self.face([corners[i] for i in f], mat_id)

    def hip_roof(self, cx, cy, sx, sy, z0, rise, ridge_axis="y", overhang=0.45, mat_id=1):
        """Low hip roof with a short ridge, matching the aerial's roof planes."""
        x0,x1 = cx-sx/2-overhang, cx+sx/2+overhang
        y0,y1 = cy-sy/2-overhang, cy+sy/2+overhang
        if ridge_axis == "y":
            ry = min(sy*0.28, 3.6)
            ridge_s = (cx,y0+ry/2,z0+rise)
            ridge_n = (cx,y1-ry/2,z0+rise)
            corners = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]
            self.face([corners[0],corners[1],ridge_s],mat_id)
            self.face([corners[1],corners[2],ridge_n,ridge_s],mat_id)
            self.face([corners[2],corners[3],ridge_n],mat_id)
            self.face([corners[3],corners[0],ridge_s,ridge_n],mat_id)
            self.face([corners[0],corners[3],corners[2],corners[1]],mat_id)
        else:
            rx = min(sx*0.28, 3.6)
            ridge_w = (x0+rx/2,cy,z0+rise)
            ridge_e = (x1-rx/2,cy,z0+rise)
            corners = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]
            self.face([corners[0],corners[1],ridge_e,ridge_w],mat_id)
            self.face([corners[1],corners[2],ridge_e],mat_id)
            self.face([corners[2],corners[3],ridge_w,ridge_e],mat_id)
            self.face([corners[3],corners[0],ridge_w],mat_id)
            self.face([corners[0],corners[3],corners[2],corners[1]],mat_id)


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    src = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    feature = src["features"][0]
    attrs = feature["attributes"]
    assert attrs["FID"] == 781 and attrs["BUILDING_N"] == "Chi Omega"
    ring_ll = feature["geometry"]["rings"][0]
    outline = [local_xy(lon,lat) for lon,lat in ring_ll[:-1]]
    assert len(outline) >= 8
    minx,maxx = min(x for x,y in outline),max(x for x,y in outline)
    miny,maxy = min(y for x,y in outline),max(y for x,y in outline)
    cx,cy=(minx+maxx)/2,(miny+maxy)/2
    sx,sy=maxx-minx,maxy-miny

    # Clean generated scene. Massing remains a single campus-coordinate mesh.
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections,):
        for coll in list(datablocks):
            if coll.name != "Collection": datablocks.remove(coll)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    coll = bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(coll)

    wall = material("ChiOmega_StreetView_Red_Brick",(0.40,0.16,0.12))
    roof = material("ChiOmega_Orthophoto_Dark_Roof",(0.19,0.20,0.21))
    glass = material("ChiOmega_StreetView_Dark_Glazing",(0.07,0.12,0.14),0.35)
    trim = material("ChiOmega_StreetView_White_Trim",(0.86,0.84,0.78))
    builder = MeshBuilder()
    n=len(outline)
    bottom=[(x,y,0.0) for x,y in outline]
    eaves=[(x,y,WALL_EAVE_M) for x,y in outline]
    # Floor and eave caps plus faithful structural perimeter walls.
    builder.face(list(reversed(bottom)),0)
    builder.face(eaves,0)
    for i in range(n): builder.face([bottom[i],bottom[(i+1)%n],eaves[(i+1)%n],eaves[i]],0)

    # Orthophoto shows several intersecting roof zones; these are conservative
    # roof-volume proxies, kept inside the official footprint. Heights are estimates.
    builder.hip_roof(cx+6.3, cy+3.4, 12.0, 16.6, WALL_EAVE_M, 2.5, "y", mat_id=1)
    builder.hip_roof(cx-7.0, cy+0.8, 7.2, 11.4, WALL_EAVE_M, 2.0, "y", mat_id=1)
    builder.hip_roof(cx, cy-10.7, 24.0, 8.0, WALL_EAVE_M, 1.7, "x", mat_id=1)
    builder.hip_roof(cx-10.1, cy-2.6, 4.2, 11.8, WALL_EAVE_M, 1.4, "y", mat_id=1)

    # Repeated windows are neutral placeholders: no elevation or bay schedule was found.
    # Place two rows on longer exterior edges, orienting each shallow unit outward.
    for i in range(n):
        a=Vector(outline[i]); b=Vector(outline[(i+1)%n]); edge=b-a; length=edge.length
        if length < 7.0: continue
        tangent=edge.normalized(); normal=Vector((tangent.y,-tangent.x))
        if sum(outline[k][0]*outline[(k+1)%n][1]-outline[(k+1)%n][0]*outline[k][1] for k in range(n)) < 0:
            normal=-normal
        count=max(1,round(length/4.1))
        for j in range(count):
            t=(j+0.5)/count
            p=a.lerp(b,t)+normal*0.035
            for z in (2.3,5.3):
                builder.box((p.x,p.y,z), ((tangent.x,tangent.y,0),(normal.x,normal.y,0),(0,0,1)), (1.25,0.10,1.35), 2)
                # Thin top band reinforces a repeated opening rhythm; decorative only.
                builder.box((p.x,p.y,z+0.76), ((tangent.x,tangent.y,0),(normal.x,normal.y,0),(0,0,1)), (1.42,0.12,0.12), 3)

    # The Street View photograph shows a prominent white columned entry with
    # an upper balcony on the west/Waldron-facing elevation. Its exact bay width
    # and heights are not surveyed, so keep this as a restrained visual proxy.
    front_x=min(x for x,y in outline)
    entry_y=cy-4.1
    portico_width=7.0
    column_x=front_x-1.05
    column_z0=0.15; column_z1=6.8
    for offset in (-2.55,-0.85,0.85,2.55):
        py=entry_y+offset
        # Shallow square shafts approximate the pale classical columns seen in
        # the photograph while keeping every component inside the single mesh.
        builder.box((column_x,py,(column_z0+column_z1)/2),
                    ((0,1,0),(1,0,0),(0,0,1)),(0.40,0.40,column_z1-column_z0),3)
        builder.box((column_x,py,column_z0+0.14),
                    ((0,1,0),(1,0,0),(0,0,1)),(0.62,0.62,0.28),3)
        builder.box((column_x,py,column_z1-0.12),
                    ((0,1,0),(1,0,0),(0,0,1)),(0.65,0.65,0.24),3)
    # Balcony deck, two rails, and light balusters over the entry.
    builder.box((front_x-1.12,entry_y,4.45),((1,0,0),(0,1,0),(0,0,1)),(2.0,portico_width,0.25),3)
    builder.box((front_x-2.03,entry_y,5.55),((1,0,0),(0,1,0),(0,0,1)),(0.12,portico_width,0.12),3)
    builder.box((front_x-2.03,entry_y,4.82),((1,0,0),(0,1,0),(0,0,1)),(0.12,portico_width,0.12),3)
    for k in range(13):
        py=entry_y-portico_width/2+k*(portico_width/12)
        builder.box((front_x-2.03,py,5.18),((0,1,0),(1,0,0),(0,0,1)),(0.08,0.08,0.68),3)
    # Simple white entablature and shallow pitched portico cap.
    builder.box((front_x-1.02,entry_y,6.92),((1,0,0),(0,1,0),(0,0,1)),(2.30,portico_width+0.7,0.32),3)
    builder.face([(front_x-2.18,entry_y-portico_width/2-0.35,7.08),
                  (front_x-2.18,entry_y+portico_width/2+0.35,7.08),
                  (front_x-2.18,entry_y,8.10)],3)
    builder.face([(front_x-2.18,entry_y-portico_width/2-0.35,7.08),
                  (front_x-1.02,entry_y-portico_width/2-0.35,7.08),
                  (front_x-1.02,entry_y,8.10),
                  (front_x-2.18,entry_y,8.10)],3)
    builder.face([(front_x-2.18,entry_y+portico_width/2+0.35,7.08),
                  (front_x-2.18,entry_y,8.10),
                  (front_x-1.02,entry_y,8.10),
                  (front_x-1.02,entry_y+portico_width/2+0.35,7.08)],3)
    # The ground-floor doorway is set behind the columns; color and position
    # are visible in the Street View source, while its exact dimensions are not.
    builder.box((front_x-0.035,entry_y,1.25),((0,1,0),(1,0,0),(0,0,1)),(1.15,0.10,2.35),2)

    mesh=bpy.data.meshes.new("ChiOmega_Surveyed_Footprint_Estimated_Shell")
    mesh.from_pydata(builder.verts,[],builder.faces); mesh.materials.clear()
    for m in (wall,roof,glass,trim): mesh.materials.append(m)
    for poly,mi in zip(mesh.polygons,builder.material_ids): poly.material_index=mi
    mesh.update()
    obj=bpy.data.objects.new("Chi Omega",mesh); coll.objects.link(obj)
    obj["building_id"]=ASSET_ID; obj["source_feature_id"]=781
    obj["footprint_source"]="Purdue ArcGIS BuildingShapesZip4 FID 781; WGS84 local approximation"
    obj["height_status"]="estimated; no measured elevation located; visual source shows two full levels and roof/upper level"
    obj["roof_status"]="multi-wing planes interpreted from 2022-2025 orthophoto and April 2026 Street View"
    obj["facade_status"]="red brick and columned west entry/balcony supported by April 2026 Street View; exact dimensions illustrative"

    # Studio preview from southwest (west is left in campus coordinates).
    rig=bpy.data.collections.new("ChiOmega_Preview_Rig"); scene.collection.children.link(rig)
    cam_data=bpy.data.cameras.new("ChiOmega_Preview_Camera")
    cam=bpy.data.objects.new("ChiOmega_Preview_Camera",cam_data); rig.objects.link(cam)
    cam.location=(cx-sx*1.45,cy-sy*1.35,29.0)
    target=Vector((cx,cy,WALL_EAVE_M*0.56)); direction=target-Vector(cam.location)
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler(); cam.data.type="ORTHO"; cam.data.ortho_scale=max(sx,sy)*1.65
    scene.camera=cam
    light_data=bpy.data.lights.new("ChiOmega_Preview_Area","AREA"); light_data.energy=8000; light_data.size=35
    light=bpy.data.objects.new("ChiOmega_Preview_Area",light_data); rig.objects.link(light); light.location=(cx-20,cy-12,38)
    light.rotation_euler=(Vector((cx,cy,4))-Vector(light.location)).to_track_quat("-Z","Y").to_euler()
    scene.render.engine="BLENDER_EEVEE_NEXT"; scene.render.resolution_x=1100; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(PREVIEW_PATH)
    scene.world.color=(0.48,0.48,0.48)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.48,0.48,0.48,1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.75
    scene.view_settings.view_transform="Standard"
    scene.render.film_transparent=False
    bpy.ops.render.render(write_still=True)

    # Keep the exported asset limited to one mesh; the preview rig is transient.
    bpy.data.objects.remove(cam, do_unlink=True); bpy.data.objects.remove(light, do_unlink=True)
    bpy.data.collections.remove(rig)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    result={
      "asset_id":ASSET_ID,"asset_path":str(ASSET_PATH.relative_to(ROOT)),"collection":COLLECTION_NAME,
      "scene":SCENE_NAME,"source_feature":{"provider":"Purdue University GIS / ArcGIS BuildingShapesZip4","fid":781,
       "name":attrs["BUILDING_N"],"address":attrs["ADDRESS"],"source_crs":"EPSG:4326",
       "retrieved":"2026-10-26","source_date":"not provided by service snapshot"},
      "footprint":{"method":"WGS84 lon/lat transformed using repository local approximation","vertex_count":n,
       "bounds_xy_m":[[minx,maxx],[miny,maxy]],"width_m":sx,"depth_m":sy,
       "estimated_area_m2":abs(sum(outline[i][0]*outline[(i+1)%n][1]-outline[(i+1)%n][0]*outline[i][1] for i in range(n))/2)},
      "height":{"wall_eave_m":WALL_EAVE_M,"roof_peak_m":ROOF_PEAK_M,"status":"estimated; GIS extrusion metadata has no declared unit, and current elevation unavailable"},
      "roof":{"status":"roof zones interpreted from Indiana orthophoto and April 2026 Street View; not survey-measured","components":4},
      "facade":{"status":"photo-supported, dimensions approximate","details":"red brick body, white columned west entrance with upper balcony and pitched cap interpreted from Google Street View panorama at 417 Waldron St looking toward 402 Waldron; windows remain simplified"},
      "preview":str(PREVIEW_PATH.relative_to(ROOT)),"reopened_validation":"pending"}
    BUILD_RESULT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("BUILD_RESULT",json.dumps(result))

if __name__=="__main__": main()
