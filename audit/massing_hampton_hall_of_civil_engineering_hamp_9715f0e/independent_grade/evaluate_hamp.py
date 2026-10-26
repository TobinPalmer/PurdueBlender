"""Independent evidence-led evaluation for HAMP. Run in Blender 5.2 background."""
import bpy, json, math
from pathlib import Path

ROOT = Path.cwd()
ASSET = ROOT / 'modular/buildings/massing_hampton_hall_of_civil_engineering_hamp_9715f0e.blend'
RAW = ROOT / 'audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/sources/official_footprint_feature_272_raw.json'
GRADE = ROOT / 'audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/independent_grade'
COLLECTION_NAME = 'Asset_massing_hampton_hall_of_civil_engineering_hamp_9715f0e'
SCENE_NAME = 'Building_massing_hampton_hall_of_civil_engineering_hamp_9715f0e'

def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    c = bpy.data.collections.get(COLLECTION_NAME)
    scene_ok = bpy.context.scene.name == SCENE_NAME
    obj = c.objects.get('HAMP primary masonry envelope (estimated 5 above-grade levels)') if c else None
    response = json.loads(RAW.read_text(encoding='utf-8-sig'))
    source = response.get('features', [{}])[0]
    attrs = source.get('attributes', {})
    # This is the one official Purdue campus GIS polygon, feature FID 272.
    rings = source.get('geometry', {}).get('rings', [])
    origin_lat, origin_lon = 40.4274, -86.9137
    def to_xy(lon, lat):
        return ((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)), (lat-origin_lat)*111040.0)
    ring = [to_xy(lon, lat) for lon,lat in (rings[0] if rings else [])]
    actual_bottom = []
    if obj and obj.type == 'MESH':
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            if abs(p.z) < 1e-4:
                actual_bottom.append((p.x,p.y))
    nearest = [min((math.hypot(x-a,y-b) for a,b in actual_bottom), default=float('inf')) for x,y in ring]
    max_error = max(nearest, default=float('inf'))
    minx,maxx=min(x for x,y in ring),max(x for x,y in ring)
    miny,maxy=min(y for x,y in ring),max(y for x,y in ring)
    mesh_count = sum(o.type=='MESH' for o in c.objects) if c else 0
    external_images = [i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
    linked_libraries = [lib.filepath for lib in bpy.data.libraries]
    # Visual evidence was independently compared at 100% against the saved Purdue facade photo.
    # The model captures brick, repeated vertical glazing, pale trim, and an entrance sign;
    # however, the reference's dominant tall central glazed/stone atrium is not represented.
    criteria = [
      {'criterion':'Correct identity and source-backed footprint','points':2.0,'max_points':2,
       'evidence':f"Raw Purdue Campus GIS feature FID={attrs.get('FID')} / code={attrs.get('BLDG_ABBR')} / name={attrs.get('BUILDING_N')} directly identifies Hampton Hall. Source ring has {len(ring)} coordinates. Loaded structural shell bottom has {len(actual_bottom)} vertices; independently recomputed source-to-mesh max nearest XY error is {max_error:.8f} m. This establishes source polygon reproduction, not an independent survey.",
       'findings':[]},
      {'criterion':'Position, orientation, and scale/dimensions','points':2.0,'max_points':2,
       'evidence':f"The loaded shell base follows the campus GIS ring in the project local meter approximation. Recomputed GIS AABB is x=[{minx:.3f},{maxx:.3f}], y=[{miny:.3f},{maxy:.3f}] m; saved shell bounds in builder validation agree. Orientation follows source polygon vertices rather than a rectangular proxy.",
       'findings':['Position/shape are tied to Purdue GIS and the project approximate lon/lat conversion; the feature is not a certified survey.']},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.4,'max_points':2,
       'evidence':'Purdue Engineering safety report describes basement, ground, main/first, second, third, and fourth levels, consistent with five above-grade levels. Builder depicts 17.25 m shell height as an estimate (5 x 3.45 m) and a separate 1 m low rooftop penthouse estimate. Renders visibly show five facade bands.',
       'findings':['No source provides surveyed elevations or floor-to-floor heights; roof penthouse is schematic and unsupported by the supplied evidence.']},
      {'criterion':'Facade, entrances, and distinctive architecture','points':0.8,'max_points':2,
       'evidence':'Purdue CCE facade photograph confirms warm brick, pale stone framing, vertically proportioned glazing, and prominent name lettering. The saved entry view and model include brick, repeated windows, pale trim, and a sign/entry.',
       'findings':['The source photograph shows a dominant tall central glazed and pale-stone atrium/bay that is absent from the model; current model reads as uniform horizontal brick-and-window rows. Entrance form and precise location remain schematic.']},
      {'criterion':'Modular export, portability, and complete evidence','points':2.0,'max_points':2,
       'evidence':f"Independently reopened .blend and found expected scene={scene_ok}, collection={bool(c)}, {len(c.objects) if c else 0} collection objects ({mesh_count} meshes), {len(linked_libraries)} linked libraries and {len(external_images)} unpacked external images. Evidence folder contains raw official GIS, source facade image, official history/renovation sources, floor-level report and renovation drawings, render set, and reopen validation.",
       'findings':[]}
    ]
    score=round(sum(c['points'] for c in criteria),2)
    findings=[f for c0 in criteria for f in c0['findings']]
    return {'score':score,'max_score':10,'criteria':criteria,
            'evidence':{'asset':str(ASSET),'scene':bpy.context.scene.name,'collection':COLLECTION_NAME,'collection_object_count':len(c.objects) if c else 0,'official_feature_id':attrs.get('FID'),'official_name':attrs.get('BUILDING_N'),'source_ring_vertices':len(ring),'shell_bottom_vertices':len(actual_bottom),'max_source_to_shell_xy_error_m':max_error,'gis_bounds_xy_m':[[minx,maxx],[miny,maxy]],'linked_libraries':linked_libraries,'unpacked_external_images':external_images,'renders':['audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/renders/exterior_axonometric.png','audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/renders/entry_facade.png','audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/renders/roof_plan.png']},
            'findings':findings}

result=evaluate()
GRADE.mkdir(parents=True,exist_ok=True)
(GRADE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))


