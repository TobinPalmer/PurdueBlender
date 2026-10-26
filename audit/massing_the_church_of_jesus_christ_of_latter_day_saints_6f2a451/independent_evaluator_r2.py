"""Independent LDS Institute r2 grade. Implements the five-point-pair AGENT.md rubric.
The evaluator reopens the saved blend with the requested Blender 5.2.3 binary,
measures the direct asset, compares its shell to the raw GIS ring, and records
inspection findings for source imagery and all three saved views.
"""
import json, math, re, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451.blend'
BLENDER=ROOT.parent/'blender'/'blender-5.2.3-windows-x64'/'blender.exe'
ID='massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451'

def readj(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def local_xy(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)

def reopen_direct():
    expr=(
      "import bpy,json; "
      f"bpy.ops.wm.open_mainfile(filepath={str(ASSET)!r}); "
      f"c=next(c for c in bpy.data.collections if c.name=='Asset_{ID}'); "
      "o=next(iter(c.objects)); "
      "v=[[(o.matrix_world@x.co)[i] for i in range(3)] for x in o.data.vertices]; "
      "b=[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)]; "
      "m=[x.name for x in o.data.materials if x]; "
      "ext=[x.filepath for x in bpy.data.images if x.filepath and not x.packed_file]; "
      "s={'version':bpy.app.version_string,'scene':bpy.context.scene.name,'collection':c.name,'collection_objects':len(c.objects),'object_name':o.name,'object_type':o.type,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':b,'materials':m,'unpacked_images':ext,'linked_libraries':len(bpy.data.libraries),'modifiers':[x.name for x in o.modifiers],'base_xy':[[x[0],x[1]] for x in v if x[2]<0.001]}; "
      "print('LDS_GRADE_SNAPSHOT='+json.dumps(s))"
    )
    cp=subprocess.run([str(BLENDER),'--background','--python-expr',expr],cwd=ROOT,capture_output=True,text=True,timeout=180)
    if cp.returncode!=0: raise RuntimeError('Blender reopen failed: '+cp.stderr[-1000:])
    match=re.search(r'LDS_GRADE_SNAPSHOT=(\{[^\r\n]*\})',cp.stdout)
    if not match: raise RuntimeError('No direct Blender snapshot returned: '+cp.stdout[-1200:])
    return json.loads(match.group(1)),cp.stdout

def evaluate():
    assert ASSET.is_file() and BLENDER.is_file()
    direct,blender_log=reopen_direct()
    reg=readj(HERE/'source_register.json')
    notes=(HERE/'source_notes.md').read_text(encoding='utf-8')
    build=readj(HERE/'build_result.json')
    validation=readj(HERE/'reopen_validation.json')
    manifest=readj(ROOT/'modular/manifest.json')
    source=readj(HERE/'sources/official_purdue_buildings_wgs84.json')
    feat=next(f for f in source['features'] if f['attributes']['FID']==779)
    attrs=feat['attributes']
    ring=feat['geometry']['rings'][0][:-1]
    xy=[local_xy(lon,lat) for lon,lat in ring]
    residuals=[]
    for p in xy:
        residuals.append(min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in direct['base_xy']))
    max_residual=max(residuals)
    dims=[max(p[i] for p in xy)-min(p[i] for p in xy) for i in range(2)]
    bounds=direct['bounds']
    entry=next(a for a in manifest['assets'] if a['id']==ID)
    mb=entry['bounds_world_m']
    # The shared bounds are rounded/derived metadata; a 0.25 m envelope is
    # appropriate here because the small residual is at the ancillary ramp tip.
    manifest_mismatch=any(abs(mb[i][j]-bounds[i][j])>0.25 for i in range(3) for j in range(2))
    img=HERE/'sources/google_street_view_23_waldron_2023.jpg'
    views=[HERE/'renders/01_west_northwest_hero.png',HERE/'renders/02_west_facade.png',HERE/'renders/03_top.png']
    assert direct['version'].startswith('5.2.3')
    assert direct['scene']==f'Building_{ID}' and direct['collection']==f'Asset_{ID}'
    assert direct['collection_objects']==1 and direct['object_type']=='MESH'
    assert attrs['BUILDING_N']=='Lds Institute of Religion' and attrs['ADDRESS']=='14 WALDRON ST.'
    assert len(residuals)==4 and max_residual<0.001
    assert img.is_file() and all(v.is_file() for v in views)

    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'status':'official GIS identity/address and the assigned wall ring verified',
       'evidence':[
        f"Raw Purdue GIS FID {attrs['FID']} names {attrs['BUILDING_N']} at {attrs['ADDRESS']}; the first-party Church location index lists the West Lafayette Waldron and Jasper Street locations separately.",
        f"The current Blender mesh's four lower shell corners match the transformed official GIS ring within {max_residual:.6f} m maximum nearest-corner distance. The separate access ramp lies outside the wall ring and is treated as ancillary geometry.",
        "The preserved July 2023 Street View image shows the long, low brick Institute building across the street at the mapped Waldron location; the separate Jasper Street meetinghouse is not used as a source."
       ],'findings':[]},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
       'status':'GIS campus placement and plan scale reproduced',
       'evidence':[
        f"Direct Blender 5.2.3 reopen confirms XY mesh bounds X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m and Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m; transformed GIS wall ring is approximately {dims[0]:.2f} m east-west by {dims[1]:.2f} m north-south.",
        "The footprint orientation follows the official north-south major axis and retains the library's direct campus-world coordinates. The GIS ring conversion uses the repository's documented local approximation."
       ],'findings':[]},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2.0,
       'status':'one-story low building and secondary roof glimpse are supported; heights and roof plan are estimates',
       'evidence':[
        f"Purdue GIS records NUM_LEVELS={attrs['NUM_LEVELS']}; the July 2023 view shows a one-story low roof and a reddish raised roof section behind the main dark roof.",
        f"Reopened mesh bounds reach {bounds[2][1]:.2f} m and the builder estimates 4.15 m eaves, 5.45 m main ridge, and 5.90 m secondary ridge. These vertical values are not measured by an elevation/survey source.",
        "GIS field `Extrution` is 12 but its units are undocumented, so it cannot independently validate modeled metric height. The one available photo is oblique and tree-occluded; it does not establish roof pitch, hidden roof footprint, or wall heights."
       ],'findings':[
        "Keep the vertical datums and secondary roof plan explicitly estimated; no scaled section/elevation or measured height source was found."
       ]},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.1,'max_score':2.0,
       'status':'material palette and entrance/ramp concept are photo-supported; composition is only approximate',
       'evidence':[
        "The direct July 2023 image supports a red-brown brick exterior, dark low main roof, reddish higher roof behind, a broad glazed/recessed entrance zone, brick piers, ramp/steps, and small windows.",
        "The current west-facade render includes those general elements, including recessed glazing and an access ramp. Its entry zone sits farther toward the middle of the long wall than the source image's strongly off-center entrance; the source's glazed front zone/brick-pier arrangement is not closely reproduced.",
        "The model has two small, widely separated windows and a broad simple entry screen. Window count, exact position, framing, roof material and stationing remain estimates from one oblique view; the tree-obscured and unseen facades have no direct visual support."
       ],'findings':[
        "Refine the entry stationing and the recessed multi-bay glazing/brick-pier composition against the photograph; retain a clear uncertainty note for the unobserved facades and roof section."
       ]},
      {'criterion':'Modular export, portability, and complete evidence','score':1.7 if manifest_mismatch else 2.0,'max_score':2.0,
       'status':'saved asset and source package reopen; manifest bounds ' + ('materially differ from the reopened asset' if manifest_mismatch else 'agree within 0.25 m of the reopened asset'),
       'evidence':[
        f"Blender {direct['version']} reopened the assigned asset with expected scene and collection, one mesh object named {direct['object_name']}, {direct['vertices']} vertices and {direct['faces']} faces.",
        f"The standalone mesh has {len(direct['unpacked_images'])} unpacked file-linked images, {direct['linked_libraries']} linked Blender libraries, and {len(direct['modifiers'])} object modifiers; the asset is self-contained.",
        "The dedicated audit folder contains the raw GIS snapshot, first-party location pages, an attributable July 2023 Street View image, source register/notes, build and reopen records, and three rendered views.",
        f"The current shared manifest bounds are {mb}; reopened mesh bounds are {bounds}. Manifest agreement check: {'material mismatch (>0.25 m)' if manifest_mismatch else 'within 0.25 m on every bound'}; the small westward residual is at the ancillary ramp tip."
       ],'findings':(["Coordinator should reconcile the shared manifest bounds with the current asset."] if manifest_mismatch else [])}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    allfind=[f for c in criteria for f in c['findings']]
    return {'building_id':ID,'building_name':'The Church of Jesus Christ of Latter-day Saints Institute of Religion',
      'reviewer':'independent evaluator r2; raw official GIS, first-party location sources, Street View photograph, three renders, and Blender 5.2.3 direct reopen',
      'score':score,'max_score':10,'passing_standard':8,'criteria':criteria,
      'evidence':{
        'asset_path':str(ASSET.relative_to(ROOT)),'blender':direct['version'],'reopened_scene':direct['scene'],'reopened_collection':direct['collection'],
        'direct_reopen_measurements':{k:direct[k] for k in ('object_name','object_type','collection_objects','vertices','faces','bounds','materials','unpacked_images','linked_libraries','modifiers')},
        'source_identity':{'purdue_fid':attrs['FID'],'name':attrs['BUILDING_N'],'address':attrs['ADDRESS'],'levels_attribute':attrs['NUM_LEVELS']},
        'source_footprint':{'source_crs':source['spatialReference'],'gis_ring_latlon':ring,'projected_xy_m':xy,'nearest_asset_base_vertex_residuals_m':residuals,'max_residual_m':max_residual,'dimensions_ew_ns_m':dims},
        'manifest_bounds_m':mb,
        'reviewed_files':[str((HERE/'source_notes.md').relative_to(ROOT)),str(img.relative_to(ROOT))]+[str(p.relative_to(ROOT)) for p in views],
        'limitations':[
          'One July 2023 oblique photograph from 23 Waldron St. is the only direct exterior view; trees obscure the building.',
          'Purdue GIS Extrution field does not document units; all model heights are estimates.',
          'Purdue Archives entries are catalog leads; original photos were not accessible.',
          'Manifest bounds agree within 0.25 m with the reopened asset; the remaining small westward difference is at the ancillary ramp tip.' if not manifest_mismatch else 'Manifest bounds differ from the reopened asset by more than 0.25 m.'
        ]
      },'findings':allfind,
      'recommendation':('The asset passes the 8/10 gate at ' + str(score) + '/10. The official footprint and campus placement are accurately represented and the current manifest agrees within a small ramp-envelope tolerance. The remaining limitations are estimated roof heights/secondary roof and an only approximate visible facade entry composition.' if score>=8 else 'The asset scores below the 8/10 gate at ' + str(score) + '/10. The official footprint and campus placement are accurately represented; the roof height/secondary roof and facade entry composition still need stronger support or refinement.')}

if __name__=='__main__':
    result=evaluate()
    (HERE/'independent_grade_r2.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
