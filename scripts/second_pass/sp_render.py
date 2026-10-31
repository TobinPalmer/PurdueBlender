"""Second-pass review render harness (headless bpy).

Usage:
  python scripts/second_pass/sp_render.py <asset.blend> <out_dir> [--views a,b] [--res 1200] [--inspect]

Opens the saved asset, frames the evaluated geometry of the exported Asset_<id>
collection and renders a consistent neutral-daylight review set: four principal
elevations (N,E,S,W), four obliques, roof/top and an eye-level close view per face.
Writes render_settings.json and inspection.json (bounds, object counts, SHA-256).
"""
import sys, os, json, math, hashlib, argparse
import bpy
from mathutils import Vector


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def world_bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type not in {'MESH', 'CURVE', 'FONT'}:
            continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            w = oe.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx


def setup_scene(res):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.cycles.max_bounces = 4
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res * 0.62)
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = -0.4
    # neutral daylight world
    w = bpy.data.worlds.new('SP_ReviewWorld')
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[0].default_value = (0.62, 0.72, 0.85, 1); bg.inputs[1].default_value = 0.6
    out = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs[0], out.inputs[0])
    sc.world = w
    for o in list(bpy.data.objects):
        if o.name.startswith('SP_'):
            bpy.data.objects.remove(o, do_unlink=True)
    sun_d = bpy.data.lights.new('SP_Sun', 'SUN'); sun_d.energy = 2.6; sun_d.angle = math.radians(2)
    sun = bpy.data.objects.new('SP_Sun', sun_d); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    return sc


def add_ground(mn, mx):
    cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
    size = max(mx.x - mn.x, mx.y - mn.y) * 4 + 50
    bpy.ops.mesh.primitive_plane_add(size=size, location=(cx, cy, mn.z - 0.02))
    g = bpy.context.active_object; g.name = 'SP_Ground'
    m = bpy.data.materials.new('SP_GroundMat'); m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.32, 0.33, 0.3, 1)
    g.data.materials.append(m)


def cam_at(sc, loc, target, lens=35, ortho=None):
    cd = bpy.data.cameras.new('SP_Cam'); cd.lens = lens; cd.clip_end = 5000
    if ortho:
        cd.type = 'ORTHO'; cd.ortho_scale = ortho
    c = bpy.data.objects.new('SP_Cam', cd); sc.collection.objects.link(c)
    c.location = loc
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    return c


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument('blend'); ap.add_argument('out')
    ap.add_argument('--views', default='')
    ap.add_argument('--res', type=int, default=1100)
    ap.add_argument('--samples', type=int, default=24)
    ap.add_argument('--collection', default='')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    digest = sha256(a.blend)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.blend))
    sc = bpy.context.scene
    col = None
    if a.collection:
        col = bpy.data.collections.get(a.collection)
    if col is None:
        cands = [c for c in bpy.data.collections if c.name.startswith('Asset_')]
        col = cands[0] if cands else None
    objs = list(col.all_objects) if col else list(sc.objects)
    mn, mx = world_bounds(objs)
    insp = {
        'asset_path': a.blend, 'asset_sha256': digest,
        'collection': col.name if col else None,
        'object_count': len(objs),
        'mesh_objects': sum(1 for o in objs if o.type == 'MESH'),
        'bounds_min': list(mn), 'bounds_max': list(mx),
        'size_m': list(mx - mn),
        'blender': bpy.app.version_string,
    }
    json.dump(insp, open(os.path.join(a.out, 'inspection.json'), 'w'), indent=2)
    print(json.dumps(insp, indent=1))
    setup_scene(a.res); sc.cycles.samples = a.samples
    add_ground(mn, mx)
    c = (mn + mx) / 2; sx, sy, sz = (mx - mn)
    R = max(sx, sy)
    tz = mn.z + sz * 0.4
    views = {}
    # principal elevations, camera at ~1.7 m+ eye-ish elevated slightly for whole facade
    d = R * 1.25 + 20
    views['north'] = ((c.x, mx.y + d, mn.z + sz * 0.45), (c.x, c.y, tz), 35)
    views['south'] = ((c.x, mn.y - d, mn.z + sz * 0.45), (c.x, c.y, tz), 35)
    views['east'] = ((mx.x + d, c.y, mn.z + sz * 0.45), (c.x, c.y, tz), 35)
    views['west'] = ((mn.x - d, c.y, mn.z + sz * 0.45), (c.x, c.y, tz), 35)
    od = R * 0.95 + 18
    for nm, (ux, uy) in {'northeast': (1, 1), 'northwest': (-1, 1), 'southeast': (1, -1), 'southwest': (-1, -1)}.items():
        views[nm] = ((c.x + ux * od, c.y + uy * od, mn.z + sz * 0.9 + 6), (c.x, c.y, tz), 32)
    views['roof'] = ((c.x, c.y, mx.z + R * 2), (c.x, c.y, mn.z), None, R * 1.15)
    # eye-level oblique close views along each face
    e = R * 0.35 + 10
    views['eye_south'] = ((c.x - sx * 0.25, mn.y - e, mn.z + 1.7), (c.x + sx * 0.1, mn.y, mn.z + sz * 0.45), 28)
    views['eye_north'] = ((c.x + sx * 0.25, mx.y + e, mn.z + 1.7), (c.x - sx * 0.1, mx.y, mn.z + sz * 0.45), 28)
    views['eye_east'] = ((mx.x + e, c.y - sy * 0.25, mn.z + 1.7), (mx.x, c.y + sy * 0.1, mn.z + sz * 0.45), 28)
    views['eye_west'] = ((mn.x - e, c.y + sy * 0.25, mn.z + 1.7), (mn.x, c.y - sy * 0.1, mn.z + sz * 0.45), 28)
    sel = [v for v in a.views.split(',') if v] or list(views)
    settings = {'engine': 'CYCLES CPU', 'samples': a.samples, 'res_x': sc.render.resolution_x, 'res_y': sc.render.resolution_y,
                'world': 'uniform sky 0.6 + sun 2.6 @ elev 40deg az 35deg, Standard view, exposure -0.4', 'cameras': {}}
    for nm in sel:
        v = views[nm]
        for o in list(bpy.data.objects):
            if o.name.startswith('SP_Cam'):
                bpy.data.objects.remove(o, do_unlink=True)
        if nm == 'roof':
            cam_at(sc, v[0], v[1], ortho=v[3])
        else:
            cam_at(sc, v[0], v[1], lens=v[2])
        settings['cameras'][nm] = {'loc': list(v[0]), 'target': list(v[1]), 'lens_or_ortho': v[2] if v[2] else v[3]}
        sc.render.filepath = os.path.join(a.out, nm + '.png')
        bpy.ops.render.render(write_still=True)
        print('rendered', nm)
    json.dump(settings, open(os.path.join(a.out, 'render_settings.json'), 'w'), indent=2)


if __name__ == '__main__':
    main()
