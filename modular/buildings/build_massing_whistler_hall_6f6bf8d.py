"""Rebuild Whistler Hall from its official Purdue GIS footprint.

Run with Blender 5.x from the repository root:
  blender -b --python modular/buildings/build_massing_whistler_hall_6f6bf8d.py

The exported collection keeps the manifest ID/name. Geometry is building-local;
the proposed campus origin is recorded in audit/whistler_hall/placement.json for
the coordinator to apply to its master placement marker and shared manifest.
Facade and room layouts are deliberately schematic where plans/elevations were
not found. No external image assets are required.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_whistler_hall_6f6bf8d.blend"
EVIDENCE = ROOT / "audit/whistler_hall"
GIS = EVIDENCE / "sources/purdue_fid84_whistler.json"
BUILDING_ID = "massing_whistler_hall_6f6bf8d"
COLLECTION_NAME = "Asset_massing_whistler_hall_6f6bf8d"
SCENE_NAME = "Building_massing_whistler_hall_6f6bf8d"
OBJECT_NAME = "Whistler Hall"
LAT0, LON0 = 40.4274, -86.9137


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)


def area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
               poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))


def material(name, color, roughness=.72, brick=False, glass=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    if glass:
        bsdf.inputs['Metallic'].default_value = .18
        bsdf.inputs['Roughness'].default_value = .2
    else:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 38 if brick else 5
        tex.inputs['Detail'].default_value = 2
        tex.inputs['Roughness'].default_value = .72
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .25
        ramp.color_ramp.elements[0].color = tuple(c * .78 for c in color) + (1,)
        ramp.color_ramp.elements[1].position = .77
        ramp.color_ramp.elements[1].color = tuple(min(1, c * 1.1) for c in color) + (1,)
        links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .12 if brick else .05
        bump.inputs['Distance'].default_value = .035 if brick else .012
        links.new(tex.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def mesh_object(name, verts, faces, mat, collection, bevel=0):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new('Soft arrises', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def box(name, center, size, mat, collection, bevel=0):
    x, y, z = center
    sx, sy, sz = (v / 2 for v in size)
    # Keep mesh vertices around the origin so rotation is about the box center.
    verts = [(dx*sx, dy*sy, dz*sz) for dx,dy,dz in
             [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj = mesh_object(name, verts, faces, mat, collection, bevel)
    obj.location=(x,y,z)
    return obj


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    data = json.loads(GIS.read_text(encoding='utf-8'))
    feature = next(f for f in data['features'] if f['attributes']['FID'] == 84)
    attrs = feature['attributes']
    ring_ll = feature['geometry']['rings'][0]
    ring_world = [local_xy(lon, lat) for lon, lat in ring_ll]
    minx, maxx = min(p[0] for p in ring_world), max(p[0] for p in ring_world)
    miny, maxy = min(p[1] for p in ring_world), max(p[1] for p in ring_world)
    ox, oy = (minx + maxx)/2, (miny + maxy)/2
    ring = [(x-ox, y-oy) for x,y in ring_world]
    if ring[0] == ring[-1]:
        ring.pop()
    if area2(ring) < 0:
        ring.reverse()
    footprint_area = abs(area2(ring))/2

    # Start with a clean scene and one stable exported collection.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset_col = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset_col)
    shell = bpy.data.collections.new('Whistler Hall | GIS footprint shell')
    asset_col.children.link(shell)
    detail = bpy.data.collections.new('Whistler Hall | facade details')
    asset_col.children.link(detail)
    interior = bpy.data.collections.new('Whistler Hall | schematic lab interior')
    asset_col.children.link(interior)

    brick = material('Whistler warm russet masonry | procedural', (.34,.13,.085), brick=True)
    concrete = material('Pale precast concrete bands', (.58,.55,.49), brick=False)
    roofmat = material('Flat roof membrane', (.16,.18,.18), roughness=.91)
    glass = material('Muted blue-grey laboratory glazing', (.16,.29,.34), roughness=.22, glass=True)
    frame = material('Dark bronze window frames', (.11,.13,.13), roughness=.36)
    interior_wall = material('Schematic interior partitions', (.72,.69,.59), roughness=.8)
    lab_top = material('Laboratory worktops', (.68,.69,.64), roughness=.42)
    floor_mat = material('Interior floor concrete', (.42,.42,.39), roughness=.85)

    # Four above-grade levels are supported by NUM_LEVELS/CountOfFLO. The exact
    # roof elevation is not surveyed; 16.2 m is a 4-storey architectural estimate.
    ground_z, roof_z = .0, 16.2
    floor_levels = [0.0, 3.7, 7.4, 11.1, 14.8]
    parapet_z = 16.2
    # Exact GIS perimeter extrusion, split into quads. The cap tessellation uses
    # the identical plan vertices (no footprint simplification).
    n = len(ring)
    verts = [(x,y,ground_z) for x,y in ring] + [(x,y,roof_z) for x,y in ring]
    faces = [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    base_obj = mesh_object(OBJECT_NAME, verts, faces, brick, shell)
    base_obj['stable_building_id'] = BUILDING_ID
    base_obj['official_gis_fid'] = 84
    base_obj['geometry_note'] = 'Walls follow official WSLR FID 84 footprint; facade articulation estimated.'
    # Exterior vertical concrete belt courses; thin facia around the perimeter.
    for z, h in [(3.55,.16),(7.25,.16),(10.95,.16),(14.65,.16),(15.92,.24)]:
        for i in range(n):
            a,b=ring[i],ring[(i+1)%n]
            dx,dy=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dy)
            if length < 1.7: continue
            nx,ny=dy/length,-dx/length
            off=.055
            vv=[(a[0]+nx*off,a[1]+ny*off,z-h/2),(b[0]+nx*off,b[1]+ny*off,z-h/2),
                (b[0]+nx*off,b[1]+ny*off,z+h/2),(a[0]+nx*off,a[1]+ny*off,z+h/2)]
            mesh_object(f'Precast belt {i:02d} z{z:.2f}',vv,[(0,1,2,3)],concrete,detail)

    # Repeated recessed-looking windows only on long structural faces. Their
    # spacing is a visual estimate, not a measured elevation schedule.
    primary_edge=max(range(n),key=lambda i:math.hypot(ring[(i+1)%n][0]-ring[i][0],ring[(i+1)%n][1]-ring[i][1]))
    window_count=0
    for i in range(n):
        a,b=ring[i],ring[(i+1)%n]
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        if length < 7.0: continue
        ux,uy=dx/length,dy/length
        nx,ny=uy,-ux
        count=max(2, round(length/(4.5 if i==primary_edge else 3.5)))
        for floor in range(4):
            z0=.55+floor*3.7
            for j in range(count):
                s=length*(j+1)/(count+1)
                width=min(3.4 if floor==3 else 1.65,length/(count+1)*.78)
                height=1.3 if floor==3 else 1.75
                if i==primary_edge and floor==0 and abs(s-length*.5)<2.8:
                    continue
                cx=a[0]+ux*s+nx*.085
                cy=a[1]+uy*s+ny*.085
                cz=z0+1.55
                # shallow glass and a surround; box depth is along the wall normal
                glazing=box(f'Window glazing {window_count:03d}',(cx,cy,cz),(width,.10,height),glass,detail,.025)
                glazing.rotation_euler[2]=math.atan2(uy,ux)
                # Fine horizontal mullion and sill are separated materials.
                sill=box(f'Window sill {window_count:03d}',(cx+nx*.055,cy+ny*.055,cz-height/2-.06),(width+.16,.12,.11),concrete,detail,.018)
                sill.rotation_euler[2]=math.atan2(uy,ux)
                mull=box(f'Window mullion {window_count:03d}',(cx+nx*.06,cy+ny*.06,cz),(width+.06,.08,.055),frame,detail,.008)
                mull.rotation_euler[2]=math.atan2(uy,ux)
                window_count+=1

    # Roof cap exactly uses triangulated official perimeter.
    poly = [[Vector((x,y,roof_z)) for x,y in ring]]
    tris=tessellate_polygon(poly)
    cap_faces=[tuple(v if isinstance(v,int) else 0 for v in tri) for tri in tris]
    roof=mesh_object('Whistler Hall flat roof',[(x,y,roof_z+.02) for x,y in ring],cap_faces,roofmat,shell)
    roof['source_basis']='GIS FID 84 perimeter; flat parapeted roof is an inferred institutional form.'
    # Parapet stripe around perimeter.
    for i in range(n):
        a,b=ring[i],ring[(i+1)%n]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length < 1.0: continue
        nx,ny=dy/length,-dx/length; off=.07
        vv=[(a[0]+nx*off,a[1]+ny*off,15.85),(b[0]+nx*off,b[1]+ny*off,15.85),
            (b[0]+nx*off,b[1]+ny*off,16.2),(a[0]+nx*off,a[1]+ny*off,16.2)]
        mesh_object(f'Parapet coping {i:02d}',vv,[(0,1,2,3)],concrete,detail)

    # Restrained, clearly schematic lab furniture on two floors. Purdue sources
    # establish multiple laboratory suites, but not room-by-room plans.
    # Use the footprint centroid with small generic benches; floor slabs remain
    # visible through glazing as a believable massing interior.
    cx=sum(p[0] for p in ring)/n; cy=sum(p[1] for p in ring)/n
    floor_tris=tessellate_polygon([[Vector((x,y,0)) for x,y in ring]])
    floor_faces=[tuple(v if isinstance(v,int) else 0 for v in tri) for tri in floor_tris]
    for idx,z in enumerate([3.68,7.38,11.08,14.78]):
        floor_obj=mesh_object(f'Schematic interior floor {idx+1}',[(x,y,z) for x,y in ring],floor_faces,floor_mat,interior)
        floor_obj['layout_status']='schematic slab only; not a room plan'
    # Generic bench groups are intentionally small and do not purport to map actual rooms.
    for floor in [1,2,3]:
        z=floor_levels[floor]+.95
        for row in range(3):
            yy=cy-15+row*6
            box(f'Schematic lab bench f{floor} r{row}',(cx+2,yy,z),(6.0,.8,.92),lab_top,interior,.04)
            box(f'Schematic lab island f{floor} r{row}',(cx-5,yy+2.0,z),(4.2,.72,.92),lab_top,interior,.04)
        for xoff in [-10,0,10]:
            box(f'Schematic partition f{floor} x{xoff}',(cx+xoff,cy,z+1.0),(.08,25,1.9),interior_wall,interior)
    # The archival 2015 Purdue photo confirms a brick long facade, grouped
    # glazing, concrete bands and a central raised gable. The photograph is not
    # georeferenced; exact side, dimensions and entrance coordinates remain estimates.
    a,b=ring[primary_edge],ring[(primary_edge+1)%n]
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L>6:
        ux,uy=dx/L,dy/L; nx,ny=uy,-ux
        px=(a[0]+b[0])/2; py=(a[1]+b[1])/2
        canopy=box('Estimated long-facade entry canopy',(px+nx*.9,py+ny*.9,3.0),(5.4,2.0,.18),concrete,detail,.04)
        canopy.rotation_euler[2]=math.atan2(uy,ux)
        for s in [-1,1]:
            col=box(f'Entry canopy support {s}',(px+ux*s*2.3+nx*1.5,py+uy*s*2.3+ny*1.5,1.5),(.18,.20,3.0),concrete,detail,.02)
            col.rotation_euler[2]=math.atan2(uy,ux)
        door=box('Estimated main entrance glazing',(px+nx*.11,py+ny*.11,1.2),(3.4,.12,2.4),glass,detail,.025)
        door.rotation_euler[2]=math.atan2(uy,ux)
        # Photo-visible triangular rooftop accent, represented as a shallow
        # brick gable. It is an illustrative silhouette, not a measured roof plan.
        gable_profile=[(-5.2,16.18),(5.2,16.18),(0,19.35)]
        gv=[]
        for depth in [.08,-3.4]:
            for s,z in gable_profile:
                gv.append((px+ux*s+nx*depth,py+uy*s+ny*depth,z))
        gf=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
        gable=mesh_object('Photographed central gable silhouette',gv,gf,brick,detail)
        gable['evidence']='Visible in Purdue Agricultural Communication photo, 2015-01-08; dimensions and compass side estimated.'
        # Substantial piers bracket the central facade zone as in the reference.
        for s in [-8,-5,5,8]:
            pier=box(f'Long-facade masonry pier {s}',(px+ux*s+nx*.14,py+uy*s+ny*.14,7.8),(.32,.30,15.6),brick,detail,.025)
            pier.rotation_euler[2]=math.atan2(uy,ux)

    # Camera, lighting and render for an inspectable preview. All data remains
    # in the asset; the render images are audit artifacts beside the blend file.
    world=bpy.data.worlds.new('Whistler overcast studio') if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world; world.use_nodes=True
    world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.27,.32,.38,1)
    world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.55
    area_data=bpy.data.lights.new('Large softbox','AREA')
    area=bpy.data.objects.new('Large softbox',area_data); scene.collection.objects.link(area)
    area.location=(35,-55,65); area.data.energy=4500; area.data.size=40
    area.rotation_euler=(math.radians(24),0,math.radians(30))
    scene.render.engine='CYCLES'
    scene.cycles.samples=24
    scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'

    def camera_at(name, location, target, lens=45, ortho=None):
        data_cam=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data_cam); scene.collection.objects.link(cam)
        cam.location=location
        direction=Vector(target)-cam.location
        cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
        cam.data.lens=lens
        if ortho: cam.data.type='ORTHO'; cam.data.ortho_scale=ortho
        scene.camera=cam
        return cam
    target=(0,0,7)
    camera_at('Exterior preview camera',(76,-102,58),target,49)
    scene.render.filepath=str(EVIDENCE/'whistler_exterior.png')
    bpy.ops.render.render(write_still=True)
    camera_at('Top plan preview camera',(0,0,160),(0,0,0),ortho=(max(maxx-minx,maxy-miny)+18)*scene.render.resolution_x/scene.render.resolution_y)
    scene.render.filepath=str(EVIDENCE/'whistler_topdown.png')
    bpy.ops.render.render(write_still=True)

    # Create camera and light outside exported asset collection. Save the file.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    # Evidence calculations and proposed origin for coordinator-owned placement.
    ll_center=[(lon,lat) for lon,lat in ring_ll]
    # geographic coordinate corresponding to approximate local center
    lon0=LON0+ox/(111412.84*math.cos(math.radians(LAT0)))
    lat0=LAT0+oy/111040.0
    local_area_as_webmercator=footprint_area/(math.cos(math.radians((min(p[1] for p in ring_ll)+max(p[1] for p in ring_ll))/2))**2)
    report={
      'building_id':BUILDING_ID,'official_identity':attrs['BUILDING_N'],'official_abbreviation':attrs['BLDG_ABBR'],
      'fid':attrs['FID'],'source_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D84&outFields=*&returnGeometry=true&outSR=4326&f=pjson',
      'source_crs':'Feature geometry requested as EPSG:4326; FeatureServer layer metadata reports native/latest spatial reference WKID 102100/3857. Project local approximation is applied directly to returned lon/lat.',
      'retrieved':'2026-10-26','project_transform':'X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040',
      'proposed_origin_world_xy_m':[ox,oy],'proposed_origin_lon_lat':[lon0,lat0],
      'asset_local_bounds_xy_m':[[min(p[0] for p in ring),max(p[0] for p in ring)],[min(p[1] for p in ring),max(p[1] for p in ring)]],
      'gis_projected_area_m2':footprint_area,'gis_shape_area_field':attrs['Shape__Area'],'gis_shape_area_units':'square metres in layer-native Web Mercator (EPSG:3857), confirmed by FeatureServer metadata; the feature geometry was requested in EPSG:4326.',
      'area_projection_check':{'project_local_ring_area_m2':footprint_area,'approx_web_mercator_area_m2':local_area_as_webmercator,'official_shape_area_m2':attrs['Shape__Area'],'difference_percent':(local_area_as_webmercator/attrs['Shape__Area']-1)*100,'method':'project local equirectangular ring area divided by cos(latitude)^2 to compare approximate Web Mercator planar area; not survey area'},
      'gis_ring_vertex_count':len(ring),'model_shell_vertex_count':len(ring),'footprint_comparison':'Exact same FID 84 perimeter ring drives all wall segments and roof tessellation; no plan scaling or vertex simplification.',
      'footprint_match':'vertex-identical by construction, local-transform residual 0.0 m; transformation is project approximate local conversion, not a survey CRS.',
      'official_story_count':attrs['NUM_LEVELS'],'main_parapet_height_estimate_m':roof_z,'highest_gable_apex_estimate_m':19.35,'height_evidence':'Four levels supported by NUM_LEVELS=4 and CountOfFLO=4. Main parapet 16.2 m and small gable apex 19.35 m are architectural estimates. GIS Extrution=17 has no unit definition in layer schema, so it is not treated as measured height. No surveyed roof elevation was found.',
      'material_note':'A Purdue Agricultural Communication photo dated 2015-01-08 confirms russet brick, horizontal concrete/light bands, a broad band of upper glazing, grouped window openings, and a raised gable. Exact facade side, dimensions, window schedule, and entry location are estimated from the oblique archival view. No external texture assets.',
      'interior_note':'Generic schematic lab benches/partitions supported only by Purdue sources establishing Whistler as a multi-lab research building; not a representation of actual room layout.',
      'window_count':window_count,'asset_object_count':sum(len(c.objects) for c in [shell,detail,interior]),'asset_material_count':len({m for c in [shell,detail,interior] for o in c.objects if o.type=='MESH' for m in o.data.materials if m}),
      'previews':['audit/whistler_hall/whistler_exterior.png','audit/whistler_hall/whistler_topdown.png']
    }
    (EVIDENCE/'placement.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
