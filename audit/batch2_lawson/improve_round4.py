import bpy, math, os, json
from mathutils import Vector, Matrix
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
OUT=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lawson_hall'];root=bpy.data.objects['AssetRoot_lawson_hall']
for o in list(asset.objects):
    if o and o.name.startswith('LWSN_R4_'): bpy.data.objects.remove(o,do_unlink=True)

def material(name,color,rough=.5,metal=0,emission=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    if emission and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    return m

def local_cube(name,center,dims,mat,props=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    ob=bpy.context.object;ob.name='LWSN_R4_'+name;ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4)
    if mat:ob.data.materials.append(mat)
    if props:
        for k,v in props.items():ob[k]=v
    return ob

# Label inherited roof and stairs as schematic; do not invent a height adjustment.
for o in asset.objects:
    if not o: continue
    if (any(k in o.name.lower() for k in ('roof','penthouse','mechanical','overrun','parapet')) or
        o.name in {'LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Window_Glazing','LWSN_Window_Frames','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels','LWSN_Rotunda_Mullions'}):
        o['evidence_status']='Schematic / unverified height and current rooftop configuration'
        o['evidence_note']='No measured elevation or current rooftop survey was found in the cited Lawson sources. The building shell/roof height and equipment are inherited schematic massing, not verified heights. Preserve only as a visual cue.'
    if o.name.startswith('LWSN_Stair_Flight') or o.name.startswith('LWSN_R3_Stair_Landing'):
        o['evidence_status']='Plan-located schematic stair element; vertical continuity not verified'
        o['evidence_note']='First-floor plan supports stair location only. Do not infer a continuous upper-floor route from these disconnected flights/landings.'

# The existing Harris screen is documented as a 16 x 9 ft tiled wall. Keep its
# source location; resize the visible backing to the published overall size.
wall=bpy.data.objects.get('LWSN_1130_Harris_Video_Wall')
if wall:
    wall.dimensions=(wall.dimensions.x,4.8768,2.7432)
    bpy.context.view_layer.objects.active=wall;wall.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.select_set(False)
    wall['source']='Purdue CS, Harris Video Wall Installed in Lawson Commons (2011)'
    wall['source_url']='https://www.cs.purdue.edu/news/articles/2011/harris-video-wall.html'
    wall['evidence_note']='Purdue reports a 16 x 9 ft wall with sixteen 46-inch LCD monitors in a 4 x 4 grid. This models that documented 2011 configuration; current configuration is unverified.'
    # dark equipment backing and physically distinct narrow-bezel screen modules
    bezel=material('LWSN_R4_VideoWall_Bezel',(.012,.018,.022),.29,.5)
    screens=[material('LWSN_R4_VideoWall_Pixel_'+str(i),c,.23,.15,.22) for i,c in enumerate([
        (.025,.075,.12),(.035,.09,.14),(.02,.05,.09),(.045,.105,.15),
        (.04,.12,.16),(.03,.07,.12),(.06,.14,.17),(.025,.08,.13),
        (.035,.09,.13),(.04,.11,.15),(.025,.06,.1),(.05,.13,.17),
        (.02,.055,.1),(.035,.085,.12),(.045,.105,.15),(.025,.07,.11)])]
    # screens face +X. Grid dimensions follow the documented 4x4 arrangement of 46 in displays.
    cy=float(wall.matrix_world.translation.y);cz=float(wall.matrix_world.translation.z);cx=float(wall.matrix_world.translation.x)
    pw=1.018;ph=.5715;gap=.018;gridw=4*pw+3*gap;gridh=4*ph+3*gap
    for row in range(4):
        for col in range(4):
            yy=cy-gridw/2+pw/2+col*(pw+gap)
            zz=cz+gridh/2-ph/2-row*(ph+gap)
            idx=row*4+col
            frame=local_cube(f'VideoWall_46in_Frame_{row+1}_{col+1}',(cx+.068,yy,zz),(.045,pw,ph),bezel,{'evidence_status':'Documented 2011 46-inch display module; arrangement illustrative'})
            panel=local_cube(f'VideoWall_LCD_{row+1}_{col+1}',(cx+.095,yy,zz),(.008,pw-.028,ph-.028),screens[idx],{'evidence_status':'Screen face is a neutral illustrative graphic, not recovered wall content'})

# Echo Spiral: confirmed by Purdue CS as an 800 lb brushed/textured stainless
# spiral installed in the lobby directly in front of the main entrance in 2006.
steel=material('LWSN_R4_EchoSpiral_Brushed_Stainless',(.47,.52,.55),.27,.88)
stone=material('LWSN_R4_EchoSpiral_Base_Stone',(.42,.43,.42),.62,.05)
wood=material('LWSN_R4_Kurz_DisplayCase_Wood',(.20,.13,.075),.48,.05)
glass=material('LWSN_R4_Kurz_DisplayCase_Glass',(.18,.25,.28),.25,.22)
bronze=material('LWSN_R4_Kurz_Kiosk_Metal',(.12,.16,.18),.31,.62)
center=(.9,-40.55)
base=local_cube('Echo_Spiral_Base',(*center,.12),(.78,.78,.24),stone,{'evidence_status':'Approximate placement; sculpture base dimensions not published'})
# Parametric helical tube represents the reported spiral silhouette only. Exact
# sculptural profile/shape is not inferred from text alone.
verts=[];faces=[];steps=144;cross=10;r=.37;turns=1.55;z0=.22;height=2.965;minor=.055
for i in range(steps+1):
    u=i/steps;theta=2*math.pi*turns*u
    radial=Vector((math.cos(theta),math.sin(theta),0));tangent=Vector((-math.sin(theta),math.cos(theta),height/(2*math.pi*turns*r))).normalized();normal2=tangent.cross(radial).normalized()
    c=Vector((center[0]+r*math.cos(theta),center[1]+r*math.sin(theta),z0+height*u))
    for j in range(cross):
        a=2*math.pi*j/cross
        p=c+minor*(math.cos(a)*radial+math.sin(a)*normal2);verts.append(tuple(p))
for i in range(steps):
    for j in range(cross):
        a=i*cross+j;b=i*cross+(j+1)%cross;c=(i+1)*cross+(j+1)%cross;d=(i+1)*cross+j;faces.append((a,b,c,d))
me=bpy.data.meshes.new('Echo Spiral schematic helical tube');me.from_pydata(verts,[],faces);me.materials.append(steel);me.update()
spiral=bpy.data.objects.new('LWSN_R4_Echo_Spiral_Schematic',me);asset.objects.link(spiral);spiral.parent=root;spiral.matrix_parent_inverse=Matrix.Identity(4)
spiral['source']='Purdue CS Echo Spiral article, 2006; sculpture made by John Mishler, stainless steel, brushed/textured, installed inside lobby directly in front of main entrance.'
spiral['source_url']='https://www.cs.purdue.edu/news/articles/2006/echo-spiral.html'
spiral['evidence_status']='Schematic silhouette; modeled overall height 3.048 m follows source-reported 10 ft. Exact sculptural profile is not reconstructed.'
spiral['vertical_route_claim']='None; decorative sculpture only.'
# Lobby display case and wayfinding touch-screen kiosks, documented in official
# 2006 Purdue description; locations and all sizes are explicitly illustrative.
case_x,case_y=-2.7,-39.25
local_cube('Kurz_DisplayCase_Base',(case_x,case_y,.19),(1.45,.48,.38),wood,{'evidence_status':'Purdue reports a display case in the Kurz Lobby; location/dimensions illustrative'})
local_cube('Kurz_DisplayCase_Top',(case_x,case_y,1.42),(1.50,.53,.08),wood,{'evidence_status':'Illustrative top trim'})
for sx in (-.68,.68):
    for sy in (-.19,.19):
        local_cube('Kurz_DisplayCase_Post',(case_x+sx,case_y+sy,.91),(.055,.055,1.02),wood,{'evidence_status':'Illustrative frame'})
local_cube('Kurz_DisplayCase_Front_Glass',(case_x,case_y-.20,.91),(1.30,.012,.93),glass,{'evidence_status':'Illustrative glazing'})
local_cube('Kurz_DisplayCase_Back_Glass',(case_x,case_y+.20,.91),(1.30,.012,.93),glass,{'evidence_status':'Illustrative glazing'})
for sx in (-.715,.715):
    local_cube('Kurz_DisplayCase_Side_Glass',(case_x+sx,case_y,.91),(.012,.36,.93),glass,{'evidence_status':'Illustrative glazing'})
local_cube('Kurz_DisplayCase_Interior_Shelf',(case_x,case_y,.83),(1.30,.36,.04),wood,{'evidence_status':'Illustrative display shelf'})
for i,x in enumerate((3.45,4.25)):
    local_cube(f'Kurz_Lobby_Touchscreen_Kiosk_{i+1}',(x,-39.25,.86),(.42,.24,1.72),bronze,{'evidence_status':'Purdue reports touchscreens for directions/information in Kurz Lobby; location/dimensions illustrative'})
    local_cube(f'Kurz_Lobby_Touchscreen_Display_{i+1}',(x,-39.38,1.45),(.33,.012,.46),screens[3+i],{'evidence_status':'Illustrative display face'})

# Preserve source placement and export collection; save source-only file.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
# immediately reopen the just-saved source before validation/renders
bpy.ops.wm.open_mainfile(filepath=ASSET)
print(json.dumps({'reopened':True,'file':bpy.data.filepath,'round4_objects':sum(1 for o in bpy.data.collections['Asset_lawson_hall'].objects if o and o.name.startswith('LWSN_R4_')),'video_wall_panels':sum(1 for o in bpy.data.collections['Asset_lawson_hall'].objects if o and o.name.startswith('LWSN_R4_VideoWall_LCD_')),'roof_marked_schematic':sum(1 for o in bpy.data.collections['Asset_lawson_hall'].objects if o and o.get('evidence_status','').startswith('Schematic / unverified'))},indent=2))
