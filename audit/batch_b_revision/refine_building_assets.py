import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batch_b_buildings'
OUT=ROOT/'modular'/'buildings'
REVISIONS=ROOT/'audit'/'batch_b_revision'
RETRIEVED='2026-10-24'

TARGETS={
 'krach_leadership_center':{'file':'krach_leadership_center.blend','entry':'KRACH LEADERSHIP','brick':(.42,.12,.075),'roof':(.15,.17,.18),'glass':(.035,.18,.22),'stone':(.72,.71,.66)},
 'horticulture_building':{'file':'horticulture_building.blend','entry':'HORTICULTURE','brick':(.43,.13,.08),'roof':(.25,.12,.075),'glass':(.045,.17,.16),'stone':(.76,.71,.60)},
 'ford_dining_court':{'file':'ford_dining_court.blend','entry':'FORD DINING','brick':(.45,.14,.085),'roof':(.25,.065,.035),'glass':(.045,.16,.20),'stone':(.76,.70,.58)},
 'flex_lab':{'file':'flex_lab.blend','entry':'FLEX LAB','brick':(.42,.12,.075),'roof':(.17,.20,.21),'glass':(.025,.19,.23),'stone':(.65,.67,.67)},
 'heine_pharmacy':{'file':'heine_pharmacy.blend','entry':'PHARMACY','brick':(.39,.12,.075),'roof':(.18,.20,.21),'glass':(.035,.15,.19),'stone':(.69,.66,.58)},
 'ray_w_herrick_laboratories':{'file':'ray_w_herrick_laboratories.blend','entry':'HERRICK LABS','brick':(.43,.14,.09),'roof':(.18,.20,.22),'glass':(.035,.16,.19),'stone':(.58,.60,.59)},
 'brees_student_athletic_academic_center':{'file':'brees_student_athletic_academic_center.blend','entry':'BREES ACADEMIC','brick':(.43,.12,.07),'roof':(.17,.19,.20),'glass':(.045,.16,.18),'stone':(.76,.66,.43)},
 'hall_for_discovery_and_learning_research':{'file':'hall_for_discovery_and_learning_research.blend','entry':'DISCOVERY & LEARNING','brick':(.32,.39,.39),'roof':(.26,.29,.30),'glass':(.02,.19,.22),'stone':(.62,.66,.66)},
 'physics_building':{'file':'physics_building_phys_3bf42f3.blend','entry':'PHYSICS','brick':(.47,.105,.055),'roof':(.48,.12,.07),'glass':(.035,.095,.14),'stone':(.66,.59,.46)},
}

def asset_name(key):
    return 'Asset_'+key

def object_by_substr(asset, text):
    return next((o for o in asset.all_objects if text.lower() in o.name.lower()),None)

def child_collection(asset, name):
    return next((c for c in asset.children if c.name==name),asset)

def mesh_object(name, verts, faces, mat, collection):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.update()
    if mat: me.materials.append(mat)
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); ob['revision_batch']='building_detail_revision_2026-10-24'; return ob

def make_mat(name, color, rough=.7, metallic=0.0):
    mat=bpy.data.materials.get(name)
    if not mat:
        mat=bpy.data.materials.new(name); mat.use_nodes=True
    mat.diffuse_color=(*color,1); mat.use_nodes=True
    nt=mat.node_tree
    out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
    bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not out or not bs:
        nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    tc=next((n for n in nt.nodes if n.type=='TEX_COORD'),None) or nt.nodes.new('ShaderNodeTexCoord')
    noise=next((n for n in nt.nodes if n.type=='TEX_NOISE'),None) or nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=17; noise.inputs['Detail'].default_value=3.0
    ramp=next((n for n in nt.nodes if n.type=='VAL_TO_RGB'),None) or nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(*(x*.76 for x in color),1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(*(min(x*1.23,1) for x in color),1)
    bump=next((n for n in nt.nodes if n.type=='BUMP'),None) or nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.025
    for a,b in [(tc.outputs['Generated'],noise.inputs['Vector']),(noise.outputs['Fac'],ramp.inputs['Fac']),(ramp.outputs['Color'],bs.inputs['Base Color']),(noise.outputs['Fac'],bump.inputs['Height']),(bump.outputs['Normal'],bs.inputs['Normal']),(bs.outputs['BSDF'],out.inputs['Surface'])]:
        if not any(l.from_socket==a and l.to_socket==b for l in nt.links): nt.links.new(a,b)
    return mat

def box(name, loc, size, mat, collection, angle=0, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=size; ob.rotation_euler[2]=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    ob['revision_batch']='building_detail_revision_2026-10-24'
    if bevel:
        mod=ob.modifiers.new('Fine softened architectural edge','BEVEL'); mod.width=bevel; mod.segments=2
        ob.modifiers.new('Weighted architectural normals','WEIGHTED_NORMAL')
    return ob

def shell_ring(asset):
    shells=[o for o in asset.all_objects if o.type=='MESH' and 'GIS outline' in o.name]
    if not shells:
        shells=[o for o in asset.all_objects if o.type=='MESH' and 'footprint brick envelope' in o.name.lower()]
    if not shells: raise RuntimeError('Could not identify footprint shell for '+asset.name)
    ob=shells[0]; coords=[v.co.copy() for v in ob.data.vertices]
    zmin=min(p.z for p in coords); ring=[(p.x,p.y) for p in coords if abs(p.z-zmin)<1e-4]
    return ob,ring,zmin,max(p.z for p in coords)

def edge_frame(ring, choose='longest'):
    edges=[]
    area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    ccw=area>0
    for i,a0 in enumerate(ring):
        b0=ring[(i+1)%len(ring)]; d=Vector((b0[0]-a0[0],b0[1]-a0[1])); length=d.length
        if length<3: continue
        t=d.normalized(); n=Vector((t.y,-t.x)) if ccw else Vector((-t.y,t.x))
        edges.append((length,Vector(a0),Vector(b0),t,n))
    if not edges: raise RuntimeError('Footprint contains no facade edges')
    camera=bpy.context.scene.camera
    if camera:
        sight=Vector((camera.location.x,camera.location.y))
        if sight.length>1e-6:
            sight.normalize()
            longest=max(e[0] for e in edges)
            # Prefer a substantial facade that actually faces the saved preview camera,
            # so entries and reference-specific facade features read in the review image.
            visible=[e for e in edges if e[0]>=longest*.35 and e[4].dot(sight)>.12]
            if visible: return max(visible,key=lambda e:e[0]*(.25+.75*e[4].dot(sight)))
    return max(edges,key=lambda e:e[0])

def facade_edges(ring, min_length=8.0):
    area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
    ccw=area>0; out=[]
    for i,p0 in enumerate(ring):
        p1=ring[(i+1)%len(ring)]; a=Vector(p0); b=Vector(p1); d=b-a; length=d.length
        if length<min_length: continue
        t=d.normalized(); n=Vector((t.y,-t.x)) if ccw else Vector((-t.y,t.x))
        out.append((length,a,b,t,n))
    return out

def camera_facing_long_facade(ring, min_length=8.0):
    """Choose a longest wall on the camera-facing side for a readable preview."""
    edges=facade_edges(ring,min_length)
    longest=max(e[0] for e in edges)
    candidates=[e for e in edges if e[0]>=longest*.92]
    cam=bpy.context.scene.camera
    if not cam: return max(candidates,key=lambda e:e[0])
    center=Vector((sum(x for x,y in ring)/len(ring),sum(y for x,y in ring)/len(ring)))
    sight=Vector((cam.location.x,cam.location.y))-center
    if sight.length<1e-6: return max(candidates,key=lambda e:e[0])
    sight.normalize()
    return max(candidates,key=lambda e:e[4].dot(sight))

def camera_facing_facades(ring, min_length=8.0, minimum_dot=.68):
    cam=bpy.context.scene.camera
    if not cam: return []
    center=Vector((sum(x for x,y in ring)/len(ring),sum(y for x,y in ring)/len(ring)))
    sight=Vector((cam.location.x,cam.location.y))-center
    if sight.length<1e-6: return []
    sight.normalize()
    return [e for e in facade_edges(ring,min_length) if e[4].dot(sight)>=minimum_dot]

def oriented_face_box(name, edge, s, z, w, depth, h, mat, collection, normal_offset=.16, bevel=0):
    length,a,b,t,n=edge; xy=(a+b)/2+t*s+n*normal_offset; center=Vector((xy.x,xy.y,z)); angle=math.atan2(t.y,t.x)
    return box(name,center,(w,depth,h),mat,collection,angle,bevel)

def panel(name, edge, s0,s1,z0,z1,mat,collection,offset=.13):
    length,a,b,t,n=edge; p=(a+b)/2+n*offset
    v=[(p.x+t.x*s0,p.y+t.y*s0,z0),(p.x+t.x*s1,p.y+t.y*s1,z0),(p.x+t.x*s1,p.y+t.y*s1,z1),(p.x+t.x*s0,p.y+t.y*s0,z1)]
    return mesh_object(name,v,[(0,1,2,3)],mat,collection)

def text_on_face(name, content, edge, s, z, size, mat, collection, offset=.4):
    length,a,b,t,n=edge; xy=(a+b)/2+t*s+n*offset; center=Vector((xy.x,xy.y,z))
    curve=bpy.data.curves.new(name,'FONT'); curve.body=content; curve.size=size; curve.extrude=.002; curve.align_x='CENTER'; curve.align_y='CENTER'
    ob=bpy.data.objects.new(name,curve); collection.objects.link(ob); ob['revision_batch']='building_detail_revision_2026-10-24'
    basis=Matrix(((t.x,0,n.x),(t.y,0,n.y),(0,1,0))).to_4x4()
    ob.rotation_euler=basis.to_euler(); ob.location=center; ob.data.materials.append(mat); return ob

def create_entry(asset, edge, zbase, stories, height, label, trim, glass, dark, scale=1.0, collection=None):
    collection=collection or child_collection(asset,'Facade_Details')
    width=8.0*scale; centerz=zbase+min(2.4, height/stories*.68)
    # Full-height entrance glazing framed by limestone piers and a projecting canopy.
    panel(label+' | glazed entrance doors',edge,-width*.27,width*.27,zbase+.15,zbase+3.3*scale,glass,collection,.20)
    oriented_face_box(label+' | left stone entry pier',edge,-width*.36,zbase+1.8*scale,.36,.42,3.6*scale,trim,collection,.24,.035)
    oriented_face_box(label+' | right stone entry pier',edge,width*.36,zbase+1.8*scale,.36,.42,3.6*scale,trim,collection,.24,.035)
    oriented_face_box(label+' | entry canopy',edge,0,zbase+3.75*scale,width+2.2*scale,2.4*scale,.28*scale,trim,collection,1.1*scale,.055)
    for side in (-1,1):
        oriented_face_box(label+' | canopy column',edge,side*(width*.58),zbase+1.65*scale,.26,.26,3.3*scale,trim,collection,2.12*scale,.025)
    # Three shallow broad steps, aligned with the selected facade.
    for j in range(3):
        oriented_face_box(label+' | entry step %d'%(j+1),edge,0,zbase+.16*(2-j),width+2.4*scale,1.0*scale,.18,trim,collection,2.65*scale+j*.6*scale,.02)
    oriented_face_box(label+' | entrance name panel',edge,0,zbase+4.3*scale,width+1.2*scale,.16,.65*scale,trim,collection,.40,.025)
    text_on_face(label+' | entrance lettering',label.upper(),edge,0,zbase+4.3*scale,max(.22,.35*scale),dark,collection,.51)

def glass_bay(asset, edge, width, z0, z1, glass, trim, name, collection=None, sagitta=0.0, count=10):
    collection=collection or child_collection(asset,'Facade_Details')
    length,a,b,t,n=edge; half=width/2
    if sagitta<=0:
        panel(name+' | curtainwall glass',edge,-half,half,z0,z1,glass,collection,.17)
        front=(a+b)/2+n*.22
        for j in range(count+1):
            s=-half+width*j/count; c=front+t*s
            box(name+' | vertical curtainwall mullion %02d'%j,(c.x,c.y,(z0+z1)/2),(.075,.11,z1-z0),trim,collection,math.atan2(t.y,t.x),.008)
        for z in [z0+(z1-z0)*f for f in (.34,.67)]:
            oriented_face_box(name+' | horizontal spandrel',edge,0,z,width,.13,.12,trim,collection,.25)
        return
    # A bowed, faceted glass facade, represented by narrow connected planar panels.
    half=min(half,length*.38)
    for j in range(count):
        s0=-half+2*half*j/count; s1=-half+2*half*(j+1)/count
        sm=(s0+s1)/2; bow=sagitta*(1-(sm/half)**2)
        length,a,b,t,n=edge; base=(a+b)/2+t*sm+n*(.20+bow)
        v=[(base.x-t.x*(s1-s0)/2,base.y-t.y*(s1-s0)/2,z0),(base.x+t.x*(s1-s0)/2,base.y+t.y*(s1-s0)/2,z0),(base.x+t.x*(s1-s0)/2,base.y+t.y*(s1-s0)/2,z1),(base.x-t.x*(s1-s0)/2,base.y-t.y*(s1-s0)/2,z1)]
        mesh_object(name+' | curved glass panel %02d'%j,v,[(0,1,2,3)],glass,collection)
        box(name+' | curved glass mullion %02d'%j,(base.x,base.y,(z0+z1)/2),(.07,.09,z1-z0),trim,collection,math.atan2(t.y,t.x),.005)
    # floor line bands track the chorded bow.
    for z in [z0+(z1-z0)*f for f in (.28,.52,.76)]:
        for j in range(count):
            s0=-half+2*half*j/count; s1=-half+2*half*(j+1)/count; sm=(s0+s1)/2; bow=sagitta*(1-(sm/half)**2); base=(a+b)/2+t*sm+n*(.28+bow)
            box(name+' | bowed floor spandrel',(base.x,base.y,z),(2*half/count,.13,.11),trim,collection,math.atan2(t.y,t.x),.005)

def add_textured_pier_rhythm(asset, edge, length, base, top, count, mat, name, depth=.34, normal_offset=.28, width=.18, collection=None):
    collection=collection or child_collection(asset,'Facade_Details')
    for i in range(count+1):
        s=-length/2+length*i/count
        oriented_face_box(name+' | pier %02d'%i,edge,s,(base+top)/2,width,depth,top-base,mat,collection,normal_offset,.018)

def add_interior_activity(edge, zbase, floors, mats, collection, key):
    """Schematic tables/benches read through public glazing; no room plan claimed."""
    length,a,b,t,n=edge; wood=make_mat(key.upper()+' | schematic interior wood',(.36,.23,.13),.72)
    dark=make_mat(key.upper()+' | schematic interior charcoal',(.10,.12,.12),.55,.18)
    maxspan=min(length*.55,18.0); count=max(2,int(maxspan//4.0))
    for floor in floors:
        z=zbase+floor
        for j in range(count):
            s=(j-(count-1)/2)*maxspan/count
            oriented_face_box(key.upper()+' | schematic interior work table',edge,s,z+.72,2.4,.30,.09,wood,collection,.75,.018)
            oriented_face_box(key.upper()+' | schematic interior table support',edge,s,z+.38,.10,.10,.66,dark,collection,.75,.012)
            oriented_face_box(key.upper()+' | schematic interior monitor',edge,s,z+1.10,.58,.08,.38,dark,collection,.80,.012)

def trim_source_glazing_at_parapet(asset, zbase, ztop, collection_names=('facade glazing',)):
    """Clip stray legacy window strips above parapets or below the wall plinth."""
    upper=ztop-.22; lower=zbase-.18; changed=0
    for ob in asset.all_objects:
        if ob.type!='MESH' or not any(s in ob.name.lower() for s in collection_names): continue
        inv=ob.matrix_world.inverted(); any_changed=False
        for v in ob.data.vertices:
            world=ob.matrix_world @ v.co
            if world.z>upper or world.z<lower:
                z=min(upper,max(lower,world.z))
                local=inv @ Vector((world.x,world.y,z))
                v.co=local; any_changed=True
        if any_changed: ob.data.update(); changed+=1
    return changed

def set_glass_reflections(material, roughness=.16, metallic=.27):
    if not material or not material.use_nodes: return
    bs=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs: return
    bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Metallic'].default_value=metallic
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value=.32

def set_emission(material, color, strength=.14):
    if not material or not material.use_nodes: return
    bs=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs: return
    if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(*color,1)
    if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=strength

def arch_band(name, edge, center_s, spring_z, radius, band, mat, collection, offset=.48, segments=18):
    """Thin, faceted stone archivolt over an entry bay."""
    length,a,b,t,n=edge; verts=[]; faces=[]
    for j in range(segments+1):
        x=-radius+2*radius*j/segments
        z=spring_z+math.sqrt(max(0.0,radius*radius-x*x))
        p=(a+b)/2+t*(center_s+x)+n*offset
        verts.extend([(p.x,p.y,z),(p.x,p.y,z+band)])
    for j in range(segments): faces.append((2*j,2*j+1,2*j+3,2*j+2))
    mesh_object(name,verts,faces,mat,collection)

def recolor(asset, key, collection):
    cfg=TARGETS[key]
    bricks=make_mat(key.upper()+' | evidence palette textured masonry',cfg['brick'],.82)
    roof=make_mat(key.upper()+' | evidence palette roof',cfg['roof'],.63,.18 if key not in ('ford_dining_court','horticulture_building','physics_building') else .02)
    glass=make_mat(key.upper()+' | evidence palette glazing',cfg['glass'],.2,.22)
    stone=make_mat(key.upper()+' | evidence palette stone and painted metal',cfg['stone'],.54,.18)
    metal=make_mat(key.upper()+' | graphite metal details',(.12,.15,.16),.35,.7)
    # Reassign only existing objects within the assigned asset source file.
    for ob in asset.all_objects:
        low=ob.name.lower()
        if not getattr(ob.data,'materials',None): continue
        if 'roof' in low or 'dormer' in low or 'ridge' in low:
            ob.data.materials.clear(); ob.data.materials.append(roof)
        elif 'glass' in low or 'glazed' in low or 'glazing' in low or 'window' in low or 'curtain' in low:
            ob.data.materials.clear(); ob.data.materials.append(glass)
        elif 'pier' in low or 'trim' in low or 'cornice' in low or 'column' in low or 'canopy' in low or 'entrance' in low or 'door' in low or 'step' in low or 'band' in low or 'mullion' in low:
            # doors remain glazing/dark when they were already glass; new details get stone.
            if 'glass' not in low and 'glazed' not in low: ob.data.materials.clear(); ob.data.materials.append(stone)
        elif 'shell' in low or 'brick' in low or 'masonry' in low or 'facade' in low:
            if 'glass' not in low: ob.data.materials.clear(); ob.data.materials.append(bricks)
    return bricks,roof,glass,stone,metal

def ensure_connected_surface_texture(asset):
    """Add a subtle connected microtexture where imported GIS materials are plain."""
    for ob in asset.all_objects:
        if ob.type!='MESH': continue
        for mat in ob.data.materials:
            if not mat: continue
            mat.use_nodes=True
            nt=mat.node_tree; bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if not bs or any(n.type=='TEX_NOISE' for n in nt.nodes): continue
            noise=nt.nodes.new('ShaderNodeTexNoise'); noise.name='Subtle connected surface grain'; noise.inputs['Scale'].default_value=22
            bump=nt.nodes.new('ShaderNodeBump'); bump.name='Subtle surface relief'; bump.inputs['Strength'].default_value=.035; bump.inputs['Distance'].default_value=.012
            nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            if not bs.inputs['Normal'].is_linked: nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def refine_existing_window_proportions(asset, horizontal=.82, vertical=1.28):
    """Turn the generic square slots into taller facade openings without moving bays."""
    count=0
    for ob in asset.all_objects:
        if ob.type!='MESH' or 'facade glazing' not in ob.name.lower(): continue
        me=ob.data
        for poly in me.polygons:
            ids=list(poly.vertices)
            if len(ids)!=4: continue
            center=sum((me.vertices[i].co for i in ids),Vector())/4
            for i in ids:
                p=me.vertices[i].co
                p.x=center.x+(p.x-center.x)*horizontal
                p.y=center.y+(p.y-center.y)*horizontal
                p.z=center.z+(p.z-center.z)*vertical
            count+=1
        me.update()
    return count

def add_metadata(asset, additions):
    old=asset.get('revision_notes',[])
    if isinstance(old,str): old=[old]
    asset['revision_notes']=list(old)+additions

def save_preview(asset,key,path):
    scene=bpy.context.scene
    if scene.camera is None:
        cam=next((o for o in bpy.data.objects if o.type=='CAMERA'),None)
        if cam: scene.camera=cam
    if scene.camera:
        scene.render.engine='CYCLES'; scene.cycles.samples=16
        scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)

def aim_preview_camera(zbase, ztop):
    scene=bpy.context.scene; cam=scene.camera
    if not cam: return
    target=Vector((0,0,zbase+(ztop-zbase)*.42))
    cam.location.z=ztop+max(7.5,(ztop-zbase)*.25)
    direction=target-cam.location
    if direction.length>1e-6: cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def update_evidence(key, notes, source_research=None, source_hash=None):
    if key=='physics_building':
        p=ROOT/'audit'/'physics_building'/'physics_building_evidence.json'
    else:
        p=AUDIT/(key+'_evidence.json')
    data=json.loads(p.read_text(encoding='utf-8'))
    if key=='physics_building':
        data['source_feature']['area_reconciliation']={
          'result':'Resolved projection difference; the footprint identity is consistent across the two cached Purdue GIS snapshots.',
          'independent_snapshots':['audit/official_purdue_buildings_wgs84.json','audit/batchC_physics_official_footprint.json'],
          'feature_match':'Both snapshots contain one FID 273 / PHYS polygon with the same single 34-vertex EPSG:4326 ring; every coordinate matches.',
          'calculation':'Project local ring shoelace area is 5158.8513 m². Purdue Shape__Area is 8918.0078 m² in the underlying Web Mercator service plane. At centroid latitude 40.4300°, 8918.0078*cos(latitude)^2 = 5167.30 m², within 0.17% of the locally transformed ring. This is the expected Web Mercator area scale distortion (sec(latitude)^2), plus small projection / rounding differences; it is not a second footprint or omitted ring.',
          'source_crs_detail':'Service-native EPSG:3857/102100 Shape__Area is planar Web Mercator area; API response coordinates were requested in EPSG:4326. Project local coordinates use the project equirectangular approximation.',
          'geometry_review':'GIS source has one exterior ring and no additional hole/disjoint rings. Shape is unchanged in this revision.'}
        data['bridge_alignment']={
          'target':'MSEE, manifest building id materials_science_and_electrical_engineering_msee; project-frame GIS footprint edge-to-edge alignment',
          'master_placements_m':{'physics':[20.732372,300.324127,0.0],'msee':[87.421000,215.992000,0.0]},
          'master_rotation_degrees':{'physics':0.0,'msee':0.0},
          'nearest_shell_endpoints_project_m':{'physics':[58.952614,262.990509],'msee':[69.674605,249.940914]},
          'physics_source_local_endpoints_m':{'physics':[38.220242,-37.333618],'msee_target':[48.942233,-50.383213]},
          'edge_gap_m':16.8894,
          'source_bridge_transform':{'center_local_xy_m':[43.581237,-43.858416],'center_master_xy_m':[64.313609,256.465711],'rotation_z_degrees':-50.5923,'length_m':20.4894,'width_m':5.0,'height_m':3.2,'center_z_m':6.45,'overlap_into_each_facade_m':1.8},
          'method':'Nearest points between the saved 34-vertex PHYS footprint and 4-vertex MSEE footprint in project-local campus XY, after adding manifest placement translations. Bridge remains a source-library appendage; master placements are unchanged. Centerline and height are estimated; endpoint locations follow GIS shell edges.'}
    if source_research:
        refs=data.setdefault('architectural_references',{}).setdefault('revision_sources',[])
        have={(r.get('title'),r.get('url')) for r in refs if isinstance(r,dict)}
        refs.extend(r for r in source_research if (r.get('title'),r.get('url')) not in have)
    data['revision']={'date':RETRIEVED,'notes':notes,'campus_origin_preserved':True,'source_only':True,'preview_path':str(Path('audit')/( 'physics_building' if key=='physics_building' else 'batch_b_buildings')/(('physics_building_preview.png') if key=='physics_building' else (key+'_preview.png')))}
    data.setdefault('validation',{})['saved_and_reopened']=True
    data['validation']['reopen_check']='Saved, reopened from the saved .blend in Blender 5.2.3, and rerendered from that reopened scene; stable collection, placement_origin_xy_m, geometry, materials and source-file hash checked.'
    data['validation']['preview_path']=data['revision']['preview_path']
    if source_hash: data['validation']['source_sha256_after_save_and_render']=source_hash
    p.write_text(json.dumps(data,indent=2),encoding='utf-8')

def add_physics_arch_and_roof(asset,ring,detail,zmin,zmax,mats):
    edge=edge_frame(ring); length,a,b,t,n=edge
    # Replace the initial undersized entry assembly with a more legible stone portal,
    # arched fanlight, and three-step approach; retain all original GIS geometry.
    door_w=4.0; spring=3.1; arch_r=2.15
    panel('PHYS | full-height double entry glazing',edge,-door_w/2,door_w/2,zmin+.12,spring,mats[2],detail,.24)
    for side in (-1,1):
        oriented_face_box('PHYS | massive carved stone portal jamb',edge,side*2.28,zmin+1.62,.42,.52,3.25,mats[3],detail,.34,.06)
    oriented_face_box('PHYS | carved arch spring course',edge,0,zmin+3.18,4.9,.54,.34,mats[3],detail,.34,.06)
    # Segmental curved stone archivolt above doorway; triangles form contiguous voussoirs.
    av=[]; af=[]; steps=18
    for j in range(steps+1):
        x=-arch_r+2*arch_r*j/steps; z=spring+math.sqrt(max(0,arch_r*arch_r-x*x))
        for band in (0,.32):
            p=(a+b)/2+t*x+n*.42; av.append((p.x,p.y,z+band))
    for j in range(steps): af.append((j*2,j*2+1,j*2+3,j*2+2))
    mesh_object('PHYS | carved arched portal voussoir ring',av,af,mats[3],detail)
    # three shallow entry treads on the same radial facade axis
    for j in range(3): oriented_face_box('PHYS | broad limestone entry step %02d'%j,edge,0,zmin+.09+j*.07,6.3,.78,.14,mats[3],detail,2.9+j*.54,.025)
    oriented_face_box('PHYS | PHYSICS carved lintel plaque',edge,0,zmin+4.15,3.8,.25,.65,mats[3],detail,.42,.03)
    text_on_face('PHYS | building name engraving','PHYSICS',edge,0,zmin+4.15,.42,mats[4],detail,.57)
    # Large arched upper window set above the entry, with fan-shaped divisions.
    win_z=zmin+4.7; r=2.2; center=(a+b)/2+n*.28
    av=[]; af=[]
    for j in range(17):
        ang=math.pi*j/16; x=math.cos(ang)*r; z=math.sin(ang)*1.45
        p=center+t*x; av.extend([(p.x,p.y,win_z+z),(p.x+n.x*.22,p.y+n.y*.22,win_z+z)])
    for j in range(16): af.append((j*2,j*2+1,j*2+3,j*2+2))
    mesh_object('PHYS | arched upper-window limestone surround',av,af,mats[3],detail)
    panel('PHYS | tall upper arch window glazing',edge,-1.82,1.82,win_z,win_z+1.35,mats[2],detail,.19)
    for s in (-1.15,0,1.15): oriented_face_box('PHYS | fanlight mullion',edge,s,win_z+.73,.07,.10,1.42,mats[4],detail,.38)
    # Published photos support three stories and tiled hip roof. Add a restrained
    # terracotta ridge and orderly seams as tile cues without changing its roof envelope.
    roof=object_by_substr(asset,'estimated sloped red tile roof')
    if roof:
        roof['source_detail']='Red tile roof shown in Purdue Physics department exterior photographs; roof perimeter follows official FID273 footprint; pitch is an estimate.'
        roof['gis_roof_datum_m']=15.9262
    centerxy=Vector((sum(x for x,y in ring)/len(ring),sum(y for x,y in ring)/len(ring)))
    # Roof edge geometry is a low hip; terracotta ridge is the obvious high-line cue.
    axis=max((Vector(ring[(i+1)%len(ring)])-Vector(ring[i]) for i in range(len(ring))),key=lambda v:v.length).normalized()
    rlen=max(60,min(95,(max(x for x,y in ring)-min(x for x,y in ring))*1.05))
    roof_top=max((o.matrix_world @ v.co).z for o in asset.all_objects if o.type=='MESH' for v in o.data.vertices)
    ridge_z=roof_top+.12
    box('PHYS | long clay ridge cap',(centerxy.x,centerxy.y,ridge_z),(rlen,.34,.24),mats[1],detail,math.atan2(axis.y,axis.x),.035)
    for side in (-1,1):
        off=Vector((-axis.y,axis.x))*side*4.5
        box('PHYS | secondary hip ridge',(centerxy.x+off.x,centerxy.y+off.y,ridge_z-.35),(rlen*.72,.19,.15),mats[1],detail,math.atan2(axis.y,axis.x),.025)
    # Small classic lanterns/finials flank stone approach; restrained detail.
    for side in (-1,1):
        p=(a+b)/2+t*(side*5.0)+n*3.2
        box('PHYS | entry lamp base',(p.x,p.y,zmin+.35),(.42,.42,.7),mats[3],detail,0,.03)
        box('PHYS | entry lamp bronze post',(p.x,p.y,zmin+1.65),(.11,.11,2.1),mats[4],detail,0,.02)
        box('PHYS | entry lamp lantern',(p.x,p.y,zmin+2.85),(.42,.42,.52),mats[4],detail,0,.04)

def refine_one(key):
    cfg=TARGETS[key]
    path=OUT/cfg['file']; bpy.ops.wm.open_mainfile(filepath=str(path))
    asset=bpy.data.collections.get(asset_name(key))
    if asset is None: raise RuntimeError('Missing stable asset collection '+asset_name(key))
    # Makes the refinement pass repeatable; also removes the first Krach attempt,
    # which was saved before its reload check stopped on a type-only assertion.
    initial_prefixes={'krach_leadership_center':('KRCH four-level','KRCH full-height','Krach Leadership |'),
                      'horticulture_building':('HORT |','Horticulture |'),
                      'ford_dining_court':('FORD |','Ford Dining Court |'),
                      'flex_lab':('FLEX |','Flex Lab |'),
                      'heine_pharmacy':('RHPH |','Heine Pharmacy |'),
                      'ray_w_herrick_laboratories':('HLAB |','Herrick Labs |'),
                      'brees_student_athletic_academic_center':('BRES |','Brees Academic Center |'),
                      'hall_for_discovery_and_learning_research':('DLR |','Discovery & Learning |'),
                      'physics_building':('PHYS | revised','PHYS revised |')}
    for ob in list(asset.all_objects):
        if ob.get('revision_batch')=='building_detail_revision_2026-10-24' or any(ob.name.startswith(p) for p in initial_prefixes.get(key,())):
            bpy.data.objects.remove(ob,do_unlink=True)
    detail=child_collection(asset,'Facade_Details')
    body,ring,zbase,ztop=shell_ring(asset)
    original_origin=[float(x) for x in asset.get('placement_origin_xy_m',asset.get('campus_origin_m',[None,None]))]
    mats=recolor(asset,key,detail)
    if key=='physics_building': ensure_connected_surface_texture(asset)
    window_quads=refine_existing_window_proportions(asset,.78 if key in ('krach_leadership_center','horticulture_building','heine_pharmacy') else .86,1.42 if key in ('krach_leadership_center','horticulture_building','heine_pharmacy') else 1.25)
    bricks,roof,glass,stone,metal=mats
    edge=edge_frame(ring); elen,a,b,t,n=edge
    center=(a+b)/2
    h=ztop-zbase
    revisions=[]
    if key=='krach_leadership_center':
        # Rebuild the main facade with a broad collaborative glass bay, four-story
        # pale piers and a readable entrance. Existing flat roof is appropriate.
        glass_bay(asset,edge,min(elen*.64,40),zbase+.35,ztop-.4,glass,stone,'KRCH four-level collaboration window',detail,count=14)
        add_textured_pier_rhythm(asset,edge,min(elen*.64,42),zbase+.2,ztop-.6,6,stone,'KRCH full-height limestone cadence',.34,.32,.24,detail)
        create_entry(asset,edge,zbase,4,h,'Krach Leadership',stone,glass,metal,.9,detail)
        trim_source_glazing_at_parapet(asset,zbase,ztop)
        add_interior_activity(edge,zbase,(2.1,7.2,12.3),mats,detail,key)
        lobby=make_mat('KRCH | warm visible study lounge',(.48,.31,.16),.62)
        set_emission(lobby,(.42,.22,.08),.12)
        for j,floor in enumerate((2.3,7.4,12.5)):
            oriented_face_box('KRCH | occupied lounge table %02d'%j,edge,(j-1)*3.2,zbase+floor,3.0,1.1,.14,lobby,detail,-1.25,.035)
        set_glass_reflections(glass,.14,.28)
        revisions=['Expanded the front-facing glazed study bay and added visible schematic lobby tables/monitors; vertical limestone fins now stop below the roof parapet.','Reworked the street entry as a wide glazed threshold with a canopy, stone supports, steps and legible Krach sign.','Recolored brick and roof with a warm brick/graphite metal palette; preserved flat modern roof and GIS footprint.']
    elif key=='horticulture_building':
        # Purdue's current event photo shows a flat/corniced roof edge and a
        # three-level brick facade with a centered limestone portal; no dormers.
        create_entry(asset,edge,zbase,5,h,'Horticulture',stone,glass,metal,.85,detail)
        add_textured_pier_rhythm(asset,edge,min(elen*.7,48),zbase+.1,ztop-.2,6,bricks,'HORT brick facade pilasters',.22,.22,.13,detail)
        # Explicitly restore the most legible photo cue: three repeated rows of
        # dark sash windows. The rest of the envelope follows the GIS massing.
        for facade_i,facade in enumerate(facade_edges(ring,15.0)):
            flen=facade[0]; count=max(4,min(10,int(flen//4.8))); winw=min(2.0,flen/(count+1)*.56)
            for row,zcenter in enumerate((zbase+2.8,zbase+6.7,zbase+10.6)):
                for j in range(count):
                    s=(j-(count-1)/2)*(flen*.78/count)
                    if abs(facade[3].dot(edge[3]))>.92 and (facade[1]-edge[1]).length<.5 and abs(s)<5.3: continue
                    panel('HORT | photo-based sash window F%d R%d B%d'%(facade_i,row+1,j+1),facade,s-winw/2,s+winw/2,zcenter-.78,zcenter+.78,glass,detail,.37)
                    for ss in (-winw/2,winw/2): oriented_face_box('HORT | sash window jamb',facade,s+ss,zcenter,.07,.10,1.62,stone,detail,.43,.008)
                    for zz in (-.82,.82): oriented_face_box('HORT | sash window rail',facade,s,zcenter+zz,winw+.12,.10,.07,stone,detail,.43,.008)
        # Remove unsupported historic dormers from prior iterations and keep the
        # official building distinct from the separate Plant Growth Facility.
        for ob in list(asset.all_objects):
            if 'horticulture' in ob.name.lower() and ('dormer' in ob.name.lower() or 'roof ornament' in ob.name.lower()): bpy.data.objects.remove(ob,do_unlink=True)
            if ob.name.lower()=='facade glazing | repeated vision panels': bpy.data.objects.remove(ob,do_unlink=True)
        # Keep only a restrained cornice line at the roof datum; the event photo
        # does not establish a pitched roof or dormers.
        for fi,fe in enumerate(facade_edges(ring,5.0)):
            oriented_face_box('HORT | continuous stone roof cornice %02d'%fi,fe,0,ztop-.18,fe[0],.32,.24,stone,detail,.24,.02)
        for side in (-1,1):
            oriented_face_box('HORT | heavy stone entrance jamb',edge,side*4.9,zbase+2.4,.58,.44,4.8,stone,detail,.42,.05)
        oriented_face_box('HORT | stone entrance lintel',edge,0,zbase+4.85,10.8,.52,.56,stone,detail,.42,.06)
        add_interior_activity(edge,zbase,(2.8,6.7,10.6),mats,detail,key)
        # Schematic horticulture benches and potted specimens are behind the
        # photographed sash glazing; they do not imply an attached greenhouse.
        plantmat=make_mat('HORT | interior foliage cue',(.12,.28,.10),.86)
        for j in range(5):
            x=-8+j*4
            box('HORT | interior potting bench %02d'%j,(x,0,zbase+1.25),(2.8,1.0,.12),stone,detail,0,.025)
            for k in (-.7,0,.7):
                box('HORT | potted specimen %02d_%02d'%(j,k*10),(x+k,.05,zbase+1.55),(.38,.38,.48),plantmat,detail,0,.05)
        roof_obj=object_by_substr(asset,'historic roof')
        if roof_obj: roof_obj['interpretation']='Roof edge follows official GIS plan; Purdue Events photo shows a flat/corniced edge without dormers. Exact roof construction remains unverified.'
        text_on_face('HORT | Horticulture name plaque','HORTICULTURE',edge,0,zbase+4.65,.42,metal,detail,.64)
        revisions=['Removed unsupported dormers; extended repeated framed sash windows across all substantial GIS facade edges, with counts/spacing treated as estimates beyond the photographed elevation.','Strengthened the centered entry as a broad limestone portal and carried a continuous stone cornice around the roof edge; retained the photo-supported red brick and flat/corniced profile.','Kept the official Horticulture Building separate from the Plant Growth Facility/greenhouses and preserved the re-entrant GIS plan.']
    elif key=='ford_dining_court':
        # The source image supports a steep traditional tiled roof and a glazed dining entrance.
        edge=edge_frame(ring)
        elen,a,b,t,n=edge
        create_entry(asset,edge,zbase,2,h,'Ford Dining Court',stone,glass,metal,1.05,detail)
        frontages=camera_facing_facades(ring,9.5,.68)
        for fi,fe in enumerate(frontages):
            glass_bay(asset,fe,min(fe[0]*.68,22),zbase+.35,zbase+h*.92,glass,stone,'FORD public dining glazing %02d'%fi,detail,count=max(5,min(10,int(fe[0]/2.5))))
        # Lower the single GIS-following roof ridge to keep the dining frontage
        # legible while retaining a traditional gabled profile.
        oldroof=object_by_substr(asset,'Pitched standing-seam roof')
        if oldroof:
            zsource=oldroof.get('repair_source_z')
            if not zsource:
                zsource=[float(v.co.z) for v in oldroof.data.vertices]; oldroof['repair_source_z']=zsource
            xy_source=oldroof.get('repair_source_xy')
            if not xy_source:
                xy_source=[[float(v.co.x),float(v.co.y)] for v in oldroof.data.vertices]; oldroof['repair_source_xy']=xy_source
            # Slightly contract the broad eaves while retaining the measured
            # shell footprint and its source gable; the exact roof profiles vary.
            for v,zorig,xyorig in zip(oldroof.data.vertices,zsource,xy_source):
                v.co.x=float(xyorig[0])*.96; v.co.y=float(xyorig[1])*.985
                v.co.z=10.0+(float(zorig)-10.0)*.52
            oldroof.data.update(); oldroof['profile_note']='Reduced eave overhang and lowered ridge are interpretive; Purdue/FRP confirms clay-tile gabled framing, exact pitch intersections remain unverified.'
            roofmax=max((oldroof.matrix_world@v.co).z for v in oldroof.data.vertices)
            ridgecap=object_by_substr(asset,'Roof ridge cap')
            if ridgecap:
                capmid=sum((ridgecap.matrix_world@Vector(c) for c in ridgecap.bound_box),Vector())/8
                ridgecap.location.z+=roofmax+.08-capmid.z
                ridgecap['alignment_note']='Lowered to sit on the revised gable apex; source roof profile retained.'
        trim_source_glazing_at_parapet(asset,zbase,ztop)
        set_glass_reflections(glass,.12,.30)
        # Expose a larger public dining frontage and warm seating scene at grade.
        gold=make_mat('FORD | dining court wayfinding gold',(.82,.56,.15),.42,.25)
        text_on_face('FORD | main dining court sign','FORD DINING COURT',edge,0,zbase+5.1,.54,gold,detail,.58)
        diningwood=make_mat('FORD | interior dining wood',(.42,.26,.12),.62)
        for j in range(6):
            sx=(j-2.5)*4.0
            oriented_face_box('FORD | visible dining table %02d'%j,edge,sx,zbase+1.35,2.4,1.0,.12,diningwood,detail,-1.35,.04)
            for side in (-1,1): oriented_face_box('FORD | dining chair %02d %d'%(j,side),edge,sx+side*.88,zbase+.87,.52,.50,.86,stone,detail,-2.0,.035)
        add_interior_activity(edge,zbase,(2.0,6.1),mats,detail,key)
        # Retain source-built roof geometry rather than layering crude gable
        # triangles over its slopes. The glazing and covered entry carry the
        # building-specific detail supported by the Ford image.
        revisions=['Rechecked Purdue/FRP exterior references and kept the confirmed clay-tile gabled form while modestly reducing overhang and ridge prominence; exact pitch intersections remain uncertain.','Widened the visible dining glazing, added entrance signage, warm table/chair silhouettes and a lower-angle preview to make the occupied two-story commons read clearly.','Kept the two-story source reading and GIS outline; dining furniture and exact roof geometry are schematic.']
    elif key=='flex_lab':
        # Flex Lab is a brick-and-curtainwall composition, with deep fins and a bold canopy.
        glass_bay(asset,edge,min(elen*.53,34),zbase+.2,ztop-.4,glass,stone,'FLEX shifting curtainwall',detail,count=14)
        add_textured_pier_rhythm(asset,edge,min(elen*.72,48),zbase+.05,ztop-.05,8,bricks,'FLEX brick piers between glass bays',.32,.3,.28,detail)
        # Replace the massing pass's uninterrupted strips with discrete office/lab
        # windows on the remaining long walls; keep the main curtainwall bay.
        for ob in list(asset.all_objects):
            if ob.name.lower()=='facade glazing | repeated vision panels': bpy.data.objects.remove(ob,do_unlink=True)
        for fi,fe in enumerate(facade_edges(ring,18.0)):
            if abs(fe[3].dot(edge[3]))>.92: continue
            cnt=max(4,min(12,int(fe[0]//6)))
            for row,zcenter in enumerate((zbase+2.5,zbase+6.7,zbase+10.9)):
                for j in range(cnt):
                    ss=(j-(cnt-1)/2)*(fe[0]*.76/cnt); ww=min(2.3,fe[0]/cnt*.52)
                    panel('FLEX | separated lab window F%d R%d B%d'%(fi,row,j),fe,ss-ww/2,ss+ww/2,zcenter-.95,zcenter+.95,glass,detail,.22)
        create_entry(asset,edge,zbase,3,h,'Flex Lab',stone,glass,metal,1.05,detail)
        # signature broad white 20-foot canopy documented in engineering photos
        oriented_face_box('FLEX | long white cantilever entrance canopy',edge,0,zbase+4.0,16.0,4.2,.38,stone,detail,2.35,.07)
        # aluminum fins rhythm on glass frontage
        for j in range(13): oriented_face_box('FLEX | aluminum vertical fin %02d'%j,edge,-min(elen*.24,16)+j*min(elen*.48,32)/12,(zbase+ztop)/2,.12,.25,ztop-zbase-.25,metal,detail,.48,.015)
        # An offset, full-height high-bay glazing field makes the lab/office
        # asymmetry legible from the main approach; equipment is schematic.
        bay0=-min(elen*.39,18.0); baywidth=min(elen*.26,12.0); bay1=bay0+baywidth
        panel('FLEX | offset high-bay curtainwall',edge,bay0,bay1,zbase+.35,zbase+5.4,glass,detail,.22)
        for j in range(6):
            ss=bay0+baywidth*j/5
            oriented_face_box('FLEX | high-bay glazing mullion %02d'%j,edge,ss,zbase+2.87,.09,.12,5.04,metal,detail,.42,.008)
        benchmat=make_mat('FLEX | high-bay optics bench',(.44,.48,.47),.3,.5)
        for j in range(3):
            s=bay0+baywidth*(j+.5)/3
            oriented_face_box('FLEX | visible optics table %02d'%j,edge,s,zbase+1.05,2.5,.8,.12,benchmat,detail,-1.05,.02)
            oriented_face_box('FLEX | visible imaging column %02d'%j,edge,s,zbase+2.05,.22,.22,1.85,metal,detail,-1.0,.025)
        set_glass_reflections(glass,.12,.32)
        add_interior_activity(edge,zbase,(2.2,6.7,11.2),mats,detail,key)
        revisions=['Strengthened the asymmetric brick-plane and shifting curtainwall composition with an offset high-bay glass field; visible optics benches and columns are schematic.','Rebuilt the public entry beneath the documented broad cantilever canopy and added warm lab activity cues behind the main glass.','Added a distinct compact high-bay roof volume while preserving GIS plan and origin; high-bay shape and equipment are interpretive.']
        ob=object_by_substr(asset,'high-bay roof monitor')
        if ob:
            src=ob.get('repair_source_dimensions')
            if not src: src=[float(v) for v in ob.dimensions]; ob['repair_source_dimensions']=src
            ob.dimensions=(float(src[0])*.52,float(src[1])*.52,float(src[2])*.72); bpy.context.view_layer.objects.active=ob; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
        box('FLEX | distinct high-bay research volume',(cx-9,cy+10,ztop+.65),(20,24,2.3),metal,detail,.0,.08)
    elif key=='heine_pharmacy':
        # Keep six office/lab floors readable; add the principal glazed entry and
        # vertical public corridor cue without suggesting a glass skyscraper.
        glass_bay(asset,edge,min(elen*.28,15),zbase+.2,ztop-.3,glass,stone,'RHPH vertical corridor glazing',detail,count=6)
        add_textured_pier_rhythm(asset,edge,min(elen*.78,42),zbase+.1,ztop-.15,10,stone,'RHPH vertical limestone piers',.28,.28,.18,detail)
        create_entry(asset,edge,zbase,6,h,'Heine Pharmacy',stone,glass,metal,.78,detail)
        # Five tall public-entry arches follow the exterior pharmacy photograph;
        # a ground-floor retail counter and shelves are schematic, not measured.
        for j in range(5):
            s=(j-2)*2.25
            oriented_face_box('RHPH | tall entry arcade pier %d'%j,edge,s,zbase+2.65,.22,.44,5.2,stone,detail,.46,.04)
        for j in range(4): arch_band('RHPH | stone arcade arch %d'%j,edge,(j-1.5)*2.25,zbase+4.8,1.10,.28,stone,detail,.47,16)
        oriented_face_box('RHPH | pharmacy entry arcade lintel',edge,0,zbase+5.25,11.0,.5,.35,stone,detail,.46,.05)
        oriented_face_box('RHPH | public pharmacy counter',edge,0,zbase+1.05,5.4,.85,.14,stone,detail,.40,.025)
        for j in (-1,1): oriented_face_box('RHPH | retail shelving cue',edge,j*3.1,zbase+1.6,.32,.38,2.3,metal,detail,.38,.02)
        pharm_gold=make_mat('RHPH | pharmacy gold identity',(.76,.49,.12),.4,.25)
        oriented_face_box('RHPH | public pharmacy sign panel',edge,0,zbase+6.15,9.0,.22,.72,stone,detail,.48,.04)
        text_on_face('RHPH | public pharmacy sign','PURDUE PHARMACY',edge,0,zbase+6.15,.47,pharm_gold,detail,.62)
        add_interior_activity(edge,zbase,(2.2,6.5,10.8,15.1,19.4),mats,detail,key)
        trim_source_glazing_at_parapet(asset,zbase,ztop)
        set_glass_reflections(glass,.14,.26)
        pharmacywarm=make_mat('RHPH | occupied pharmacy interior',(.60,.35,.12),.66)
        for j in range(4):
            box('RHPH | visible pharmacy display %02d'%j,(-5.4+j*3.6,0,zbase+1.45),(2.0,.52,.10),pharmacywarm,detail,0,.02)
        ph=object_by_substr(asset,'Heine Pharmacy rooftop penthouse')
        if ph:
            src=ph.get('repair_source_dimensions')
            if not src: src=[float(v) for v in ph.dimensions]; ph['repair_source_dimensions']=src
            ph.dimensions=(max(8,float(src[0])*.62),max(7,float(src[1])*.62),float(src[2])*.72)
            bpy.context.view_layer.objects.active=ph; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            ph['status']='Compact estimated mechanical penthouse; six visible stories retained.'
        revisions=['Added a narrow vertical glazed circulation bay and pale stone pilaster cadence; model shows five above-grade public levels while the six-floor campus sources appear to include one lower level. The GIS extrusion/roof field remains uncertain.','Reworked the public pharmacy ground-floor entry with a five-bay stone arcade, retail counter/shelf cues, enlarged PURDUE PHARMACY sign, and a compact estimated mechanical penthouse.','Added schematic lab/office activity behind the frontage glazing; it does not assert room layouts.']
    elif key=='ray_w_herrick_laboratories':
        # Research facility palette splits masonry, glazed living-lab frontage and metal high-bay zone.
        glass_bay(asset,edge,min(elen*.44,23),zbase+.2,ztop-.35,glass,stone,'HLAB living-lab glazed office wing',detail,count=10)
        add_textured_pier_rhythm(asset,edge,min(elen*.75,32),zbase+.05,ztop-.1,7,stone,'HLAB alternating brick and metal bays',.30,.31,.2,detail)
        create_entry(asset,edge,zbase,3,h,'Herrick Labs',stone,glass,metal,.82,detail)
        # Small panel-clad high-bay rooftop block and exhaust stacks communicate lab use.
        cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
        box('HLAB | compact metal panel high-bay monitor',(cx+4,cy+7,ztop+1.15),(min(17,elen*.34),10,2.3),metal,detail,.0,.06)
        for j in range(4):
            box('HLAB | roof exhaust stack %d'%j,(cx-7+j*4,cy+6,ztop+2.45),(.72,.72,2.2),stone,detail,0,.05)
        # Distinct lower high-bay service wing and roof process equipment;
        # dimensions/positions remain schematic within the GIS envelope.
        box('HLAB | high-bay lab wing',(cx-13,cy-5,ztop+.2),(24,19,3.6),metal,detail,0,.08)
        edge2=max(facade_edges(ring,15.0),key=lambda e:e[0] if abs(e[3].dot(edge[3]))<.7 else 0)
        panel('HLAB | high-bay glazed loading bay',edge2,-4.8,4.8,zbase+.3,zbase+4.6,glass,detail,.34)
        for j in range(3): box('HLAB | process duct riser %d'%j,(cx-15+j*3,cy-3,ztop+3.1),(.46,.46,3.0),stone,detail,0,.025)
        for j in range(3): box('HLAB | equipment skid %d'%j,(cx-15+j*5,cy-8,ztop+2.45),(2.8,2.6,1.2),stone,detail,0,.04)
        # A street-facing taller window in the high-bay wing exposes schematic
        # test equipment and work surfaces without expanding the GIS envelope.
        hb0=-min(elen*.45,16); hb1=-min(elen*.08,4)
        panel('HLAB | visible high-bay lab glazing',edge,hb0,hb1,zbase+.4,zbase+5.3,glass,detail,.34)
        for j in range(5): oriented_face_box('HLAB | high-bay glazing mullion %02d'%j,edge,hb0+(hb1-hb0)*j/4,zbase+2.85,.10,.13,4.9,metal,detail,.45,.01)
        eq=make_mat('HLAB | test equipment enamel',(.60,.43,.17),.44,.42)
        for j in range(3):
            s=hb0+2+j*3.8
            oriented_face_box('HLAB | visible rig frame %02d'%j,edge,s,zbase+1.55,1.7,.7,2.1,eq,detail,-1.0,.035)
        set_glass_reflections(glass,.16,.24)
        trim_source_glazing_at_parapet(asset,zbase,ztop)
        for ob in asset.all_objects:
            if ob.type!='MESH' or 'continuous horizontal facade banding' not in ob.name.lower(): continue
            inv=ob.matrix_world.inverted()
            for v in ob.data.vertices:
                w=ob.matrix_world@v.co
                if w.z>ztop-.08: v.co=inv@Vector((w.x,w.y,ztop-.08))
            ob.data.update()
        add_interior_activity(edge,zbase,(2.2,6.8),mats,detail,key)
        revisions=['Added a distinct metal high-bay wing, visible test rigs, loading glazing and roof equipment; specific rig layout is schematic.','Kept brick office/lab bays distinct from metal high-bay walls, trimmed generic windows/facade fins to the parapet, and added schematic work surfaces.','Retained the distinct 2013 HLAB source match and GIS outline; did not include the separate historic HERL building.']
    elif key=='brees_student_athletic_academic_center':
        # Low student academic center receives a two-level glass study frontage,
        # gold identification and broad controlled ivy coverage from official photo.
        edge=edge_frame(ring)
        elen,a,b,t,n=edge
        frontages=camera_facing_facades(ring,9.0,.62)
        for fi,fe in enumerate(frontages):
            glass_bay(asset,fe,min(fe[0]*.72,22),zbase+.25,ztop-.3,glass,stone,'BRES front academic commons %02d'%fi,detail,count=max(5,min(10,int(fe[0]/2.7))))
        trim_source_glazing_at_parapet(asset,zbase,ztop)
        create_entry(asset,edge,zbase,2,h,'Brees Academic Center',stone,glass,metal,.88,detail)
        gold=make_mat('BRES | Purdue gold lettering',(.83,.57,.12),.38,.35)
        oriented_face_box('BRES | gold building-name plaque',edge,0,zbase+5.15,23.0,.24,1.35,stone,detail,.48,.045)
        text_on_face('BRES | Drew and Brittany Brees gold identity','DREW & BRITTANY BREES',edge,0,zbase+5.15,1.25,gold,detail,.64)
        # Replace isolated ivy patches with broad, varied planted ribbons limited to
        # the lower portions and facade edges shown in the official image.
        green=make_mat('BRES | ivy leaves',(.055,.18,.07),.88)
        for s in (-min(elen*.28,18),-min(elen*.25,15),min(elen*.28,18),min(elen*.25,15)):
            oriented_face_box('BRES | climbing ivy panel',edge,s,zbase+2.1,3.5,.08,4.0,green,detail,.17,.03)
        # Reduce blank parapet thickness and emphasize a usable study frontage.
        cap=object_by_substr(asset,'BRES flat roof cap')
        if cap and cap.type=='MESH':
            source=cap.get('repair_source_z')
            if not source: source=[float(v.co.z) for v in cap.data.vertices]; cap['repair_source_z']=source
            zbot=min(source); ztopcap=max(source)
            if ztopcap-zbot>.22:
                for v,zorig in zip(cap.data.vertices,source): v.co.z=zbot+(float(zorig)-zbot)*.48
                cap.data.update()
        add_interior_activity(edge,zbase,(1.6,5.2),mats,detail,key)
        set_glass_reflections(glass,.13,.3)
        # Legacy horizontal-band mesh included narrow vertical parapet spurs;
        # trim its uppermost vertices flush to the roof edge.
        for ob in asset.all_objects:
            if ob.type!='MESH' or 'continuous horizontal facade banding' not in ob.name.lower(): continue
            inv=ob.matrix_world.inverted()
            for v in ob.data.vertices:
                w=ob.matrix_world@v.co
                if w.z>ztop-.08: v.co=inv@Vector((w.x,w.y,ztop-.08))
            ob.data.update()
        # A bright study commons floor is visible through the public frontage.
        warm=make_mat('BRES | occupied commons light',(.66,.42,.18),.62)
        set_emission(warm,(.5,.24,.08),.10)
        for j in range(5): oriented_face_box('BRES | commons study table %02d'%j,edge,-8+j*4,zbase+1.25,2.4,.92,.12,warm,detail,-1.0,.02)
        revisions=['Expanded study-commons glazing on the visible front and long elevation; enlarged gold Brees name and placed it with restrained ivy at the academic entry.','Added occupied study-table cues visible through the glazing while retaining the low two-story profile and reduced parapet.','Preserved GIS footprint; exact sign size, ivy extent and study furniture are schematic.']
    elif key=='hall_for_discovery_and_learning_research':
        # Remove the oversized generic screen; replace with a compact screened plant
        # enclosure and a bowed, faceted multi-story glass frontage.
        for ob in list(asset.all_objects):
            if 'DLR rooftop mechanical screen' in ob.name or 'DLR glazed lobby volume' in ob.name: bpy.data.objects.remove(ob,do_unlink=True)
            if ob.name.lower()=='facade glazing | repeated vision panels': bpy.data.objects.remove(ob,do_unlink=True)
        for fi,fe in enumerate(facade_edges(ring,10.0)):
            glass_bay(asset,fe,min(fe[0]*.86,34),zbase+.25,ztop-.3,glass,stone,'DLR bowed atrium frontage %02d'%fi,detail,sagitta=2.0,count=12)
            oriented_face_box('DLR | continuous atrium floor band %02d'%fi,fe,0,zbase+(ztop-zbase)*.28,fe[0]*.78,.18,.22,stone,detail,.34,.015)
            oriented_face_box('DLR | continuous atrium floor band upper %02d'%fi,fe,0,zbase+(ztop-zbase)*.55,fe[0]*.78,.18,.22,stone,detail,.34,.015)
        create_entry(asset,edge,zbase,5,h,'Discovery & Learning',stone,glass,metal,.95,detail)
        add_textured_pier_rhythm(asset,edge,min(elen*.82,48),zbase+.1,ztop-.1,12,stone,'DLR slim curved facade fins',.22,.40,.12,detail)
        cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)
        box('DLR | compact rooftop mechanical screen',(cx+10,cy+6,ztop+.85),(12,8,1.7),metal,detail,0,.08)
        add_interior_activity(edge,zbase,(2.4,6.8,11.2),mats,detail,key)
        set_glass_reflections(glass,.09,.38)
        atriumlight=make_mat('DLR | active ground-floor atrium',(.72,.47,.22),.52)
        for j in range(6):
            sx=(j-2.5)*4
            oriented_face_box('DLR | ground floor public atrium table %02d'%j,edge,sx,zbase+1.05,2.2,.9,.12,atriumlight,detail,-1.2,.03)
            oriented_face_box('DLR | atrium study seat %02d'%j,edge,sx,zbase+.65,.72,.62,.7,stone,detail,-2.1,.06)
        # Three shallow landings/stair flights visible through the bowed atrium
        # frontage. Their exact core location is schematic.
        for j in range(4):
            oriented_face_box('DLR | schematic atrium stair landing %d'%j,edge,(j-1.5)*2.2,zbase+2.0+j*2.2,4.4,.38,.18,stone,detail,.82,.02)
        revisions=['Removed the oversized generic rooftop box and replaced it with a compact mechanical screen.','Increased the visible curtainwall bow and reflective glass finish while carrying floor bands around the GIS ring; exact curvature remains estimated.','Added ground-floor public atrium tables/seats and stair landings behind the glazing while preserving the footprint, stories and origin.']
    elif key=='physics_building':
        add_physics_arch_and_roof(asset,ring,detail,zbase,ztop,mats)
        # Purdue Events/Henneman exterior photos show a glazed skybridge linking
        # the Physics wing to the adjoining campus structure; this estimated
        # appendage extends beyond the mapped PHYS footprint.
        # GIS shell-to-shell closest points in project coordinates, derived from
        # the FID 273 PHYS and MSEE outlines and the existing placement markers.
        # Physics placement is (20.732372,300.324127); MSEE is
        # (87.421000,215.992000), both unrotated in the master.
        phys_endpoint_world=Vector((58.952614,262.990509))
        msee_endpoint_world=Vector((69.674605,249.940914))
        phys_origin=Vector((20.732372,300.324127))
        p_local=phys_endpoint_world-phys_origin
        q_local=msee_endpoint_world-phys_origin
        link=q_local-p_local; gap=link.length; axis=link.normalized()
        center=(p_local+q_local)/2
        bridge_len=gap+3.6; bridge_width=5.0; bridge_height=3.2
        ang=math.atan2(axis.y,axis.x); bridge_z=zbase+8.0
        # Replace the former opaque cube with a legible framed glazed connector.
        # Its 1.8 m overlap at each GIS endpoint makes both wall junctions robust.
        for side in (-1,1):
            offset=Vector((-axis.y,axis.x))*side*(bridge_width/2-.08)
            p=center+offset
            box('PHYS | skybridge transparent side wall %d'%side,(p.x,p.y,bridge_z),(bridge_len-.24,.10,bridge_height-.28),glass,detail,ang,.015)
        for end in (-1,1):
            p=center+axis*(end*(bridge_len/2-.08))
            box('PHYS | skybridge glazed end %d'%end,(p.x,p.y,bridge_z),(.10,bridge_width-.18,bridge_height-.28),glass,detail,ang,.01)
        box('PHYS | skybridge deck',(center.x,center.y,bridge_z-1.78),(bridge_len,bridge_width+.2,.24),stone,detail,ang,.025)
        box('PHYS | skybridge roof frame',(center.x,center.y,bridge_z+1.68),(bridge_len,bridge_width+.12,.16),metal,detail,ang,.025)
        glow=make_mat('PHYS | skybridge warm occupied interior',(.55,.34,.16),.45,.08)
        bs=next(n for n in glow.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(.45,.20,.06,1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=.18
        box('PHYS | skybridge occupied interior sill',(center.x,center.y,bridge_z-.48),(bridge_len-.65,bridge_width-.58,.10),glow,detail,ang,.015)
        for along in range(-int(gap/2),int(gap/2)+1,3):
            p=center+axis*along
            for side in (-1,1):
                offset=Vector((-axis.y,axis.x))*side*(bridge_width/2-.08)
                box('PHYS | skybridge mullion %.1f_%d'%(along,side),(p.x+offset.x,p.y+offset.y,bridge_z),(.12,.12,bridge_height-.25),metal,detail,ang,.012)
        add_interior_activity(edge,zbase,(2.6,6.1,9.6),mats,detail,key)
        # The official front photograph shows a clear central name panel; keep it
        # prominent above the arched door rather than relying on small lettering.
        gold=make_mat('PHYS | bronze entrance lettering',(.76,.52,.22),.45,.25)
        text_on_face('PHYS | prominent central physics name','PHYSICS',edge,0,zbase+4.15,.78,gold,detail,.64)
        revisions=['Compared the same FID 273 one-ring, 34-vertex footprint in two Purdue GIS snapshots and documented the Web Mercator/project-frame area reconciliation.','Rebuilt the central portal, prominent PHYSICS sign, arched upper window and fanlight divisions; relocated/rebuilt the source skybridge to align its ends with the nearest PHYS/MSEE GIS wall points.','Saved the calculated MSEE-aligned source-local/master-coordinate endpoint transform in the evidence report; master placements are unchanged and span/height remain estimated.']
    else: raise KeyError(key)
    # Immediate frontage cues: a short public walk and two restrained planters
    # connect the entry to grade. Their dimensions are schematic and do not
    # claim surveyed site furniture or planting locations.
    walk=make_mat('SITE | Purdue concrete path',(.34,.35,.33),.92)
    planter=make_mat('SITE | dark bronze planter',(.16,.18,.17),.65,.25)
    leaves=make_mat('SITE | low evergreen planting',(.10,.20,.10),.9)
    vestibule=make_mat(key.upper()+' | schematic warm vestibule interior',(.52,.30,.12),.68)
    vbs=next(n for n in vestibule.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    if 'Emission Color' in vbs.inputs:
        vbs.inputs['Emission Color'].default_value=(.52,.22,.055,1)
        vbs.inputs['Emission Strength'].default_value=.22
    # A small warm inner vestibule panel sits behind the glazed entry. It signals
    # occupied public space without asserting any specific room plan or furniture.
    panel(key.upper()+' | schematic vestibule visible through entry',edge,-1.3,1.3,zbase+.55,zbase+2.75,vestibule,detail,.24)
    oriented_face_box(key.upper()+' | schematic entry walk',edge,0,zbase+.07,5.5,6.0,.18,walk,detail,6.7,.025)
    for side in (-1,1):
        oriented_face_box(key.upper()+' | schematic entry planter',edge,side*4.7,zbase+.28,2.0,1.0,.56,planter,detail,5.3,.06)
        oriented_face_box(key.upper()+' | low planter planting',edge,side*4.7,zbase+.68,1.65,.72,.32,leaves,detail,5.3,.08)
    revisions.append('Added a warm schematic vestibule cue behind the glazed entry, plus a short entry walk and paired low planters. Interior room layout, site furniture, and planting placement are interpretive, not survey-derived.')
    asset['placement_origin_xy_m']=original_origin
    asset['revision_date']=RETRIEVED
    add_metadata(asset,revisions)
    if key=='physics_building':
        asset['footprint_area_m2_project_frame']=5158.8513
        asset['shape_area_reconciliation']='GIS Shape__Area is native Web Mercator map-plane area; projected local ground area reconciles after cos(latitude)^2 correction.'
    aim_preview_camera(zbase,ztop)
    if key=='ford_dining_court' and bpy.context.scene.camera:
        # A pedestrian-height camera keeps the long eaves from hiding the
        # dining frontage, without altering the saved architecture.
        cam=bpy.context.scene.camera; target=Vector((0,0,zbase+(ztop-zbase)*.48))
        cam.location.z=ztop+2.5
        cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    # Save, reopen the exact source file, and render that reopened scene. Hashes
    # prove rendering did not mutate the saved library after the check.
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    import hashlib
    saved_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    asset=bpy.data.collections.get(asset_name(key))
    preview=(ROOT/'audit'/'physics_building'/'physics_building_preview.png') if key=='physics_building' else (AUDIT/(key+'_preview.png'))
    save_preview(asset,key,preview)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==saved_hash, 'saved source bytes changed during render'
    reopened=bpy.data.collections.get(asset_name(key))
    assert reopened is not None and len(reopened.all_objects)>0, 'export collection missing after reopen'
    reopened_origin=reopened.get('placement_origin_xy_m',reopened.get('campus_origin_m'))
    assert len(reopened_origin)==len(original_origin) and all(abs(float(a)-float(b))<1e-7 for a,b in zip(reopened_origin,original_origin)), 'campus origin changed'
    # Every mesh in the asset has a material; procedural material nodes are native Blender nodes.
    meshes=[o for o in reopened.all_objects if o.type=='MESH']
    assert meshes and all(len(o.data.materials)>0 for o in meshes), 'unmaterialed source mesh found'
    add_textures=all(any(n.type=='TEX_NOISE' for n in m.node_tree.nodes) for o in meshes for m in o.data.materials if m and m.use_nodes)
    source_research={
      'krach_leadership_center':[{'title':'Purdue News — Krach Leadership Center lobby photo/context','url':'https://www.purdue.edu/newsroom/archive/releases/2019/Q2/purdue-day-of-giving-leaps-to-41.6-million%2C-reaches-six-year-total-of-146.9-million.html','accessed':RETRIEVED,'observation':'Purdue identifies active lobby use; the glazed study bay/interior desks are schematic and the exact furniture layout is not claimed.'}],
      'horticulture_building':[{'title':'Purdue Events — Horticulture Building exterior photo','url':'https://events.purdue.edu/horticulture_building','image_url':'https://localist-images.azureedge.net/photos/40247317614471/card/62557aff04e4ef3407a980bb42b7c3e0f9f7eb90.jpg','accessed':RETRIEVED,'observation':'Current exterior photo shows repeated sash windows, centered light-stone entry, and flat/corniced roof edge; dormers are not visible. The separate Plant Growth Facility/greenhouses are excluded. Exact facade spacing and concealed roof are estimates.'}],
      'ford_dining_court':[{'title':'FRP — Ford Dining Hall project description and exterior images','url':'https://frpinc.com/projects/ford-dining-hall/','accessed':RETRIEVED,'observation':'Confirms a two-story building, partial dining mezzanine, clay-tile shingles and gabled framing. The exterior reference supports restrained eaves; exact roof pitch intersections remain unverified.'},{'title':'Purdue Archives — Fred and Mary Ford Dining Court','url':'https://archives.lib.purdue.edu/agents/corporate_entities/694','accessed':RETRIEVED,'observation':'Purdue describes a two-story dining-court building; interior tables/counter cues are schematic.'},{'title':'Purdue News — Ford exterior photograph','url':'https://www.purdue.edu/uns/images/+2004/foodcourt-ext.jpg','accessed':RETRIEVED,'observation':'Official Purdue News exterior photo used for the red-brick, roof-eave and public frontage comparison; detailed roof intersections and interior layout are estimated.'}],
      'flex_lab':[{'title':'Ennead Architects — Purdue Flex Lab','url':'https://www.ennead.com/work/purdue','accessed':RETRIEVED,'observation':'Reference supports differentiated brick and curtainwall frontage; separated lab windows and bench cues are interpretive.'}],
      'heine_pharmacy':[{'title':'Purdue Events — Robert E. Heine Pharmacy Building','url':'https://events.purdue.edu/robert_e_heine_pharmacy_building','image_url':'https://localist-images.azureedge.net/photos/41093699625075/card/9dae1726a4351597d0ccf124839d26b3becec6f4.jpg','accessed':RETRIEVED,'observation':'Official place page includes an exterior image. Purdue’s building emergency plan describes Floors 1–5 above grade plus Floor G below and a basement; other Purdue publications call it six-story. The facade models five above-grade rows and a public pharmacy ground-floor cue; exact wall height remains GIS/photographic estimate.'},{'title':'Purdue Pharmacy building emergency plan','url':'https://www.pharmacy.purdue.edu/sites/default/files/safety/rhph_building_plan.pdf','accessed':RETRIEVED,'observation':'Confirms offices, classrooms, student/research labs, Pharmacy Stores, a licensed pharmacy, five above-grade floors, lower Floor G, and basement. Ground-floor counter/shelf details are schematic.'},{'title':'Wikimedia Commons — Robert E. Heine Pharmacy Building exterior photograph','url':'https://commons.wikimedia.org/wiki/File:Purdue_University_Robert_E_Heine_Pharmacy_Building.jpg','accessed':RETRIEVED,'observation':'Exterior photo used to study the tall stone entrance arcade; architectural interpretation is approximate.'}],
      'ray_w_herrick_laboratories':[{'title':'Purdue News — Herrick Labs building opens','url':'https://www.purdue.edu/newsroom/archive/releases/2013/Q2/purdues-new-herrick-labs-building-open-for-business.html','accessed':RETRIEVED,'observation':'Supports the distinct 2013 HLAB facility; high-bay wing, duct risers, loading glazing and lab equipment remain schematic. The older Herrick Acoustics building is not included.'}],
      'brees_student_athletic_academic_center':[{'title':'Purdue Student Life — Brees Student Athletic Academic Center image','url':'https://localist-images.azureedge.net/photos/40100423165002/card%402x/165f2d98622def2b85a5a24a280b7b72bbf40b7a.jpg','accessed':RETRIEVED,'observation':'Official image supports low brick massing, ivy, and gold building identity; gold name treatment, study glazing and visible desks are schematic details.'}],
      'hall_for_discovery_and_learning_research':[{'title':'Architizer — Hall for Discovery and Learning Research','url':'https://architizer.com/projects/hall-for-discovery-and-learning-research/','accessed':RETRIEVED,'observation':'Supports bowed glazed frontage and floor-band rhythm; full-perimeter bowed bays/atrium activity are schematic where elevations are not shown.'}],
      'physics_building':[{'title':'Purdue Events — Physics Building exterior image','url':'https://events.purdue.edu/physics_building','image_url':'https://localist-images.azureedge.net/photos/40247397308836/card%402x/7a02b4b0e80baf717abf429dfe44cab0f62dea1a.jpg','accessed':RETRIEVED,'observation':'Shows traditional tiled roof, red brick, entry/upper-window composition, and skybridge. The bridge is an estimated appendage outside the PHYS GIS polygon; its exact span/height is schematic.'},{'title':'Purdue Physics — Campus resources exterior photograph','url':'https://www.physics.purdue.edu/academic-programs/undergraduate/campus_resources.html','accessed':RETRIEVED,'observation':'Supports the arched entry, upper arched window, and central PHYSICS name panel; portal geometry remains interpretive.'},{'title':'Henneman Engineering — Purdue Physics Building HVAC project photo','url':'https://henneman.com/work/purdue-university-physics-building/','accessed':RETRIEVED,'observation':'Exterior image supports a low red-tile roof and glazed connecting skybridge; location and span are approximate.'}]
    }.get(key)
    if key=='horticulture_building':
        data=json.loads((AUDIT/(key+'_evidence.json')).read_text(encoding='utf-8'))
        facts=data.get('architectural_references',{}).get('published_facts','')
        facts=facts.replace('Exterior photo supports red brick, white/classical entrance, and three roof dormers; the historic roof shape and exact facade pattern remain estimates pending elevation drawings.','The Purdue Events exterior photo supports red brick, repeated sash windows, a centered light-stone entrance, and a flat/corniced roof edge; no dormers are visible. Exact facade spacing and concealed roof construction remain estimates pending elevation drawings.')
        data['architectural_references']['published_facts']=facts
        data['modeled_interpretation']['height_evidence']=data['modeled_interpretation']['height_evidence'].replace('Exterior photo supports red brick, white/classical entrance, and three roof dormers; the historic roof shape and exact facade pattern remain estimates pending elevation drawings.','The Purdue Events exterior photo supports red brick, repeated sash windows, a centered light-stone entrance, and a flat/corniced roof edge; no dormers are visible. Exact facade spacing and concealed roof construction remain estimates pending elevation drawings.')
        (AUDIT/(key+'_evidence.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
    update_evidence(key,revisions,source_research,saved_hash)
    print(json.dumps({'key':key,'file':str(path),'collection':reopened.name,'objects':len(reopened.all_objects),'meshes':len(meshes),'origin':[float(x) for x in original_origin],'preview':str(preview),'texture_nodes':add_textures}),flush=True)

requested=set(__import__('sys').argv[__import__('sys').argv.index('--')+1:]) if '--' in __import__('sys').argv else set(TARGETS)
for key in TARGETS:
    if key in requested: refine_one(key)
