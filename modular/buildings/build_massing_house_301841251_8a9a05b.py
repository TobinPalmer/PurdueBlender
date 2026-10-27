"""Build detailed Acacia Purdue chapter house from source-backed geometry.

Run from the project root with Blender in background mode. The asset remains in
campus coordinates because its manifest entry is a direct-linked massing asset.
The original GIS-derived outline is retained; additions beyond its south edge
represent the source-documented front porch and are recorded as estimates.
"""
import bpy, json, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIT = os.path.join(ROOT, 'audit', 'acacia')
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_house_301841251_8a9a05b.blend')
ASSET_ID = 'massing_house_301841251_8a9a05b'
COLLECTION = 'Asset_' + ASSET_ID
SCENE = 'Building_' + ASSET_ID
OBJECT = 'House_301841251'

def material(name, color, roughness=.82, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Metallic'].default_value=metallic
    return m

def noise_finish(m, scale, detail, strength, distance, dark, light):
    nt=m.node_tree; bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale; tex.inputs['Detail'].default_value=detail
    geo=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(geo.outputs['Generated'],tex.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*dark,1); ramp.color_ramp.elements[1].color=(*light,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=strength; bump.inputs['Distance'].default_value=distance
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def cube(name, loc, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat: o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Softened architectural edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def mesh_obj(name, verts, faces, mat):
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(o); return o

def prism(name, outline, z0, z1, mat):
    n=len(outline); verts=[(x,y,z0) for x,y in outline]+[(x,y,z1) for x,y in outline]
    faces=[]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    faces.append(tuple(n+i for i in range(n)))
    return mesh_obj(name,verts,faces,mat)

def gable_roof(name, x0,x1,y0,y1,zbase,zridge,mat):
    # Ridge is north-south; the documented front elevation presents its gable south.
    ym=(y0+y1)/2
    verts=[(x0,y0,zbase),(x0,y1,zbase),(x1,y1,zbase),(x1,y0,zbase),
           ((x0+x1)/2,y0,zridge),((x0+x1)/2,y1,zridge)]
    return mesh_obj(name,verts,[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)],mat)

def roof_box(name,loc,dims,mat,angle=0):
    o=cube(name,loc,dims,mat,.025); o.rotation_euler[1]=angle; return o

def window(front, along, z, width=1.25, height=1.45, yface=None, xface=None, trim=None, glass=None):
    # Front(south/north) window lies on an X-Z plane; side window on a Y-Z plane.
    if yface is not None:
        cube('Window recessed glazing', (along,yface,z+height/2),(width*.79,.08,height*.78),glass)
        cube('Window outer white frame', (along-width/2,yface-.055,z+height/2),(.10,.12,height),trim)
        cube('Window outer white frame', (along+width/2,yface-.055,z+height/2),(.10,.12,height),trim)
        cube('Window sill', (along,yface-.10,z),(width+.18,.22,.11),trim)
        cube('Window head', (along,yface-.055,z+height),(width+.12,.12,.10),trim)
        cube('Window center mullion', (along,yface-.11,z+height/2),(.055,.05,height*.78),trim)
        cube('Window center mullion', (along,yface-.11,z+height/2),(width*.79,.05,.055),trim)
    else:
        cube('Window recessed glazing', (xface,along,z+height/2),(.08,width*.79,height*.78),glass)
        cube('Window white side frame', (xface-.055,along-width/2,z+height/2),(.12,.10,height),trim)
        cube('Window white side frame', (xface-.055,along+width/2,z+height/2),(.12,.10,height),trim)
        cube('Window sill', (xface-.10,along,z),(.22,width+.18,.11),trim)
        cube('Window head', (xface-.055,along,z+height),(.12,width+.12,.10),trim)
        cube('Window center mullion', (xface-.11,along,z+height/2),(.05,.055,height*.78),trim)

def text_obj(body, name, loc, size, mat, rot=(0,0,0), extrude=.012):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=extrude; c.align_x='CENTER'; c.align_y='CENTER'
    o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o

def room_divider(x0,y0,x1,y1,z=0.15,h=2.65,t=.13,mat=None,name='Interior partition'):
    dx=x1-x0; dy=y1-y0; length=math.hypot(dx,dy); a=math.atan2(dy,dx)
    o=cube(name,((x0+x1)/2,(y0+y1)/2,z+h/2),(length,t,h),mat); o.rotation_euler[2]=a; return o

def beam_xz(name, start, end, width, depth, mat):
    a=Vector(start); b=Vector(end); vec=b-a
    o=cube(name,(a+b)/2,(width,depth,vec.length),mat)
    o.rotation_euler[1]=math.atan2(vec.x,vec.z)
    return o

def beam_yz(name, start, end, width, depth, mat):
    a=Vector(start); b=Vector(end); vec=b-a
    o=cube(name,(a+b)/2,(depth,width,vec.length),mat)
    o.rotation_euler[0]=-math.atan2(vec.y,vec.z)
    return o

def front_cross_gable(name, wall_x, center_y, width, base_z, peak_z, projection, panel_mat, roof_mat, timber_mat):
    # Entry gable faces west; the projecting hood aligns its apex above the entry arch.
    outer_x=wall_x-projection
    mesh_obj(name+' cream infill',[(outer_x,center_y-width/2,base_z),(outer_x,center_y+width/2,base_z),(outer_x,center_y,peak_z)],[(0,1,2)],panel_mat)
    beam_yz(name+' left rake',(outer_x,center_y-width/2,base_z),(outer_x,center_y,peak_z),.22,.18,timber_mat)
    beam_yz(name+' right rake',(outer_x,center_y,peak_z),(outer_x,center_y+width/2,base_z),.22,.18,timber_mat)
    cube(name+' center king post',(outer_x-.08,center_y,(base_z+peak_z)/2),(.16,.16,peak_z-base_z),timber_mat)
    cube(name+' cross rail',(outer_x-.08,center_y,(base_z+peak_z)/2),( .16,width*.78,.16),timber_mat)
    for x in (outer_x,wall_x+.18):
        # Two roof planes run from the gable face toward/over the entry wall.
        verts=[(x,center_y-width/2,base_z),(x,center_y,peak_z),(x+projection+.18,center_y,peak_z),(x+projection+.18,center_y-width/2,base_z)]
        mesh_obj(name+' left shingle plane',verts,[(0,1,2,3)],roof_mat)
        verts=[(x,center_y,peak_z),(x,center_y+width/2,base_z),(x+projection+.18,center_y+width/2,base_z),(x+projection+.18,center_y,peak_z)]
        mesh_obj(name+' right shingle plane',verts,[(0,1,2,3)],roof_mat)
    cube(name+' ridge cap',(wall_x-projection/2,center_y,peak_z+.06),(projection+.35,.26,.20),timber_mat)

def move_to_collection(o, collection):
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)

def main():
    if not os.path.exists(ASSET): raise FileNotFoundError(ASSET)
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    src=bpy.data.objects.get(OBJECT)
    if not src or src.type!='MESH': raise RuntimeError('Expected original GIS massing mesh missing')
    # Preserve source footprint vertices and exact global placement before rebuilding.
    outline=[tuple(src.data.vertices[i].co)[:2] for i in range(min(10,len(src.data.vertices)))]
    outline=[(x,y) for x,y in outline]
    xs=[p[0] for p in outline]; ys=[p[1] for p in outline]
    xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
    # Clean the single-building file, then rebuild its stable collection/object identity.
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob,do_unlink=True)
    for sc in list(bpy.data.scenes):
        if sc.name!=SCENE: bpy.data.scenes.remove(sc)
    scene=bpy.context.scene; scene.name=SCENE; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
    for col in list(bpy.data.collections):
        if col.name!='Collection': bpy.data.collections.remove(col)
    asset_col=bpy.data.collections.get(COLLECTION) or bpy.data.collections.new(COLLECTION)
    if asset_col.name not in scene.collection.children: scene.collection.children.link(asset_col)

    brick=material('Acacia weathered red-brown brick',(.24,.075,.045)); noise_finish(brick,34,2,.16,.012,(.075,.025,.015),(.30,.11,.065))
    timber=material('Acacia charcoal half-timber',(.075,.078,.08),.68)
    stucco=material('Acacia pale cream infill panels',(.76,.72,.62),.88)
    roof=material('Acacia charcoal brown shingle roof',(.055,.05,.045),.96)
    trim=material('Acacia ivory painted wood',(.84,.81,.72),.55)
    glass=material('Acacia blue gray window glass',(.12,.23,.29),.25,.2)
    wood=material('Acacia oak interior doors and furniture',(.29,.17,.09),.58)
    floor=material('Acacia warm interior oak floor',(.15,.075,.03),.86); noise_finish(floor,18,2,.05,.004,(.07,.025,.008),(.25,.13,.05))
    concrete=material('Acacia porch and foundation stone',(.48,.45,.39),.92)
    gold=material('Acacia illuminated sign letters',(.96,.53,.13),.3,.15)
    gold_bs=next(n for n in gold.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    gold_bs.inputs['Emission Color'].default_value=(1.0,.43,.07,1)
    gold_bs.inputs['Emission Strength'].default_value=1.8
    lamp=material('Warm entry lantern glass',(1,.60,.22),.24,0)
    pbricks=material('Acacia brick mortar',(.23,.20,.17))
    interior_wall=material('Acacia interior painted plaster',(.46,.40,.31),.95)
    bedlinen=material('Acacia muted sage bed linen',(.22,.32,.27),.92)

    # Primary 3-storey brick residential shell, following the retained GIS ring.
    shell=prism(OBJECT,outline,0.0,9.45,brick)
    # Main modeled mass has three levels: source elevations show FF 100'-0", 110'-7", 119'-10".
    # Model z heights are approximate; source drawing level differences inform spacing.
    floors=[0,3.23,6.43,9.45]
    # The official front is the west-facing long elevation: north is left when viewed from Waldron.
    # Aerial imagery shows the long N-S roof mass and a pedestrian approach to its west edge.
    main_x0=xmin+4.85; main_x1=xmax-.25; front_x=main_x0-.015
    facade_y0=ymin+1.0; facade_y1=ymax-.9; facade_center=(facade_y0+facade_y1)/2
    # Apply cream infill to the upper two wall bands; leave the ground floor brick as in the photo.
    for z0,z1 in ((3.25,6.35),(6.45,9.40)):
        cube('Cream half-timber facade field',(front_x-.20,facade_center,(z0+z1)/2),(.16,facade_y1-facade_y0,z1-z0),stucco)
    for z in (3.22,6.42,9.42):
        cube('Front dark story timber',(front_x-.30,facade_center,z),(.16,facade_y1-facade_y0,.15),timber)
    # Tudor framing: upright posts, diagonal braces, and compact panels around sash windows.
    facade_posts=[facade_y0+i*(facade_y1-facade_y0)/7 for i in range(8)]
    for yy in facade_posts:
        cube('Dark half-timber upright',(front_x-.30,yy,6.35),(.16,.17,6.0),timber)
    for yy in (facade_y0+2.1,facade_y0+6.5,facade_y0+10.9,facade_y0+15.3,facade_y0+19.7):
        if yy<facade_y1-1:
            beam_yz('Tudor diagonal brace',(front_x-.31,yy,6.5),(front_x-.31,yy+1.4,7.9),.12,.12,timber)
    # The west GIS step between y≈354 and 361 m is a forward wing; continue the Tudor infill on it.
    step_front_x=xmin+2.85; step_y0=ymin+11.8; step_y1=ymin+18.5
    for z0,z1 in ((3.25,6.35),(6.45,9.40)):
        cube('Cream half-timber infill west step',(step_front_x-.20,(step_y0+step_y1)/2,(z0+z1)/2),(.16,step_y1-step_y0,z1-z0),stucco)
    for yy in (step_y0+.15,step_y1-.15):
        cube('Dark half-timber west step upright',(step_front_x-.30,yy,6.35),(.16,.16,6.0),timber)
    # Main roof remains a steep N-S ridge; three dormers sit on its west slope facing the chapter approach.
    roof_start=main_x0+.10; roof_end=main_x1-.10; ridge=(roof_start+roof_end)/2
    gable_roof('Main steep dark shingle gable',roof_start,roof_end,ymin+.4,ymax-.5,9.55,14.25,roof)
    cube('North eave fascia',(main_x0-.05,ymax-.45,9.55),(.18,ymax-ymin-1.0,.22),timber)
    cube('Main roof ridge cap',(ridge,facade_center,14.28),(.35,facade_y1-facade_y0,.20),timber)
    for yy in (facade_y0+5.0,facade_center,facade_y1-5.0):
        xfront=roof_start+1.5
        cube('West roof dormer front',(xfront,yy,11.45),(1.55,1.35,1.75),stucco)
        cube('West roof dormer gabled cap',(xfront,yy,12.45),(1.85,1.55,.20),roof)
        cube('West roof dormer window',(xfront-.82,yy,11.63),(.12,.86,1.0),glass)
        cube('West roof dormer window frame',(xfront-.89,yy,11.63),(.10,1.02,1.14),trim)
    # Northwest brick stair tower is the tall left-hand feature in the west-facing photograph.
    tower_x=xmin+.85; tower_y=ymax-3.0
    cube('Northwest brick tower',(tower_x,tower_y,6.65),(4.2,6.0,13.3),brick,.04)
    cube('Tower parapet cap',(tower_x,tower_y,13.4),(4.55,6.25,.38),timber)
    cube('Tower upper coping',(tower_x,tower_y,13.63),(4.65,6.35,.11),trim)
    # Sash windows follow the photographed rhythmic vertical bays; portal center remains open at ground floor.
    facade_windows=[facade_y0+2.0,facade_y0+6.1,facade_y0+10.2,facade_y0+14.3,facade_y0+18.4,facade_y1-1.8]
    for z in (1.05,4.25,7.35):
        for yy in facade_windows:
            if z>2.0 or abs(yy-facade_center)>2.3:
                window('west front',yy,z,1.30,1.48,xface=front_x-.34,trim=trim,glass=glass)
    # Restored west-side porch/atrium: broad deck and white frame aligned with the pedestrian approach.
    porch_top=.62; porch_x=front_x-2.75; porch_length=facade_y1-facade_y0-1.0
    entry_y=facade_center; entry_x=front_x-.12
    cube('Raised west front porch patio',(front_x-1.45,facade_center,porch_top/2),(2.9,porch_length,porch_top),concrete,.05)
    cube('West porch front retaining course',(front_x-2.85,facade_center,porch_top/2),(.20,porch_length,porch_top),brick)
    for yy in (entry_y-4.0,entry_y-1.4,entry_y+1.4,entry_y+4.0):
        cube('White porch column',(porch_x,yy,2.45),(.30,.30,4.2),trim,.035)
        cube('Porch column plinth',(porch_x,yy,.82),(.48,.48,.24),concrete,.03)
    cube('West porch broad white entablature',(porch_x,entry_y,4.55),(.42,8.8,.62),trim,.06)
    # The front gable now sits directly over the illuminated arch and double entry.
    front_cross_gable('West entry gable',front_x,entry_y,6.4,4.95,9.25,2.6,stucco,roof,timber)
    curve=bpy.data.curves.new('ACACIA arch backing','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.13; curve.bevel_resolution=3
    sp=curve.splines.new('POLY'); pts=[]
    for i in range(25):
        theta=math.pi-i*math.pi/24
        pts.append((front_x-2.82,entry_y+math.cos(theta)*2.55,3.95+math.sin(theta)*1.20,1))
    sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=co
    curve_obj=bpy.data.objects.new('Illuminated west entry arch surround',curve); bpy.context.scene.collection.objects.link(curve_obj); curve_obj.data.materials.append(gold)
    text_obj('ACACIA','ACACIA letters over west entry arch',(front_x-3.06,entry_y,4.58),.58,gold,(math.pi/2,0,-math.pi/2),.025)
    # Centered entry, sidelights, traditional surround, and westward steps.
    cube('Entry oak double doors',(entry_x-.30,entry_y,1.55),(.18,1.9,2.65),wood,.04)
    for dy in (-.46,.46): cube('Entry door inset panel',(entry_x-.405,entry_y+dy,1.75),(.035,.68,1.65),trim,.025)
    cube('Entry glazing transom',(entry_x-.34,entry_y,3.15),(.15,1.9,.42),glass)
    for yy in (entry_y-1.45,entry_y+1.45):
        cube('Entry sidelight',(entry_x-.30,yy,1.75),(.14,.48,2.25),glass)
        cube('Entry lantern light',(front_x-.38,yy,3.65),(.12,.22,.43),lamp,.04)
    for i in range(6): cube('Wide west entrance step',(front_x-.52-i*.31,entry_y,.20+i*.11),(.55,3.3+i*.30,.20),concrete,.025)
    # Tower lettering is mounted on its west face, with the chapter letters stacked vertically.
    text_obj('A\nC\nA\nC\nI\nA','Tower vertical chapter lettering',(xmin-1.32,tower_y,9.65),.48,trim,(math.pi/2,0,-math.pi/2),.012)
    # East elevation and north/south gable ends keep a reduced but intentional sash rhythm.
    for yy in [ymin+4.0,ymin+8.2,ymin+12.4,ymin+16.6,ymin+20.8,ymax-3.5]:
        for z in (1.05,4.20,7.35): window('east side',yy,z,1.15,1.35,xface=xmax-.035,trim=trim,glass=glass)
    for xx in [main_x0+1.6,main_x0+4.7,main_x0+7.8,main_x0+10.9,main_x1-1.4]:
        for z in (1.05,4.20,7.35): window('north side',xx,z,1.15,1.35,yface=ymax-.035,trim=trim,glass=glass)
    # Chimneys and parapets grounded in drawings and current facade imagery.
    for x,yy in ((xmax-2.0,ymax-6.0),(xmin+6.0,ymax-9.0)):
        cube('Brick chimney stack',(x,yy,13.0),(.9,.9,3.4),brick,.035)
        cube('Chimney cap',(x,yy,14.75),(1.05,1.05,.22),pbricks,.02)

    # Interior: representative three-level rooms based on published floorplans.
    # Structural wall positions and room proportions remain estimated; plan uses room names, not surveyed dimensions.
    # Ground-floor oak floors and walls are intentionally exposed for a reviewable cutaway.
    for level,z in enumerate((.12,3.25,6.45,9.52)):
        slab=prism('Interior floor '+str(level+1),outline,z,z+.14,floor)
    # Ground floor plan is rotated relative to the source drawing; the GIS form has a 28 m north-south axis.
    # Keep all representative rooms within the source main rectangle (the west stair wing is narrow).
    midx=(xmin+xmax)/2
    room_divider(main_x0+3.35,ymin+2.4,main_x0+3.35,ymax-2.4,z=.22,h=2.7,mat=interior_wall,name='Bedroom wing corridor wall')
    room_divider(main_x1-3.7,ymin+2.4,main_x1-3.7,ymax-2.4,z=.22,h=2.7,mat=interior_wall,name='Study hall boundary')
    for yy in (ymin+8.0,ymin+13.0,ymin+18.0,ymin+23.0):
        room_divider(main_x0+.2,yy,main_x0+3.3,yy,z=.22,h=2.7,mat=interior_wall,name='Bedroom partition')
    room_divider(main_x0+3.5,ymin+10,main_x1-3.8,ymin+10,z=.22,h=2.7,mat=interior_wall,name='Library south divider')
    room_divider(main_x0+3.5,ymin+20,main_x1-3.8,ymin+20,z=.22,h=2.7,mat=interior_wall,name='Study hall south divider')
    # Lobby/atrium/reception and library fittings.
    cube('Heritage room central table',(midx,ymin+17,.74),(1.8,4.3,.12),wood,.04)
    for x in (midx-1.15,midx,midx+1.15):
        for yy in (ymin+14.8,ymin+16.3,ymin+17.8,ymin+19.3): cube('Heritage table chair',(x,yy,.57),(.44,.44,.8),wood,.05)
    cube('Library bookshelves',(main_x0+4.4,ymin+15,1.45),(4.2,.3,2.2),wood,.03)
    for yy in (ymin+13.0,ymin+16.0,ymin+19.0):
        cube('Study hall table',(main_x1-1.7,yy,.82),(3.1,1.15,.12),wood,.04)
        for x in (main_x1-3.5,main_x1+.0): cube('Study hall chair',(x,yy,.54),(.43,.43,.68),wood,.04)
    # Sample bedrooms and furniture; repeated details express function, not resident-specific furnishing.
    for yy in (ymin+5.4,ymin+10.0,ymin+14.6,ymin+19.2,ymin+23.8):
        cube('Single bed',(main_x0+1.6,yy,.53),(1.1,2.05,.38),wood,.06)
        cube('Sage bed cover',(main_x0+1.6,yy+.12,.76),(.98,1.55,.12),bedlinen,.05)
        cube('Bedroom pillow',(main_x0+1.6,yy-.74,.78),(.78,.42,.11),stucco,.05)
        cube('Bedroom desk',(main_x0+2.65,yy+1.15,.76),(.55,1.1,.08),wood,.03)
    # Second and third-floor corridors, bedroom privacy walls, beds, bathrooms as inferred from plans.
    for z,h in ((3.39,2.65),(6.59,2.55)):
        room_divider(main_x0+3.0,ymin+3.0,main_x1-2.0,ymin+3.0,z=z,h=h,mat=interior_wall,name='Residential floor corridor partition')
        for yy in [ymin+9.0,ymin+15.0,ymin+21.0]:
            room_divider(main_x0+3.2,yy,main_x1-3.4,yy,z=z,h=h,mat=interior_wall,name='Upper-floor bedroom partition')
            cube('Upper-floor student bed',(main_x1-1.7,yy-2.0,z+.35),(1.0,1.9,.45),trim,.05)
        for yy in [ymin+7.0,ymin+13.0,ymin+19.0,ymin+25.0]:
            cube('Upper-floor study desk',(main_x0+4.3,yy,z+.75),(1.35,.55,.08),wood,.03)
    # Stair flights: indicative compact oak treads in the two stair towers from plans.
    for floor_i,z in enumerate((.2,3.4,6.6)):
        for i in range(10):
            cube('Interior stair tread',(xmin+1.8+i*.18,ymax-4.0,z+i*.22+.12),(.72,2.3,.12),wood,.015)
    # Distinct interior labels aid cutaway review but remain unobtrusive.
    text_obj('LOBBY / ATRIUM','Interior wayfinding - lobby',(midx-1,ymin+4.4,.31),.68,wood)
    text_obj('HERITAGE ROOM','Interior wayfinding - heritage',(midx,ymin+23,.31),.64,wood)
    text_obj('STUDY HALL','Interior wayfinding - study hall',(xmax-4,ymin+23,.31),.64,wood)

    # Consolidate all generated geometry into stable asset collection while retaining object names.
    for o in list(scene.objects):
        move_to_collection(o,asset_col)
    # Tag stable identity and provenance on primary shell and collection.
    shell['stable_asset_id']=ASSET_ID; shell['source_fid']=791; shell['source_name']='Acacia'
    shell['coordinate_frame']='Purdue local campus coordinates; meters; x east, y north'
    asset_col['stable_asset_id']=ASSET_ID
    scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.world.color=(.08,.10,.14)
    scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-1.45
    scene.view_settings.view_transform='AgX'
    # Non-asset preview ground, lighting, and camera are deliberately outside the exported asset collection.
    groundmat=material('Preview lawn',(.20,.25,.15),.95)
    ground=cube('Preview ground',(midx,(ymin+ymax)/2,-.35),(45,48,.5),groundmat)
    ground['preview_only']=True
    area=bpy.data.lights.new('Soft exterior key','AREA'); light=bpy.data.objects.new('Soft exterior key',area); scene.collection.objects.link(light)
    light.location=(front_x-20,(ymin+ymax)/2,28); area.energy=700; area.shape='DISK'; area.size=20
    sun_data=bpy.data.lights.new('Warm architectural sun','SUN'); sun=bpy.data.objects.new('Warm architectural sun',sun_data); scene.collection.objects.link(sun)
    sun.location=(front_x-22,(ymin+ymax)/2-8,30); sun.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-28)); sun_data.energy=.4
    camdata=bpy.data.cameras.new('Acacia exterior camera'); cam=bpy.data.objects.new('Acacia exterior camera',camdata); scene.collection.objects.link(cam)
    cam.location=(front_x-34,(ymin+ymax)/2-1,10.5); target=Vector((front_x,(ymin+ymax)/2,6.6)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); camdata.lens=32; scene.camera=cam
    scene.render.filepath=os.path.join(AUDIT,'exterior.png')
    os.makedirs(AUDIT,exist_ok=True)
    # Save final asset with deterministic relative path and pack no external images (all materials procedural).
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)
    bpy.ops.render.render(write_still=True)

    # A separate overhead cutaway render exposes the representative first-floor interior.
    # It is audit evidence only; visibility is restored before leaving the saved asset.
    area_data=bpy.data.lights.new('Interior cutaway softbox','AREA'); area_obj=bpy.data.objects.new('Interior cutaway softbox',area_data); scene.collection.objects.link(area_obj)
    area_obj.location=(midx,(ymin+ymax)/2,16); area_data.energy=130; area_data.shape='DISK'; area_data.size=12
    interior_cam_data=bpy.data.cameras.new('Acacia interior plan camera'); interior_cam=bpy.data.objects.new('Acacia interior plan camera',interior_cam_data); scene.collection.objects.link(interior_cam)
    interior_cam.location=(midx,(ymin+ymax)/2,30); interior_cam.rotation_euler=(0,0,0); interior_cam_data.type='ORTHO'; interior_cam_data.ortho_scale=35
    scene.camera=interior_cam; scene.render.resolution_x=1050; scene.render.resolution_y=1400
    keep_prefixes=('Interior floor 1','Bedroom','Single bed','Heritage room','Library','Study hall','LOBBY','STUDY HALL','Interior wayfinding')
    hidden=[]
    for o in scene.objects:
        if o in (interior_cam,area_obj): continue
        keep=o.name.startswith(keep_prefixes)
        if not keep:
            hidden.append((o,o.hide_render)); o.hide_render=True
    scene.render.filepath=os.path.join(AUDIT,'interior.png'); bpy.ops.render.render(write_still=True)
    for o,was_hidden in hidden: o.hide_render=was_hidden
    scene.camera=cam; scene.render.resolution_x=1200; scene.render.resolution_y=850
    bpy.data.objects.remove(interior_cam,do_unlink=True); bpy.data.cameras.remove(interior_cam_data)
    bpy.data.objects.remove(area_obj,do_unlink=True); bpy.data.lights.remove(area_data)
    # Restore saved state after the preview-only render pass.
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)

    # Store source/evidence summary and measurements; conflicting source footprints remain explicit.
    evidence={
      'building':'Acacia, Purdue Chapter House','stable_asset_id':ASSET_ID,'source_fid':791,
      'asset_path':'modular/buildings/massing_house_301841251_8a9a05b.blend','collection':COLLECTION,
      'scene':SCENE,'date_retrieved':'2026-10-26','coordinate_frame':'project local approximate campus coordinates, meters; geographic origin 40.4274N, 86.9137W; x east, y north; retained original massing footprint coordinates',
      'sources':[
       {'provider':'Purdue BuildingShapes GIS FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D791&outFields=%2A&returnGeometry=true&outSR=4326&f=pjson','feature_id':'FID 791','snapshot':'audit/acacia/sources/purdue_gis_fid791_2026-10-26_wgs84.json','crs':'WGS84 EPSG:4326','method':'converted by documented project local approximation; used extant original massing mesh as plan outline','uncertainty':'GIS Shape__Area=798.445 m2 conflicts with area computed from projected polygon (~461.88 m2); original massing footprint vertices retained; GIS NUM_LEVELS=1 is inconsistent with published plans'},
       {'provider':'Acacia Fraternity, Purdue chapter','url':'https://purdueacacia.org/renew-acacia','snapshot':'audit/acacia/sources/acacia_purdue_renew_2026-10-26.html','source_date':'renovation updates through 2026','method':'current porch/atrium restoration and renovations; front photograph saved locally','uncertainty':'photograph is a point-in-time image and can show construction activity'},
       {'provider':'Acacia Fraternity, Purdue chapter','url':'https://purdueacacia.org/','snapshot':'audit/acacia/sources/acacia_front_porch.jpg','method':'front facade visual reference: brick tower, half-timbered upper gable, shingle roof, dormer, porch and illuminated name arch','uncertainty':'photograph provides no exact dimensions or compass bearing'},
       {'provider':'Acacia Fraternity, Purdue chapter','url':'https://purdueacacia.org/renew-acacia','snapshot':'audit/acacia/sources/acacia_plan_gallery_1.jpeg through acacia_plan_gallery_5.jpeg','method':'architectural elevations and floorplans; first/second/third-floor levels noted; room arrangement guides representative interior','uncertainty':'design drawings document plans and may not fully reflect latest renovation; architectural dimensions were not legible/available'},
       {'provider':'Acacia Fraternity, Purdue chapter','url':'https://purdueacacia.org/contact','snapshot':'audit/acacia/sources/acacia_purdue_contact_2026-10-26.html','method':'confirms Acacia House at 608 Waldron Street','uncertainty':'address confirms identity, not footprint/height'},
       {'provider':'Purdue University Archives and Special Collections','url':'https://archives.lib.purdue.edu/agents/corporate_entities/578','method':'historical identity: current 608 Waldron house was Oliver Perkins Terry House and transferred to Acacia in 1959','uncertainty':'history does not establish current architectural dimensions'},
       {'provider':'Esri World Imagery','url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=pjson','snapshot':'audit/acacia/sources/esri_world_imagery_acacia_z20_mosaic.jpg and metadata JSON','method':'north-up z20 imagery checked against the GIS ring and official porch/elevation drawings to infer west-facing long facade','uncertainty':'aerial verifies footprint/context but not facade details; image acquisition date undisclosed and facade photo is not geotagged'}],
      'modeling_decisions':{'floors':'three above-grade floors; level spacings estimated from official drawing callouts 100 ft, 110 ft 7 in, and 119 ft 10 in','roof':'steep gabled dark shingle roof and dormers modeled from official front image and elevations; geometry estimated','exterior':'red-brown brick base, cream panel and dark timber upper facade, white porch framing, illuminated ACACIA arch with a centered timber entry gable directly above, tower and chimney based on official imagery/drawings','interior':'representative lobby/atrium, library, heritage room, study hall, bedrooms, upper corridor, stairs, beds, tables and shelves based on the official plans; room dimensions, materials, furniture and exact wall positions are estimates','porch':'west-facing long elevation inferred by matching official porch/elevation plan with the north-up aerial and west-side approach path; GIS ring extends about 3.15 m south of the retained wall shell, consistent with an entry/porch projection; porch dimensions estimated'},
      'validation':{'fresh_open':'pending; run audit/acacia/fresh_open_validate.py in a separate Blender process after saving','renders':['audit/acacia/exterior.png','audit/acacia/interior.png'],'gis_overlay':'audit/acacia/gis_topdown_overlay.png','aerial_overlay':'audit/acacia/aerial_gis_orientation_overlay.png','gis_comparison':'audit/acacia/gis_comparison.json','stable_identity':'manifest ID/path/collection/scene and House_301841251 object retained','limitations':['official facade photo is not geotagged; west-facing bearing is inferred by matching the official elevation/photo features to north-up imagery and approach path','floorplan drawings may be a project/renovation issue rather than the as-built interior; roof/interior dimensions are estimates','encoded WGS84 and state-plane GIS rings agree within 0.226 m2 (0.049%); shell residual is -2.812 m2 (-0.609%) and the GIS ring extends 3.148 m farther south; shell placement is unchanged','ArcGIS Shape__Area and Shape__Length summary attributes conflict with encoded polygon geometries and are treated as stale']}
    }
    with open(os.path.join(AUDIT,'evidence.json'),'w',encoding='utf8') as f: json.dump(evidence,f,indent=2)
    print(json.dumps({'asset':ASSET,'collection':COLLECTION,'objects':len(asset_col.objects),'footprint_vertices':len(outline),'bounds':[[xmin,xmax],[ymin,ymax],[0,14.9]],'preview':os.path.join(AUDIT,'exterior.png')}))

if __name__=='__main__': main()
