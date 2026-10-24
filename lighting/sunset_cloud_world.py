"""Modeled sunset sky and campus-spanning cloud banks."""
import bpy, bmesh, math, random
from mathutils import Vector

def _drive(owner,path,scene,expression,index=None):
    fc=owner.driver_add(path) if index is None else owner.driver_add(path,index)
    dr=fc.driver;dr.type='SCRIPTED'
    for old in list(dr.variables):dr.variables.remove(old)
    var=dr.variables.new();var.name='t';var.type='SINGLE_PROP';var.targets[0].id_type='SCENE';var.targets[0].id=scene;var.targets[0].data_path='["campus_time"]'
    dr.expression=expression

def build_world(scene):
    if 'campus_time' not in scene:scene['campus_time']=18.0
    world=bpy.data.worlds.get('Campus Time Sky') or bpy.data.worlds.new('Campus Time Sky')
    scene.world=world;world.use_nodes=True;nt=world.node_tree;nt.nodes.clear()
    sky=nt.nodes.new('ShaderNodeTexSky');sky.label='Nishita sunset atmosphere';sky.sky_type='MULTIPLE_SCATTERING';sky.sun_disc=True;sky.sun_size=math.radians(.65);sky.sun_intensity=1.35;sky.air_density=1.55;sky.ozone_density=.72
    _drive(sky,'sun_elevation',scene,'0.04+1.41*max(0,sin((t-6)*pi/12))')
    _drive(sky,'sun_rotation',scene,'(t-12)*pi/12+0.7')
    bg=nt.nodes.new('ShaderNodeBackground');bg.label='Atmosphere lighting';bg.inputs['Strength'].default_value=.8
    geom=nt.nodes.new('ShaderNodeNewGeometry');geom.label='View direction';sep=nt.nodes.new('ShaderNodeSeparateXYZ');mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=1;mapping.inputs['From Max'].default_value=-1;mapping.clamp=True
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.label='Warm horizon to deep twilight';ramp.color_ramp.interpolation='EASE'
    ramp.color_ramp.elements[0].position=.46;ramp.color_ramp.elements[0].color=(.48,.075,.025,1)
    ramp.color_ramp.elements[1].position=.58;ramp.color_ramp.elements[1].color=(.45,.27,.42,1)
    for pos,color in [(.49,(.95,.23,.045,1)),(.51,(1.0,.37,.15,1)),(.535,(.88,.34,.31,1)),(.7,(.26,.30,.48,1)),(.84,(.10,.15,.30,1))]:
        el=ramp.color_ramp.elements.new(pos);el.color=color
    sunset=nt.nodes.new('ShaderNodeBackground');sunset.label='Camera-visible sunset gradient';sunset.inputs['Strength'].default_value=.85
    path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');mix.label='Sunset backdrop; sky lighting'
    out=nt.nodes.new('ShaderNodeOutputWorld');out.label='Sunset sky output'
    nt.links.new(sky.outputs['Color'],bg.inputs['Color']);nt.links.new(geom.outputs['Incoming'],sep.inputs[0]);nt.links.new(sep.outputs['Z'],mapping.inputs['Value']);nt.links.new(mapping.outputs['Result'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],sunset.inputs['Color']);nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(bg.outputs[0],mix.inputs[1]);nt.links.new(sunset.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
    old_dome=bpy.data.objects.get('Campus Sunset Sky Dome')
    if old_dome:bpy.data.objects.remove(old_dome,do_unlink=True)
    return world

def build_sky_dome(scene,radius=12000.0):
    """Camera-visible orange-to-rose sunset gradient; the world sky still lights the scene."""
    old=bpy.data.objects.get('Campus Sunset Sky Dome')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    mesh=bpy.data.meshes.new('Campus Sunset Sky Dome Mesh')
    bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=96,v_segments=48,radius=radius);bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()
    ob=bpy.data.objects.new('Campus Sunset Sky Dome',mesh);scene.collection.objects.link(ob)
    mat=bpy.data.materials.get('Campus Sunset Gradient') or bpy.data.materials.new('Campus Sunset Gradient')
    mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    geom=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=-radius;mapping.inputs['From Max'].default_value=radius;mapping.clamp=True;ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation='EASE'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    ramp.color_ramp.elements[0].position=.497;ramp.color_ramp.elements[0].color=(.72,.13,.035,1)
    for pos,color in [(.505,(1.0,.29,.075,1)),(.518,(.94,.34,.25,1)),(.55,(.64,.3,.42,1)),(.64,(.27,.29,.43,1)),(.82,(.09,.14,.27,1)),(1.0,(.035,.06,.15,1))]:
        el=ramp.color_ramp.elements.new(pos);el.color=color
    emission=nt.nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=.85
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(geom.outputs['Position'],sep.inputs[0]);nt.links.new(sep.outputs['Z'],mapping.inputs['Value']);nt.links.new(mapping.outputs['Result'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],emission.inputs['Color']);nt.links.new(emission.outputs[0],out.inputs['Surface'])
    ob.data.materials.append(mat);ob['purpose']='camera-visible sunset gradient dome';ob['radius_m']=radius
    return ob

def build_clouds(scene,bounds,spacing=850.0,seed=24731):
    old=bpy.data.collections.get('Campus Sunset Clouds')
    if old:
        for ob in list(old.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(old)
    col=bpy.data.collections.new('Campus Sunset Clouds');scene.collection.children.link(col)
    mats=[]
    for name,color in [('Cloud_Warm_Lower',(.9,.54,.39,1)),('Cloud_Rose_High',(.66,.48,.67,1))]:
        mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.diffuse_color=color;mat.use_nodes=True
        bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.96
        if 'Subsurface Weight' in bs.inputs:bs.inputs['Subsurface Weight'].default_value=.06
        mats.append(mat)
    bm=bmesh.new();rng=random.Random(seed);puff_count=0
    minx,maxx,miny,maxy=bounds
    def cloud_layer(step,prob,zlo,zhi,width_range,depth_range,height_range,material_index,puff_range):
        nonlocal puff_count
        x=minx
        while x<=maxx:
            y=miny
            while y<=maxy:
                if rng.random()<prob:
                    cx=x+rng.uniform(-step*.25,step*.25);cy=y+rng.uniform(-step*.25,step*.25);cz=rng.uniform(zlo,zhi)
                    sx=rng.uniform(*width_range);sy=rng.uniform(*depth_range);puffs=rng.randint(*puff_range)
                    # Thin base gives each cluster a broad underside; rounded lobes
                    # make the silhouette read as a real cloud bank at a distance.
                    specs=[(cx,cy,cz-rng.uniform(12,26),sx*.68,sy*.56,rng.uniform(38,62))]
                    for q in range(puffs):
                        phase=(2*math.pi*q/puffs)+rng.uniform(-.24,.24)
                        ring=rng.uniform(.08,.6)
                        specs.append((cx+math.cos(phase)*sx*ring,cy+math.sin(phase)*sy*ring,cz+rng.uniform(-12,32),rng.uniform(sx*.18,sx*.42),rng.uniform(sy*.2,sy*.46),rng.uniform(*height_range)))
                    for px,py,pz,rx,ry,rz in specs:
                        geom=bmesh.ops.create_uvsphere(bm,u_segments=12,v_segments=8,radius=1)
                        for v in geom['verts']:
                            v.co.x=v.co.x*rx+px;v.co.y=v.co.y*ry+py;v.co.z=v.co.z*rz+pz
                        # Material slots are assigned by cloud altitude after mesh creation.
                        puff_count+=1
                y+=step
            x+=step
    cloud_layer(spacing,.82,390,560,(170,290),(110,210),(42,92),0,(7,11))
    cloud_layer(spacing*1.55,.62,760,1060,(300,520),(190,360),(50,115),1,(8,12))
    mesh=bpy.data.meshes.new('Campus_Sunset_CloudBank_Mesh');bm.to_mesh(mesh);bm.free();mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth=True
        if poly.center.z>=650:poly.material_index=1
    ob=bpy.data.objects.new('Campus_Sunset_CloudBanks',mesh);col.objects.link(ob)
    mesh.materials.append(mats[0]);mesh.materials.append(mats[1])
    # All cloud banks are modeled into one efficient campus-scale mesh.
    ob['cloud_bank_count']=puff_count;ob['cloud_seed']=seed;ob['cloud_bounds_m']=list(bounds)
    return ob,puff_count

def install_sunset_lights(scene):
    key=scene.objects.get('Campus Sunset Sun')
    if not key:
        ld=bpy.data.lights.new('Campus Sunset Sun','SUN');key=bpy.data.objects.new('Campus Sunset Sun',ld);scene.collection.objects.link(key)
    key.rotation_mode='XYZ';key.data.angle=math.radians(4)
    for path,idx,exp in [('rotation_euler',0,'pi/2-1.15*sin((t-5)*pi/14)'),('rotation_euler',2,'(t-12)*pi/12+0.7')]:
        try:key.driver_remove(path,idx)
        except TypeError:pass
        _drive(key,path,scene,exp,idx)
    try:key.data.driver_remove('energy')
    except TypeError:pass
    _drive(key.data,'energy',scene,'max(0,4.2*sin((t-5)*pi/14))')
    for k,ex in enumerate(['1.0','0.35+0.6*max(0,sin((t-6)*pi/12))','0.18+0.7*max(0,sin((t-6)*pi/12))']):
        try:key.data.driver_remove('color',k)
        except TypeError:pass
        _drive(key.data,'color',scene,ex,k)
    fill=scene.objects.get('Campus Twilight Fill')
    if not fill:
        ld=bpy.data.lights.new('Campus Twilight Fill','SUN');fill=bpy.data.objects.new('Campus Twilight Fill',ld);scene.collection.objects.link(fill)
    fill.rotation_euler=(.4,-.5,-.7);fill.data.angle=.6;fill.data.color=(.72,.55,.8)
    try:fill.data.driver_remove('energy')
    except TypeError:pass
    _drive(fill.data,'energy',scene,'0.12+0.22*(max(0,1-abs(t-18)/2.5))')

def install_campus_sunset(scene,bounds,spacing=850.0,seed=24731):
    build_world(scene);ob,count=build_clouds(scene,bounds,spacing,seed);install_sunset_lights(scene)
    scene.view_settings.exposure=-.1
    scene['campus_time']=18.0;scene['campus_sky_notes']='Nishita sunset sky plus modeled, campus-spanning cloud banks. Clouds are a single linked scene mesh; the 24-hour control drives sky and sun.'
    scene.frame_set(scene.frame_current);scene.view_layers.update()
    return ob,count
