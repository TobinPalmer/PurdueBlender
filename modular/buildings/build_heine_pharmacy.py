"""Deterministically revise Heine Pharmacy's evidence-backed facade (R2).

Run from the project root with Blender 5.2:
  blender -b modular/buildings/heine_pharmacy.blend --python modular/buildings/build_heine_pharmacy.py

The GIS shell, local origin and master placement are deliberately untouched.
"""
import bpy
import hashlib
import json
import math
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'heine_pharmacy.blend'
PREVIEW = ROOT / 'audit' / 'heine_pharmacy' / 'heine_pharmacy_r2_preview.png'
assert bpy.data.filepath.lower().endswith('heine_pharmacy.blend'), bpy.data.filepath
asset = bpy.data.collections.get('Asset_heine_pharmacy')
assert asset and bpy.data.objects.get('RHPH structural shell | GIS outline')
shell = bpy.data.objects['RHPH structural shell | GIS outline']

# Recover the same photographed facade edge used in R1, using the unchanged GIS shell.
ring = []
for v in shell.data.vertices:
    p = shell.matrix_world @ v.co
    if abs(p.z + 1.0) < 1e-3:
        xy = (float(p.x), float(p.y))
        if not any(math.dist(xy, q) < 0.001 for q in ring):
            ring.append(xy)
entry_lintel = bpy.data.objects.get('RHPH | pharmacy entry arcade lintel')
if entry_lintel:
    entry_xy = Vector((entry_lintel.location.x, entry_lintel.location.y))
else:
    # Recover from the previously generated centered crown, then persist the value.
    old_crown = bpy.data.objects.get('Heine evidence entry R2 | crown beam')
    saved_entry_xy = asset.get('heine_entry_center_xy_r2')
    if saved_entry_xy and len(saved_entry_xy) == 2:
        entry_xy = Vector(saved_entry_xy)
    elif old_crown and old_crown.type == 'MESH':
        old_points = [old_crown.matrix_world @ v.co for v in old_crown.data.vertices]
        entry_xy = Vector((sum(p.x for p in old_points) / len(old_points),
                           sum(p.y for p in old_points) / len(old_points)))
    else:
        raise RuntimeError('Cannot recover the evidence-derived entry center')
segments = []
for i, a in enumerate(ring):
    b = ring[(i + 1) % len(ring)]
    d = Vector((b[0] - a[0], b[1] - a[1]))
    length = d.length
    if length < 25.0:
        continue
    u = d.normalized()
    av = Vector(a)
    t = max(0.0, min(length, (entry_xy - av).dot(u)))
    nearest = av + u * t
    segments.append(((nearest - entry_xy).length, length, Vector(a), Vector(b), u))
assert segments
_, facade_length, p0, p1, u = min(segments, key=lambda s: s[0])
assert facade_length > 35.0
outward = Vector((u.y, -u.x))
stone = bpy.data.materials.get('HEINE_PHARMACY | evidence palette stone and painted metal')
glass = bpy.data.materials.get('HEINE_PHARMACY | evidence palette glazing')
metal = bpy.data.materials.get('HEINE_PHARMACY | graphite metal details') or stone
assert stone and glass and metal

# Cleanly replace the generated R1 facade sets, making the build repeatable.
for name in (
    'Heine evidence facade | seven vertical window stacks',
    'Heine evidence facade | limestone window surrounds and spandrels',
    'Heine evidence facade | vertical sash mullions',
    'Heine evidence facade R2 | tall vertical glazing',
    'Heine evidence facade R2 | broad limestone spandrels',
    'Heine evidence facade R2 | restrained glazing rails',
    'Heine evidence entry R2 | four arch portal',
    'Heine evidence entry R2 | heavy piers',
    'Heine evidence entry R2 | crown beam',
):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# The source image supports seven slim vertical glazed slots with a deep, broad
# stone spandrel between two long glass sections. Avoid the R1 five-small-pane grid.
def quad_mesh(name, quads, material):
    verts, faces = [], []
    for q in quads:
        i = len(verts)
        verts.extend(q)
        faces.append((i, i + 1, i + 2, i + 3))
    mesh = bpy.data.meshes.new(name + ' Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset.objects.link(obj)
    return obj

def facade_quad(t0, t1, z0, z1, offset):
    n = outward * offset
    a = p0 + u * t0 + n
    b = p0 + u * t1 + n
    return [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)]

bay_count = 7
bay_spacing = facade_length / bay_count
bay_centers = [(i + 0.5) * bay_spacing for i in range(bay_count)]
glass_quads, stone_quads, rail_quads = [], [], []
glass_width = 1.50
glass_sections = [(5.45, 12.15), (15.05, 20.95)]
for center in bay_centers:
    left, right = center - glass_width / 2, center + glass_width / 2
    for z0, z1 in glass_sections:
        glass_quads.append(facade_quad(left, right, z0, z1, 0.085))
        # A single fine mid-rail keeps scale legible without subdividing the slot
        # into a repetitive five-floor grid.
        rail_z = z0 + (z1 - z0) * 0.51
        rail_quads.append(facade_quad(left, right, rail_z - 0.035, rail_z + 0.035, 0.105))
    # Broad, monolithic light-stone spandrel separating the tall panes.
    stone_quads.append(facade_quad(left - 0.12, right + 0.12, 12.15, 15.05, 0.11))
    # Pale full-height reveals emphasize each narrow vertical window strip.
    stone_quads.append(facade_quad(left - 0.16, left - 0.035, 5.25, 21.12, 0.078))
    stone_quads.append(facade_quad(right + 0.035, right + 0.16, 5.25, 21.12, 0.078))
quad_mesh('Heine evidence facade R2 | tall vertical glazing', glass_quads, glass)
quad_mesh('Heine evidence facade R2 | broad limestone spandrels', stone_quads, stone)
quad_mesh('Heine evidence facade R2 | restrained glazing rails', rail_quads, metal)

# Replace the underscaled decorative canopy-like portal. The source image shows
# four substantial masonry arches spanning nearly half the photographed elevation.
# Preserve the evidence-derived entry center, expand the arcade to 17.2 m, and
# build it as an extruded arch ring with grounded piers (not thin freestanding bars).
old_arcades = [o for o in list(asset.all_objects)
               if o.name.startswith('RHPH | tall entry arcade pier ')
               or o.name.startswith('RHPH | stone arcade arch ')]
for obj in old_arcades:
    bpy.data.objects.remove(obj, do_unlink=True)
# The legacy lintel is a shallow narrow canopy; remove it and build a taller, wider
# crown which reads with the stone arcade as one entrance composition.
bpy.data.objects.remove(entry_lintel, do_unlink=True) if entry_lintel else None
center_xy = entry_xy
center_t = (center_xy - p0).dot(u)
portal_front_offset, portal_depth = 0.90, 1.05
portal_base, spring_z = -0.95, 4.70
inner_r, outer_r = 1.55, 2.10
pitch, arc_count = 4.35, 4
arch_centers = [center_t + (i - (arc_count - 1) / 2) * pitch for i in range(arc_count)]
start_t, end_t = arch_centers[0] - outer_r, arch_centers[-1] + outer_r
assert end_t - start_t < facade_length * 0.52

def local_point(t, offset, z):
    q = p0 + u * t + outward * offset
    return (q.x, q.y, z)

def oriented_box(t0, t1, z0, z1, off0, off1):
    # six faces, with the front surface facing out from the brick facade
    a0, a1 = local_point(t0, off0, z0), local_point(t1, off0, z0)
    b0, b1 = local_point(t0, off0, z1), local_point(t1, off0, z1)
    c0, c1 = local_point(t0, off1, z0), local_point(t1, off1, z0)
    d0, d1 = local_point(t0, off1, z1), local_point(t1, off1, z1)
    return [(a0,a1,b1,b0), (c0,d0,d1,c1), (a0,c0,c1,a1),
            (b0,b1,d1,d0), (a0,b0,d0,c0), (a1,c1,d1,b1)]

arch_faces, pier_faces, crown_faces = [], [], []
segments_per_arch = 20
for idx, c in enumerate(arch_centers):
    # Sculpted annular arch band from left spring to right spring.
    for j in range(segments_per_arch):
        a0 = math.pi - math.pi * j / segments_per_arch
        a1 = math.pi - math.pi * (j + 1) / segments_per_arch
        outer0 = (c + outer_r * math.cos(a0), spring_z + outer_r * math.sin(a0))
        outer1 = (c + outer_r * math.cos(a1), spring_z + outer_r * math.sin(a1))
        inner1 = (c + inner_r * math.cos(a1), spring_z + inner_r * math.sin(a1))
        inner0 = (c + inner_r * math.cos(a0), spring_z + inner_r * math.sin(a0))
        front = [local_point(t, portal_front_offset + portal_depth, z)
                 for t,z in (outer0,outer1,inner1,inner0)]
        back = [local_point(t, portal_front_offset, z)
                for t,z in (outer0,outer1,inner1,inner0)]
        arch_faces.extend([tuple(front), tuple(reversed(back)),
                           (front[0],back[0],back[1],front[1]),
                           (front[2],back[2],back[3],front[3])])
    # Close both arch spring ends.
    for side, angle in [('left', math.pi), ('right', 0.0)]:
        t = c + inner_r * math.cos(angle)
        z = spring_z
        a = local_point(t, portal_front_offset, z)
        b = local_point(t, portal_front_offset + portal_depth, z)
        ztop = spring_z + (outer_r if side == 'left' else outer_r)
        # End face is a small radial stone reveal; it is nearly vertical at springline.
        arch_faces.append((a,b,local_point(t,portal_front_offset + portal_depth,ztop),
                           local_point(t,portal_front_offset,ztop)))
    # Heavy vertical jambs below each arch. Their visible clear opening is 3.1 m.
    half = inner_r
    for t0, t1 in ((c-half-0.44, c-half+0.03), (c+half-0.03, c+half+0.44)):
        pier_faces.extend(oriented_box(t0, t1, portal_base, spring_z,
                                       portal_front_offset, portal_front_offset + portal_depth))

# End piers and shared/intermediate piers fill the stone gaps between openings.
pillar_width = 0.76
pillar_centers = [arch_centers[0] - inner_r - pillar_width / 2]
pillar_centers.extend((arch_centers[i] + arch_centers[i+1]) / 2 for i in range(arc_count-1))
pillar_centers.append(arch_centers[-1] + inner_r + pillar_width / 2)
for pc in pillar_centers:
    pier_faces.extend(oriented_box(pc-pillar_width/2, pc+pillar_width/2,
                                   portal_base, spring_z,
                                   portal_front_offset, portal_front_offset+portal_depth))

top_z = spring_z + outer_r
crown_faces.extend(oriented_box(start_t-0.35, end_t+0.35, top_z-0.05, top_z+0.55,
                                portal_front_offset-0.03,
                                portal_front_offset+portal_depth+0.12))
quad_mesh('Heine evidence entry R2 | four arch portal', arch_faces, stone)
quad_mesh('Heine evidence entry R2 | heavy piers', pier_faces, stone)
quad_mesh('Heine evidence entry R2 | crown beam', crown_faces, stone)

asset['heine_facade_revision'] = 'R2, 2026-10-27: replaced R1 five-pane stacks with seven tall narrow vertical glazing slots, broad stone spandrels and restrained rails; rebuilt entrance as a four-arch full-height stone arcade. GIS shell and local origin preserved.'
asset['heine_entry_arcade_r2'] = 'Four extruded stone arches; 17.2 m overall width, 7.35 m top, positioned at the existing evidence-derived entry center. Dimensions are visual estimates from the 2023 oblique photograph.'
asset['heine_entry_center_xy_r2'] = [float(entry_xy.x), float(entry_xy.y)]
asset['heine_facade_photo_source'] = 'https://commons.wikimedia.org/wiki/File:Purdue_University_Robert_E_Heine_Pharmacy_Building.jpg (Nothda, 2023-10-18, CC BY-SA 4.0)'
asset['heine_facade_uncertainty'] = 'Seven-bay rhythm, tall paired glazing and substantial four-arch portal follow one dated oblique photograph. Exact dimensions, hidden elevations, absolute height and interior room layouts remain estimated or schematic.'

scene = bpy.context.scene
assert scene.camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.filepath = str(PREVIEW)
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
bpy.ops.render.render(write_still=True)
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
summary = {
    'revision':'R2', 'asset':str(ASSET), 'sha256':sha,
    'asset_object_count':len(asset.all_objects), 'facade_length_m':round(facade_length,3),
    'window_bays':bay_count, 'long_glazing_panels':len(glass_quads),
    'broad_spandrel_panels':len(stone_quads), 'arcade_arches':arc_count,
    'arcade_width_m':round(end_t-start_t,3), 'arcade_top_z_m':round(top_z+0.55,3),
    'preview':str(PREVIEW), 'shell_origin_unchanged':True,
}
(ROOT/'audit'/'heine_pharmacy'/'r2_build_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print('HEINE_R2', json.dumps(summary), flush=True)
