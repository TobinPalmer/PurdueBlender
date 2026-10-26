"""Refine the GIS-registered Dudley Hall shell with evidence-backed facade cues.

Run from the PurdueBlender repository root with Blender's --background --python.
The current manifest treats this as a massing library in campus coordinates, so
the source shell and exported collection remain in that unchanged frame.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "dudley_hall.blend"
PREFIX = "DUDLEY_DETAIL_"
_FACE_BUCKETS = {}
_MATERIALS = {}


def mat(name, color, roughness=0.55, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m


def quad(name, points, material, collection):
    _FACE_BUCKETS.setdefault((collection, material), []).append(tuple(tuple(p) for p in points))
    _MATERIALS[material] = material


def cube_between(name, a, b, width, depth, material, collection):
    """Queue a planar facade bar; details are combined into portable meshes."""
    va, vb = Vector(a), Vector(b)
    direction = vb - va
    if direction.length < 1e-6:
        return
    # Bars on horizontal facade runs widen in XY; vertical bars widen in X.
    if abs(direction.z) > 0.85 * direction.length:
        perp = Vector((1.0, 0.0, 0.0))
    else:
        perp = Vector((-direction.y, direction.x, 0.0)).normalized()
    half = perp * max(0.015, width * 0.5)
    quad(name, (va-half, vb-half, vb+half, va+half), material, collection)


def flush_detail_meshes():
    for (collection, material), faces in _FACE_BUCKETS.items():
        verts=[]; polys=[]
        for face in faces:
            first=len(verts)
            verts.extend(face)
            polys.append((first,first+1,first+2,first+3))
        mesh=bpy.data.meshes.new(f"{material.name}_CombinedMesh")
        mesh.from_pydata(verts,[],polys)
        mesh.materials.append(material)
        obj=bpy.data.objects.new(f"{PREFIX}{material.name.replace(' ','_')}",mesh)
        collection.objects.link(obj)
        obj["evidence_status"]="facade position, rhythm, and dimensions estimated from architect photography"
        obj["combined_surface_faces"]=len(polys)
    _FACE_BUCKETS.clear()


def create_facade(collection, shell):
    brick = shell.data.materials[0] if shell.data.materials else mat("Dudley Brick", (0.38, 0.12, 0.065))
    glass = mat("Dudley Dark Blue Curtainwall Estimate", (0.075, 0.16, 0.21), 0.24, 0.12)
    frame = mat("Dudley Charcoal Aluminum Estimate", (0.07, 0.075, 0.075), 0.37, 0.45)
    terracotta = mat("Dudley Terracotta Solar Screen Estimate", (0.47, 0.19, 0.095), 0.5, 0.05)
    concrete = mat("Dudley Pale Cladding Estimate", (0.62, 0.60, 0.55), 0.65)

    # The mesh was generated from the saved GIS footprint. Use its lower ring
    # edges rather than a rectangular bounding box so irregular returns remain.
    verts = shell.data.vertices
    # The saved footprint vertices are explicitly available from the model. GIS
    # perimeter sequencing is recovered by the original mesh's horizontal edges.
    edge_set = set()
    for edge in shell.data.edges:
        a, b = (verts[i].co for i in edge.vertices)
        if abs(a.z) < 1e-5 and abs(b.z) < 1e-5:
            p, q = (round(a.x, 5), round(a.y, 5)), (round(b.x, 5), round(b.y, 5))
            if p != q:
                edge_set.add(tuple(sorted((p, q))))

    z_bands = [(0.9, 2.65), (4.15, 5.95), (7.45, 9.25), (10.75, 12.6)]
    for i, (p, q) in enumerate(sorted(edge_set)):
        a, b = Vector(p), Vector(q)
        delta = b - a
        length = delta.length
        if length < 3.0:
            continue
        center = (a + b) * 0.5
        # Exterior perpendicular. The mesh's boundary outline has no consistent
        # winding in older exports; choose a deterministic normal from midpoint.
        tangent = delta.normalized()
        normal = Vector((-tangent.y, tangent.x))
        if normal.dot(Vector((center.x - 205.897, center.y + 27.339))) < 0:
            normal.negate()
        if center.y < -39 and 218 <= center.x <= 244:
            facade_type = "gateway_glass"
        elif center.x > 246 and -39 < center.y < -28:
            facade_type = "terracotta_screen"
        else:
            facade_type = "punched_windows"
        # Glass banks or punched windows are deliberately set just outside the
        # shell. Their exact bay spacing is estimated; elevations are not claimed
        # as surveyed dimensions.
        inset = min(0.65, length * 0.12)
        usable = length - 2.0 * inset
        if usable < 1.0:
            continue
        if facade_type == "gateway_glass":
            lo, hi = 0.35, 13.7
            u = a + tangent * inset
            v = a + tangent * (length - inset)
            # Pale projecting frame around the documented gateway curtainwall.
            # Wall projection and exact bounds are approximate, but this large
            # light volume and darker glass opening are visible in the 2023 photo.
            cladding_offset = normal * 0.075
            quad(f"{PREFIX}Pale_Gateway_Cladding_{i:03d}",
                 [(u.x+cladding_offset.x,u.y+cladding_offset.y,0.20),
                  (v.x+cladding_offset.x,v.y+cladding_offset.y,0.20),
                  (v.x+cladding_offset.x,v.y+cladding_offset.y,14.5),
                  (u.x+cladding_offset.x,u.y+cladding_offset.y,14.5)],concrete,collection)
            offset = normal * 0.11
            # Four broad glass levels, dark horizontal bands, narrow vertical grid.
            for band_index, (z0, z1) in enumerate([(0.35, 3.35), (3.55, 6.55), (6.75, 9.75), (9.95, 13.1)]):
                quad(f"{PREFIX}Curtainwall_{i:03d}_{band_index}",
                     [(u.x+offset.x,u.y+offset.y,z0),(v.x+offset.x,v.y+offset.y,z0),
                      (v.x+offset.x,v.y+offset.y,z1),(u.x+offset.x,u.y+offset.y,z1)], glass, collection)
                cube_between(f"{PREFIX}Curtainwall_Horizontal_{i:03d}_{band_index}",
                             (u.x+offset.x,u.y+offset.y,z0),(v.x+offset.x,v.y+offset.y,z0),
                             0.08,0.08,frame,collection)
            count = max(2, int(usable / 2.7))
            for k in range(count + 1):
                t = inset + usable * k / count
                pt = a + tangent * t + normal * 0.16
                cube_between(f"{PREFIX}Curtainwall_Mullion_{i:03d}_{k:02d}",
                             (pt.x,pt.y,0.35),(pt.x,pt.y,13.1),0.10,0.10,frame,collection)
            # The architect photo shows a centered glazed entrance under the
            # gateway curtainwall. Add a schematic paired door at the south
            # entry bay; the precise opening width/location is not surveyed.
            if center.y < -39 and 229 <= center.x <= 236:
                door_center = a + tangent * (length * 0.5) + normal * 0.20
                half_w = min(1.05, usable * 0.18)
                base_z, head_z = 0.18, 2.25
                left = door_center - tangent * half_w
                right = door_center + tangent * half_w
                mid = door_center
                quad(f"{PREFIX}Entrance_Door_Left_{i:03d}",
                     [(left.x,left.y,base_z),(mid.x,mid.y,base_z),(mid.x,mid.y,head_z),(left.x,left.y,head_z)],glass,collection)
                quad(f"{PREFIX}Entrance_Door_Right_{i:03d}",
                     [(mid.x,mid.y,base_z),(right.x,right.y,base_z),(right.x,right.y,head_z),(mid.x,mid.y,head_z)],glass,collection)
                for j,(p0,p1,w) in enumerate(((left,right,0.09),(left,mid,0.045),(mid,right,0.045))):
                    cube_between(f"{PREFIX}Entrance_Door_Frame_{i:03d}_{j}",
                                 (p0.x,p0.y,base_z),(p1.x,p1.y,base_z),w,0.05,frame,collection)
                    cube_between(f"{PREFIX}Entrance_Door_Jamb_{i:03d}_{j}",
                                 (p0.x,p0.y,base_z),(p0.x,p0.y,head_z),w,0.05,frame,collection)
                cube_between(f"{PREFIX}Entrance_Door_Head_{i:03d}",
                             (left.x,left.y,head_z),(right.x,right.y,head_z),0.06,0.05,frame,collection)
        elif facade_type == "terracotta_screen":
            # A single louvered screen is visible at the end of the gateway in
            # the architect's exterior photo. Keep its placement as an estimate.
            count = max(5, int(usable / 0.55))
            for k in range(count):
                t = inset + usable * (k + 0.5) / count
                pt = a + tangent * t + normal * 0.10
                cube_between(f"{PREFIX}Terracotta_Fin_{i:03d}_{k:02d}",
                             (pt.x,pt.y,0.3),(pt.x,pt.y,14.0),0.10,0.13,terracotta,collection)
        else:
            # Dark horizontal window openings with thin perimeter/mullion lines.
            # The brick pier rhythm is derived from the official footprint's
            # repeated ~6.9 m bays and remains an interpretation of the photos.
            bays = max(1, int(round(length / 6.8)))
            for band_index, (z0,z1) in enumerate(z_bands):
                for bay in range(bays):
                    t0 = inset + usable * (bay + 0.13) / bays
                    t1 = inset + usable * (bay + 0.87) / bays
                    u, v = a + tangent * t0, a + tangent * t1
                    offset = normal * 0.075
                    quad(f"{PREFIX}Window_{i:03d}_{band_index}_{bay:02d}",
                         [(u.x+offset.x,u.y+offset.y,z0),(v.x+offset.x,v.y+offset.y,z0),
                          (v.x+offset.x,v.y+offset.y,z1),(u.x+offset.x,u.y+offset.y,z1)],glass,collection)
                    for x,z in [(u,z0),(v,z0),(u,z1),(v,z1)]:
                        pt=x+offset
                        cube_between(f"{PREFIX}Frame_{i:03d}_{band_index}_{bay:02d}_{round(z*10)}",
                                     (pt.x,pt.y,z),(pt.x,pt.y,z+0.035),0.035,0.035,frame,collection)

    # Roof edge cap: a restrained flat-roof parapet/coping consistent with the
    # architect's project photographs and official description of simple forms.
    bpy.ops.object.select_all(action="DESELECT")
    # Existing shell top is the reliable plan silhouette. Add a narrow concrete
    # coping only on the north/south long facades; its small offset is estimated.
    for p,q in sorted(edge_set):
        a,b=Vector(p),Vector(q)
        length=(b-a).length
        mid=(a+b)*0.5
        if length < 3.0 or not (mid.y < -39 or mid.y > -17):
            continue
        tangent=(b-a).normalized(); normal=Vector((-tangent.y,tangent.x))
        if normal.dot(Vector((mid.x - 205.897, mid.y + 27.339))) < 0:
            normal.negate()
        # Build four horizontal reveal/coping lines across the dominant runs.
        if mid.y < -39 or mid.y > -17:
            for z in (3.6,7.4,11.2,15.7):
                offset=normal*0.055
                cube_between(f"{PREFIX}Brick_Stringcourse_{len(collection.objects):04d}_{int(z*10)}",
                             (a.x+offset.x,a.y+offset.y,z),(b.x+offset.x,b.y+offset.y,z),
                             0.12,0.12,concrete if z==15.7 else brick,collection)


def setup_render(scene, shell, path):
    # Camera is for evidence only and will not be stored in the exported asset
    # collection. The frame is kept campus-space, matching this massing file.
    center = Vector(shell.location) + Vector((208.0, -26.0, 7.5))
    bpy.ops.object.camera_add(location=center + Vector((112, -125, 105)))
    camera=bpy.context.object; camera.name="Dudley_Evidence_Camera"
    camera.data.type="ORTHO"; camera.data.ortho_scale=145
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=camera
    bpy.ops.object.light_add(type="AREA", location=center+Vector((40,-65,90)))
    light=bpy.context.object; light.name="Dudley_Evidence_Key"; light.data.energy=90000; light.data.shape="DISK"; light.data.size=100
    light.rotation_euler=(center-light.location).to_track_quat("-Z","Y").to_euler()
    scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
    if scene.world is None:
        scene.world=bpy.data.worlds.new("Dudley_Evidence_World")
    scene.world.color=(0.16,0.16,0.16)
    scene.view_settings.view_transform="Standard"
    scene.view_settings.look="Medium High Contrast"
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.objects.remove(light, do_unlink=True)
    scene.camera=None


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene=bpy.context.scene
    shell=bpy.data.objects.get("dudley_hall")
    collection=bpy.data.collections.get("Asset_dudley_hall")
    if not shell or not collection:
        raise RuntimeError("Expected Dudley Hall shell and export collection were not found")
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
    create_facade(collection,shell)
    flush_detail_meshes()
    evidence=ROOT / "audit" / "dudley_hall" / "views" / "dudley_hall_refined_preview.png"
    evidence.parent.mkdir(parents=True,exist_ok=True)
    setup_render(scene,shell,evidence)
    # Clear render helpers and preserve only building models in the export file.
    scene.render.filepath="//"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(f"DUDLEY_BUILD_RESULT {len(collection.objects)} objects {evidence}")


if __name__ == "__main__":
    main()
