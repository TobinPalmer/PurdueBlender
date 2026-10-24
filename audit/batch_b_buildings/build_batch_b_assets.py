import bpy, json, math, os, sys
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / 'modular' / 'buildings'
AUDIT = ROOT / 'audit' / 'batch_b_buildings'
AUDIT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'audit' / 'official_purdue_buildings_wgs84.json'
GIS_URL = 'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0'
RETRIEVED = '2026-10-22'
LAT0, LON0 = 40.4274, -86.9137
LON_M = 111412.84 * math.cos(math.radians(LAT0)); LAT_M = 111040.0

CONFIGS = [
 dict(key='brees_student_athletic_academic_center', fid=255, abbr='BRES', id='massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033', name='Drew and Brittany Brees Student-Athletic Academic Center', file='brees_student_athletic_academic_center.blend', stories=2, height=11.5, color=(.35,.105,.065), trim=(.68,.56,.37), glass=(.045,.12,.15), style='brick', source_urls=['https://purduesports.com/sports/2018/5/17/acad-services-brees-student-athlete-acad-center-html.aspx','https://events.purdue.edu/drew_and_brittany_brees_student-athlete_academic_center','https://www.purdue.edu/operations/emergency-preparedness/bres/'], visual_url='https://localist-images.azureedge.net/photos/40100423165002/card%402x/165f2d98622def2b85a5a24a280b7b72bbf40b7a.jpg', facts='Athletics academic support, study/tutoring and computer center; 2004 opened; expanded/renovated 2012 and 2019. Reference shows red brick with ivy/gold lettering; massing is 2 GIS levels; height is estimated.'),
 dict(key='ford_dining_court', fid=81, abbr='FORD', id='massing_ford_dining_court_71eede4', name='Fred and Mary Ford Dining Court', file='ford_dining_court.blend', stories=2, height=10.0, color=(.39,.14,.085), trim=(.76,.67,.52), glass=(.055,.12,.16), style='dining', source_urls=['https://archives.lib.purdue.edu/agents/corporate_entities/694','https://dining.purdue.edu/ResidentialDining/locations/ford.html','https://www.purdue.edu/accessibilityresources/Accessibility_Guide.pdf'], visual_url='https://pbs.twimg.com/profile_banners/4527780207/1610575095', facts='Two-story standalone dining court on Stadium Avenue/Russell corner per Purdue Archives; dining web page confirms use. GIS lists 4 level-related fields (15.3m,27.8m), conflicting with archival 2-story description; model uses 2 visible dining levels, roof height approximate. Roof form follows online exterior image reference with steep traditional gables.'),
 dict(key='flex_lab', fid=909, abbr='FLEX', id='massing_flex_lab_flex_cc297ea', name='Flex Lab Facility', file='flex_lab.blend', stories=3, height=14.8, color=(.38,.115,.075), trim=(.59,.60,.57), glass=(.035,.15,.19), style='flex', source_urls=['https://engineering.purdue.edu/FlexLab','https://engineering.purdue.edu/Engr/AboutUs/MeetDean/Vision-2030/space-master-plan','https://www.ennead.com/work/purdue/','https://www.cesolutionsinc.com/flex-lab-1'], visual_url='https://enneadweb.s3.amazonaws.com/work-images/1507_Purdue/_xxl/1507_Flex-Lab-AW-19.jpg', facts='2017 facility, approx 108,000 GSF, three-story simple form with brick planes and shifting glass/aluminum curtain wall; low-vibration basement, high bay and open collaborative spaces. GIS footprint FID909 and level fields are incomplete/zero, so three stories supported by architect/Purdue evidence; total above-grade height estimated.'),
 dict(key='hall_for_discovery_and_learning_research', fid=670, abbr='DLR', id='massing_hall_for_discovery_and_learning_research_dlr_ed8395e', name='Hall for Discovery and Learning Research', file='hall_for_discovery_and_learning_research.blend', stories=5, height=19.8, color=(.39,.12,.075), trim=(.63,.63,.60), glass=(.025,.17,.2), style='dlr', source_urls=['https://architizer.com/projects/purdue-university-discovery-learning-center/','https://www.purdue.edu/operations/campus-planning-architecture/wp-content/uploads/sites/10/2025/05/Giant-Leap-Master-Plan-Compressed.pdf'], visual_url='https://architizer-prod.imgix.net/mediadata/projects/082011/9fda19d9.jpg?auto=format%2Ccompress&cs=strip&q=60&w=1680', facts='Purdue GIS FID670: five floors, mapped roof elevation 63.7m above project vertical datum, but source elevation datum/precision unclear. Image shows curved glass facade with horizontal metal bands; exterior silhouette and repeated curtainwall bands modeled. Floors/height use GIS and published photo; interior arrangement remains schematic.'),
 dict(key='heine_pharmacy', fid=606, abbr='RHPH', id='massing_heine_pharmacy_rhph_2f36735', name='Robert E. Heine Pharmacy Building', file='heine_pharmacy.blend', stories=6, height=22.0, color=(.39,.14,.09), trim=(.69,.64,.55), glass=(.035,.12,.16), style='heine', source_urls=['https://legacy.pharmacy.purdue.edu/building-map','https://archives.lib.purdue.edu/fa/UA00053_Pharmacy_School_of.pdf','https://pharmacy.purdue.edu/wp-content/uploads/2025/02/2024-The-Purdue-Pharmacist.pdf'], visual_url='https://legacy.pharmacy.purdue.edu/sites/default/files/inline-images/RHPH_level1.png', facts='Purdue Archives indicates a 145,000-square-foot pharmacy facility completed/moved in 1970 and dedicated by name in 1985; Purdue pharmacy publication says six stories. GIS lists 8 level-coded values with roof 61m (vertical datum unclear), conflicting with published six-story description; visible massing modeled as 6 floors, 22m approximate. Official level-one plan supports circulation/lecture/reception/retail zones; schematic interior only.'),
 dict(key='ray_w_herrick_laboratories', fid=878, abbr='HLAB', id='massing_ray_w_herrick_laboratories_36b11c6', name='Ray W. Herrick Laboratories (2013 research building)', file='ray_w_herrick_laboratories.blend', stories=3, height=13.5, color=(.40,.145,.088), trim=(.58,.60,.58), glass=(.035,.14,.17), style='herrick', source_urls=['https://www.purdue.edu/newsroom/releases/2013/Q4/purdues-new-herrick-labs-building-open-for-business.html','https://engineering.purdue.edu/Herrick/about/facilities','https://engineering.purdue.edu/Herrick/about/about-us/history'], visual_url='https://www.purdue.edu/uns/images/2013/herrick-newbuilding.jpg', facts='This manifest record matches Purdue GIS FID878 / HLAB / 177 S Russell Street and the 2013 68,000-sq-ft new building. A separate manifest record massing_herrick_laboratories_2138103 matches FID246 / HERL “Herrick Acoustics”, the distinct historic 1920s barn building; these are distinct adjacent facilities within the lab complex, not duplicate IDs. Model only HLAB here. Three stories from current visual/source descriptions; roof height estimated.'),
 dict(key='horticulture_building', fid=232, abbr='HORT', id='massing_horticulture_286a904', name='Horticulture Building', file='horticulture_building.blend', stories=5, height=17.5, color=(.38,.125,.07), trim=(.74,.67,.54), glass=(.035,.12,.14), style='hort', source_urls=['https://archives.lib.purdue.edu/agents/corporate_entities/545','https://events.purdue.edu/horticulture_building','https://ag.purdue.edu/hla/facilities/janick-garden.html','https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/03/Space_Report_1.13.1HE_Buiding_List_Oct2021.pdf'], visual_url='https://ag.purdue.edu/department/hla/facilities/_media/garden1.jpg', facts='Purdue Archives says constructed 1926 for Department of Horticulture and Landscape Architecture. GIS FID232 lists 5 levels and 48m extrusion, likely includes multiple vertical classifications and does not specify public surveyed accuracy. Exterior photo supports red brick, white/classical entrance, and three roof dormers; the historic roof shape and exact facade pattern remain estimates pending elevation drawings.'),
 dict(key='krach_leadership_center', fid=902, abbr='KRCH', id='massing_krach_leadership_center_krch_debcdf8', name='Krach Leadership Center', file='krach_leadership_center.blend', stories=4, height=15.6, color=(.39,.14,.09), trim=(.76,.75,.70), glass=(.035,.15,.18), style='krach', source_urls=['https://www.purdue.edu/newsroom/archive/releases/2014/Q3/purdue-to-dedicate-students-krach-leadership-center-.html','https://archives.lib.purdue.edu/agents/corporate_entities/722','https://www.purdue.edu/operations/emergency-preparedness/krch/','https://stories.purdue.edu/popular-purdue-buildings-for-student-life/'], visual_url='https://stories.purdue.edu/app/uploads/2022/07/TopBuildings-ContentHub-Krach-16x9-1.jpg', facts='Purdue sources describe an 81,500-sq-ft 2014 four-story brick-and-glass student leadership building; emergency plan enumerates basement through fourth floor (5 accessible floor levels including basement). Model uses four above-grade levels plus partial basement cue, vertical glazing bays, pale structural piers, entry canopy. Exact heights are estimated.'),
]

# Optional key argument lets the coordinating agent review assets one by one.
requested = set(sys.argv[sys.argv.index('--')+1:]) if '--' in sys.argv else set()
if requested:
    CONFIGS = [cfg for cfg in CONFIGS if cfg['key'] in requested]
    if not CONFIGS:
        raise ValueError('No matching building keys: '+', '.join(sorted(requested)))

with open(SOURCE, encoding='utf-8') as f: raw=json.load(f)
feature_by_fid={f['attributes']['FID']:f for f in raw['features']}

# Blender object helpers
def clear_scene():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
        for b in list(datablocks):
            if b.users==0: datablocks.remove(b)
    scene=bpy.context.scene
    for c in list(scene.collection.children): scene.collection.children.unlink(c)
    return scene

def mat_tex(name, color, rough=.72, metallic=0, scale=18, bump=.07, amount=.08):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); bs=n.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    geo=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=3.5; noise.inputs['Roughness'].default_value=.72
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(*(max(0,c*(1-amount)) for c in color),1); ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(*(min(1,c*(1+amount)) for c in color),1)
    bp=n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=bump; bp.inputs['Distance'].default_value=.018
    m.node_tree.links.new(geo.outputs['Generated'],noise.inputs['Vector']); m.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); m.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color']); m.node_tree.links.new(noise.outputs['Fac'],bp.inputs['Height']); m.node_tree.links.new(bp.outputs['Normal'],bs.inputs['Normal']); m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

def mesh_obj(name, verts, faces, mat, collection):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update(); ob=bpy.data.objects.new(name,me); collection.objects.link(ob); return ob

def box(name, center, size, mat, collection, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center); ob=bpy.context.object; ob.name=name; ob.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob); ob.data.materials.append(mat)
    if bevel>0:
        mod=ob.modifiers.new('Soft masonry arris','BEVEL'); mod.width=bevel; mod.segments=2
        ob.modifiers.new('Weighted facade normals','WEIGHTED_NORMAL')
    return ob

def prism_poly(name, ring, z0, z1, mat, collection):
    n=len(ring); verts=[(x,y,z0) for x,y in ring]+[(x,y,z1) for x,y in ring]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): j=(i+1)%n; faces.append((i,j,n+j,n+i))
    return mesh_obj(name,verts,faces,mat,collection)

def make_windows(ring, story_n, h, zbase, glassmat, mullionmat, style, collection):
    v=[]; f=[]; mv=[]; mf=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
        if L<5: continue
        ux,uy=dx/L,dy/L; ox,oy=uy,-ux
        pitch={'dlr':3.2,'flex':3.6,'heine':4.2,'krach':4.0,'herrick':4.0,'hort':4.2,'dining':4.5,'brick':4.2}.get(style,4.0)
        n=max(1,min(34,int(L/pitch))); step=L/n
        for fl in range(story_n):
            floor_z=zbase+fl*h; wh=min(h*.52,1.8 if style not in ('flex','dlr') else 2.2); sill=floor_z+h*.25
            for k in range(n):
                center=(k+.5)*step
                if step<2.25: continue
                ww=min(step*.62,2.25 if style not in ('flex','dlr') else 2.7)
                lo=center-ww/2; hi=center+ww/2; off=.035
                pts=[]
                for dist,z in [(lo,sill),(hi,sill),(hi,sill+wh),(lo,sill+wh)]: pts.append((a[0]+ux*dist+ox*off,a[1]+uy*dist+oy*off,z))
                ix=len(v); v.extend(pts); f.append((ix,ix+1,ix+2,ix+3))
                # slim mullion strips for the glass panel
                if style in ('dlr','flex','krach'):
                    for frac in (.5,):
                        x=a[0]+ux*(center+ww*(frac-.5))+ox*(off+.008); y=a[1]+uy*(center+ww*(frac-.5))+oy*(off+.008)
                        width=.055; p0=(x-ox*width/2,y-oy*width/2,sill); p1=(x+ox*width/2,y+oy*width/2,sill); p2=(x+ox*width/2,y+oy*width/2,sill+wh); p3=(x-ox*width/2,y-oy*width/2,sill+wh); ix=len(mv); mv.extend([p0,p1,p2,p3]); mf.append((ix,ix+1,ix+2,ix+3))
    if f: mesh_obj('Facade glazing | repeated vision panels',v,f,glassmat,collection)
    if mf: mesh_obj('Curtainwall vertical mullions',mv,mf,mullionmat,collection)

def bands(ring,zs,width,mat,collection):
    v=[]; f=[]
    for z in zs:
        for i,a in enumerate(ring):
            b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
            if L==0: continue
            ox,oy=dy/L,-dx/L; off=.09
            ix=len(v); v.extend([(a[0]+ox*off,a[1]+oy*off,z-width/2),(b[0]+ox*off,b[1]+oy*off,z-width/2),(b[0]+ox*off,b[1]+oy*off,z+width/2),(a[0]+ox*off,a[1]+oy*off,z+width/2)]); f.append((ix,ix+1,ix+2,ix+3))
    if f: mesh_obj('Continuous horizontal facade banding',v,f,mat,collection)

def sign_on_facade(cfg, ring, z, mat, collection):
    # longest suitable outer face receives the building initials/nameplate
    edges=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; L=math.dist(a,b)
        if L>9: edges.append((L,a,b))
    if not edges: return
    L,a,b=max(edges); ux=(b[0]-a[0])/L; uy=(b[1]-a[1])/L; ox,oy=uy,-ux; mid=((a[0]+b[0])/2+ox*.16,(a[1]+b[1])/2+oy*.16,z)
    cv=bpy.data.curves.new(cfg['abbr']+' facade lettering','FONT'); cv.body=cfg['abbr']; cv.size=min(1.5,L*.09); cv.extrude=.006
    ob=bpy.data.objects.new(cfg['abbr']+' cast metal facade sign',cv); collection.objects.link(ob); ob.location=mid; ob.rotation_euler=Vector((ox,oy,0)).to_track_quat('Z','Y').to_euler(); ob.data.materials.append(mat)

def longest_edge(ring):
    choices=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]; L=math.dist(a,b)
        if L>6: choices.append((L,a,b))
    L,a,b=max(choices); ux=(b[0]-a[0])/L; uy=(b[1]-a[1])/L
    return L,((a[0]+b[0])/2,(a[1]+b[1])/2),(ux,uy),(uy,-ux)

def simplify_ring(ring, tolerance=.25):
    ring=list(ring)
    while len(ring)>8:
        best=(float('inf'),None)
        for i,p in enumerate(ring):
            a=ring[i-1]; b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
            if den<1e-10: d=math.dist(p,a)
            else:
                t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)); d=math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
            if d<best[0]: best=(d,i)
        if best[0]>tolerance: break
        ring.pop(best[1])
    return ring

def floor_plates(ring, levels, height, base, mat, collection, footprint_factor=.8):
    # Schematic exposed slabs are kept behind the envelope; add compact perimeter strips only.
    for i in range(levels):
        z=base+i*height+.08; v=[]; f=[]; n=len(ring)
        for p in ring: v.append((p[0],p[1],z))
        f.append(tuple(range(n)))
        mesh_obj('Schematic interior floor plate %02d'%(i+1),v,f,mat,collection)

def roof_gable(ring, z, roofmat, collection, along='long'):
    xs=[p[0] for p in ring]; ys=[p[1] for p in ring]; minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys); dx=maxx-minx; dy=maxy-miny
    # Compact gabled lid over the main rectangular envelope, with restrained overhang.
    ex=.6; minx-=ex; maxx+=ex; miny-=ex; maxy+=ex
    if dx>=dy:
        # ridge runs east-west; two roof slopes meet at north-south center
        ridge=(miny+maxy)/2; rz=z+min(dy*.22,3.4)
        verts=[(minx,miny,z),(maxx,miny,z),(maxx,ridge,rz),(minx,ridge,rz),(minx,maxy,z),(maxx,maxy,z)]
        faces=[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)]
    else:
        ridge=(minx+maxx)/2; rz=z+min(dx*.22,3.4)
        verts=[(minx,miny,z),(ridge,miny,rz),(maxx,miny,z),(minx,maxy,z),(ridge,maxy,rz),(maxx,maxy,z)]
        faces=[(0,1,4,3),(1,2,5,4),(0,3,5,2),(0,2,1)]
    mesh_obj('Pitched standing-seam roof',verts,faces,roofmat,collection)
    # ridge cap
    if dx>=dy: box('Roof ridge cap',( (minx+maxx)/2,ridge,rz+.06),(dx,.18,.12),roofmat,collection)
    else: box('Roof ridge cap',(ridge,(miny+maxy)/2,rz+.06),(.18,dy,.12),roofmat,collection)

def add_interiors(cfg, ring, base, story_h, stories, materials, coll):
    style=cfg['style']; cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
    # Entry lobby floor and limited architectural cue, not a claim of exact plan.
    floor=materials['floor']; wall=materials['trim']; dark=materials['glass']
    floor_plates(ring, stories, story_h, base, floor, coll)
    if style in ('brees','ford','flex','dlr','heine','herrick','krach'):
        # interior atrium / commons modeled only for published use types; sparse and labeled schematic.
        if style in ('brees','ford','flex','dlr','krach'):
            box('Schematic lobby / shared commons floor',(cx,cy,base+.10),(min(18,max(7,(max(x for x,y in ring)-min(x for x,y in ring))*.28)),min(13,max(6,(max(y for x,y in ring)-min(y for x,y in ring))*.22)),.14),floor,coll)
            # furniture is only illustrative, in plan-level schematic
            for j in range(3):
                box('Schematic communal table %d'%j,(cx-3+j*3,cy,base+.65),(2.2,.8,.12),wall,coll,.05)
                for s in (-1,1): box('Schematic chair %d %d'%(j,s),(cx-3+j*3,cy+s*.72,base+.43),(.38,.4,.8),dark,coll,.04)
        if style=='flex':
            # visible two-storey high-bay test volume
            box('High-bay research zone | schematic',(cx-6,cy+8,base+story_h*1.15),(9,12,story_h*2.3),materials['glass'],coll,.08)
        if style=='heine':
            # floorplan source validates central circulation and lecture space; only first-floor schematic cues
            box('Schematic pharmacy retail / reception zone',(cx+8,cy-8,base+.45),(8,6,.9),wall,coll,.08)
            box('Schematic lecture hall zone',(cx-10,cy+8,base+.3),(11,7,.6),dark,coll,.05)

def add_context(cfg, ring, coll, mats):
    style=cfg['style']; xs=[x for x,y in ring]; ys=[y for x,y in ring]; dx=max(xs)-min(xs); dy=max(ys)-min(ys); cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
    # Render-only stage landscape accents remain outside exported asset.
    if style in ('brees','hort','krach'):
        # ivy cue on selected wall via leafy narrow green panels; stylized and restrained
        pass

def build_one(cfg):
    feature=feature_by_fid[cfg['fid']]; a=feature['attributes']; geom=feature['geometry']; ring_geo=geom['rings'][0]
    if ring_geo[0]==ring_geo[-1]: ring_geo=ring_geo[:-1]
    # Project footprint to project local metre frame, position source asset around its footprint bbox center.
    xy=[((p[0]+180)%360-180, p[1]) for p in ring_geo]
    world=[((lon-LON0)*LON_M,(lat-LAT0)*LAT_M) for lon,lat in xy]
    ox=(min(p[0] for p in world)+max(p[0] for p in world))/2; oy=(min(p[1] for p in world)+max(p[1] for p in world))/2
    ring=[(x-ox,y-oy) for x,y in world]
    # Source has occasional very dense small vertices. Keep linework but drop sub-5cm duplicate segments.
    cleaned=[]
    for p in ring:
        if not cleaned or math.dist(p,cleaned[-1])>.04: cleaned.append(p)
    ring=cleaned
    if len(ring)>1 and math.dist(ring[0],ring[-1])<.04: ring.pop()
    ring=simplify_ring(ring,.25)
    area2=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    if area2 < 0: ring.reverse()  # window offsets and exterior normals assume CCW
    scene=clear_scene(); scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.render.resolution_x=760; scene.render.resolution_y=570; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.resolution_percentage=100
    asset=bpy.data.collections.new('Asset_'+cfg['key']); scene.collection.children.link(asset)
    shell=bpy.data.collections.new('Structure'); asset.children.link(shell)
    detail=bpy.data.collections.new('Facade_Details'); asset.children.link(detail)
    interior=bpy.data.collections.new('Schematic_Interior'); asset.children.link(interior)
    ctx=bpy.data.collections.new('Preview_Stage'); scene.collection.children.link(ctx)
    brick=mat_tex(cfg['abbr']+' | warm brick / facade masonry',cfg['color'],.8,0,22,.12,.11)
    trim=mat_tex(cfg['abbr']+' | pale limestone / painted metal',cfg['trim'],.62,.12,12,.055,.06)
    glass=mat_tex(cfg['abbr']+' | blue charcoal architectural glazing',cfg['glass'],.18,.3,8,.015,.04)
    roof=mat_tex(cfg['abbr']+' | graphite roof membrane / metal',(.12,.14,.15),.68,.25,20,.05,.05)
    concrete=mat_tex(cfg['abbr']+' | foundation concrete',(.37,.37,.34),.86,0,24,.12,.07)
    floor=mat_tex(cfg['abbr']+' | schematic terrazzo floor',(.48,.45,.39),.45,0,9,.03,.05)
    mats={'brick':brick,'trim':trim,'glass':glass,'roof':roof,'concrete':concrete,'floor':floor}
    # Foundation, structural shell
    base=-1.0 if cfg['style'] in ('krach','heine','flex') else 0.0
    stories=cfg['stories']; h=cfg['height']/stories
    shellmat=glass if cfg['style']=='dlr' else brick
    prism_poly(cfg['abbr']+' structural shell | GIS outline',ring,base,cfg['height'],shellmat,shell)
    # Reveal footing and parapet/ring cornice
    prism_poly(cfg['abbr']+' raised foundation plinth',ring,base,base+.48,concrete,shell)
    make_windows(ring,stories,h,base,glass,trim,cfg['style'],detail)
    if cfg['style'] in ('dlr','flex','krach','herrick','heine'):
        bands(ring,[base+.32+i*h for i in range(1,stories+1)],.22,trim,detail)
    else: bands(ring,[base+.32+i*h for i in range(1,stories+1)],.20,trim,detail)
    # unique volumes and identifying features
    xs=[x for x,y in ring]; ys=[y for x,y in ring]; minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys); cx=(minx+maxx)/2; cy=(miny+maxy)/2; dx=maxx-minx; dy=maxy-miny
    if cfg['style']=='dining':
        roof_gable(ring,cfg['height'],roof,detail)
        # glased dining frontage / central entrance and raised canopy
        box('Two-storey glass dining atrium',(cx,cy,base+h),(min(dx*.34,18),.24,h*1.55),glass,detail)
        box('Dining court projecting entrance canopy',(cx,miny-.8,base+3.7),(min(dx*.46,24),3.6,.34),trim,detail,.08)
    elif cfg['style']=='hort':
        # Preserve the U-shaped GIS outline in the roof. A bounding-box gable would
        # incorrectly bridge the documented/open courtyard recess.
        prism_poly('Horticulture historic roof | GIS footprint',ring,cfg['height']-.18,cfg['height']+.12,roof,detail)
        # Formal central entrance bay and two-column portico, based on the facade photo.
        L,mid,(ux,uy),(ex,ey)=longest_edge(ring); ang=math.atan2(uy,ux)
        entry=(mid[0]+ex*1.35,mid[1]+ey*1.35)
        canopy=box('Horticulture central entry portico',(entry[0],entry[1],base+2.8),(10,3,.36),trim,detail,.05); canopy.rotation_euler[2]=ang
        for xoff in (-2.8,2.8):
            col=box('Horticulture entry portico column',(entry[0]+ux*xoff,entry[1]+uy*xoff,base+2.25),(.34,.34,4.2),trim,detail,.045); col.rotation_euler[2]=ang
        # Three small roof dormers echo the visible front roofline; exact dimensions estimated.
        for j,xoff in enumerate((-9,0,9)):
            d=(mid[0]+ux*xoff+ex*.55,mid[1]+uy*xoff+ey*.55)
            dormer=box('Horticulture roof dormer %d'%j,(d[0],d[1],cfg['height']+1.25),(3.4,2.2,2.5),brick,detail,.04); dormer.rotation_euler[2]=ang
            win=box('Horticulture dormer glazing %d'%j,(d[0]+ex*1.12,d[1]+ey*1.12,cfg['height']+1.45),(1.6,.07,1.15),glass,detail); win.rotation_euler[2]=ang
    elif cfg['style']=='flex':
        # Alternating glass/brick planes, full-height glazed connector and entrance canopy.
        box('Flex Lab 20-foot entry canopy',(cx,miny-1.3,base+3.7),(16,5.8,.38),trim,detail,.08)
        # highbay roof monitor
        box('High-bay roof monitor',(cx-dx*.25,cy,cfg['height']+1.4),(dx*.22,dy*.34,2.8),trim,detail,.1)
    elif cfg['style']=='dlr':
        # Long curved-like glass research facade and continuous spandrel courses.
        # Slightly rounded vertical end volumes distinguish the research wing.
        box('DLR glazed lobby volume',(cx,cy,base+h*.8),(min(dx*.72,40),min(dy*.2,8),h*1.7),glass,detail,.3)
        box('DLR rooftop mechanical screen',(cx+dx*.21,cy,cfg['height']+1.0),(dx*.34,dy*.26,2.0),trim,detail,.08)
    elif cfg['style']=='heine':
        # 1970s large brick academic block; mechanical cap and rooftop penthouse
        box('Heine Pharmacy rooftop penthouse',(cx,cy,cfg['height']+1.2),(dx*.40,dy*.36,2.4),concrete,detail,.08)
        box('Pharmacy west entrance canopy',(cx,miny-1.05,base+3.3),(min(dx*.42,20),4,.35),trim,detail,.08)
    elif cfg['style']=='herrick':
        # Three readable research masses: low brick laboratory, glass commons, high-bay metal-clad box.
        # GIS outline is stepped and non-rectangular; avoid imposing false block wings
        # across it. Roof equipment and glazing remain cues, while internal wings are
        # not separately partitioned without plan evidence.
        L,mid,(ux,uy),(ex,ey)=longest_edge(ring); ang=math.atan2(uy,ux)
        c=box('Herrick Laboratories glazed entry canopy',(mid[0]+ex*.9,mid[1]+ey*.9,base+3.5),(9,2.8,.34),trim,detail,.06); c.rotation_euler[2]=ang
    elif cfg['style']=='krach':
        # Vertical white pilasters and glass stair bay on one short elevation
        for xoff in (-dx*.38,-dx*.13,dx*.13,dx*.38):
            box('Krach pale vertical facade pier',(cx+xoff,miny-.15,base+cfg['height']*.53),(.34,.3,cfg['height']*1.02),trim,detail,.04)
        box('Krach glazed stair tower',(maxx-dx*.14,cy,base+cfg['height']*.53),(dx*.25,dy*.20,cfg['height']*1.02),glass,detail,.08)
        box('Krach main entrance canopy',(cx,miny-1.1,base+3.7),(min(dx*.46,27),4.2,.4),trim,detail,.08)
    elif cfg['style']=='brees':
        # low academic center with brick entry bay, limestone cornice, ivy accents
        box('Brees center main entry canopy',(cx,miny-.9,base+3.5),(min(dx*.42,25),3.2,.34),trim,detail,.07)
        for j in range(8):
            x=minx+5+j*((dx-10)/7); z=.7+((j*3)%6)*.45
            box('Ivy patch | low wall',(x,miny-.09,z),(.72,.11,1.5),mat_tex(cfg['abbr']+' | ivy green',(.075,.18,.08),.9,0,14,.08,.15),detail)
    # Default roof cap for flat roof, not overclaiming unverified details
    if cfg['style'] not in ('dining','hort'):
        # roof slab has exact footprint form
        prism_poly(cfg['abbr']+' flat roof cap',ring,cfg['height']-.18,cfg['height']+.12,roof,detail)
    # Add unobtrusive name sign on a long facade
    sign_on_facade(cfg,ring,base+min(4.4,cfg['height']*.34),trim,detail)
    add_interiors(cfg,ring,base,h,stories,mats,interior)
    # Annotations in Blender ID properties document modeling interpretation.
    asset['source_feature_id']=cfg['fid']; asset['building_id']=cfg['id']; asset['placement_origin_xy_m']=[ox,oy]; asset['local_coordinates']=True
    # preview stage floor
    ground=mat_tex('Preview | campus lawn',(.19,.26,.16),.95,0,2,.08,.12)
    span=max(dx,dy)*1.20
    box('Preview ground',(0,0,-1.3),(span,span,.25),ground,ctx)
    # Camera from south-west / long side, target center; append stage camera/lights outside asset
    cam_data=bpy.data.cameras.new('Preview camera'); cam=bpy.data.objects.new('Preview camera',cam_data); ctx.objects.link(cam)
    target=Vector((0,0,cfg['height']*.44)); cam.location=Vector((max(dx,dy)*1.18,-max(dx,dy)*1.32,max(dx,dy)*.8)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=48; scene.camera=cam
    ld=bpy.data.lights.new('Large soft key','AREA'); lo=bpy.data.objects.new('Large soft key',ld); ctx.objects.link(lo); lo.location=(dx*.5,-dy*.5,max(dx,dy)*1.2); ld.energy=max(dx,dy)**2*24; ld.shape='DISK'; ld.size=max(dx,dy)*.8
    ld2=bpy.data.lights.new('Cool fill','AREA'); lo2=bpy.data.objects.new('Cool fill',ld2); ctx.objects.link(lo2); lo2.location=(-dx*.9,dy*.45,max(dx,dy)*.65); ld2.energy=max(dx,dy)**2*10; ld2.size=max(dx,dy)*.7
    world=bpy.data.worlds.new('Overcast blue-grey preview') if not bpy.data.worlds else bpy.data.worlds[0]; scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.26,.34,.43,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    # save asset with a camera/stage but exported stable collection stays isolated
    path=OUTDIR/cfg['file']; bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    preview=AUDIT/(cfg['key']+'_preview.png'); scene.render.filepath=str(preview); bpy.ops.render.render(write_still=True)
    # data summary
    bounds=[ [min(xs),max(xs)],[min(ys),max(ys)],[0,cfg['height']] ]
    # save raw feature per building separately with retrieval/method metadata
    feat_doc={'source':GIS_URL,'provider':'Purdue University Campus BuildingShapesZip4 ArcGIS FeatureServer layer 0','retrieved_date':RETRIEVED,'source_crs':'EPSG:4326 (response coordinates requested as WGS84; underlying service spatial reference 102100/3857; endpoint snapshot returned geographic geometry)','source_date':'not provided in feature attributes','feature_id':cfg['fid'],'attributes':a,'geometry':geom}
    (AUDIT/(cfg['key']+'_gis_feature.json')).write_text(json.dumps(feat_doc,indent=2),encoding='utf-8')
    evidence={'building':cfg['name'],'manifest_massing_id':cfg['id'],'detailed_collection':'Asset_'+cfg['key'],'asset_file':'modular/buildings/'+cfg['file'],'retrieved_date':RETRIEVED,'official_gis':{'provider':'Purdue University campus GIS ArcGIS FeatureServer, BuildingShapesZip4 layer 0','service_url':GIS_URL,'query_url':GIS_URL+'/query?where=FID%3D'+str(cfg['fid'])+'&outFields=*&returnGeometry=true&outSR=4326&f=pjson','feature_id':cfg['fid'],'building_abbreviation':cfg['abbr'],'feature_name':a.get('BUILDING_N'),'source_crs':'EPSG:4326 response; original Purdue service uses EPSG:3857/102100 (as identified in prior project source docs)','raw_snapshot':'audit/batch_b_buildings/'+cfg['key']+'_gis_feature.json','source_date':'not supplied','measurement_method':'Official GIS ring transformed by project local geographic linear approximation, duplicate/collinear vertices simplified with iterative maximum local point-to-segment deviation tolerance 0.25m; horizontal origin is the original footprint bbox center.','simplification_tolerance_m':0.25,'transform':f'X=(longitude - {LON0}) * {LON_M:.10f} m/degree; Y=(latitude - {LAT0}) * {LAT_M:.1f} m/degree; Z up in meters; this is approximate project frame, not a surveyed CRS','campus_placement_origin_xy_m':[ox,oy],'local_model_bounds_xy_m':[[min(x for x,y in ring),max(x for x,y in ring)],[min(y for x,y in ring),max(y for x,y in ring)]],'footprint_vertex_count':len(ring),'uncertainty':'GIS service gives no survey tolerance/date; vertex accuracy and wall-to-outline association unverified; overhangs not represented.'},'architectural_references':{'published_facts':cfg['facts'],'source_urls':cfg['source_urls'],'visual_reference_url':cfg['visual_url'],'google_maps_streetview':'Not directly inspected in this subtask; image sources used where cited; model detail claims limited accordingly.'},'modeled_interpretation':{'above_grade_stories':stories,'approximate_wall_height_m':cfg['height'],'height_evidence':'estimated or mixed: '+cfg['facts'],'materials':['procedural textured brick / facade masonry','procedural limestone/painted metal','procedural glazing','procedural roof metal/membrane','schematic concrete and interior floor'], 'interior':'schematic use-based furniture/zone cues only; no claim of architectural room layout except Heine first-floor circulation/lecture/retail cues follow published level-one plan','object_count':len(asset.all_objects),'local_bounds_m':bounds,'geometry_method':'source polygon extruded as structural shell with story-level glazing, facade banding, building-specific massing and entrance cues; roof form as identified by image/source or explicitly estimated'},'validation':{'saved_and_reopened':False,'reopen_check':'root integrator must reopen file and verify stable asset collection','preview_path':'audit/batch_b_buildings/'+cfg['key']+'_preview.png','texture_nodes_connected':True}}
    (AUDIT/(cfg['key']+'_evidence.json')).write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print('BUILT',cfg['key'], 'fid',cfg['fid'],'vertices',len(ring),'objects',len(asset.all_objects),'origin',round(ox,2),round(oy,2),'dims',round(dx,2),round(dy,2),'preview',preview,flush=True)

for cfg in CONFIGS: build_one(cfg)
