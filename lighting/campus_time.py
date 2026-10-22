"""Portable procedural campus sky; run once in Blender's Text Editor."""
bl_info = {"name": "Campus Time Sky", "author": "PurdueMap", "version": (1, 0, 0), "blender": (4, 2, 0), "location": "3D View > Sidebar > Campus Sky", "category": "Lighting"}

import bpy
import math

DAY = 'max(0,sin((t-6)*pi/12))'
GLOW = 'max(0,1-abs(t-18)/2.5)+0.65*max(0,1-abs(t-6)/2.5)'

def drive(owner, path, scene, expression, index=None):
    fc = owner.driver_add(path) if index is None else owner.driver_add(path, index)
    dr = fc.driver
    dr.type = 'SCRIPTED'
    for old in list(dr.variables):
        dr.variables.remove(old)
    v = dr.variables.new()
    v.name = 't'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'SCENE'
    v.targets[0].id = scene
    v.targets[0].data_path = '["campus_time"]'
    dr.expression = expression

def build_sky(scene=None):
    scene = scene or bpy.context.scene
    if 'campus_time' not in scene:
        scene['campus_time'] = 18.0
    scene.id_properties_ui('campus_time').update(min=0.0, max=24.0, soft_min=0.0, soft_max=24.0, description='Artistic local time: dawn 6, noon 12, pink sunset 18, night 0')
    if scene.world and scene.world.name != 'Campus Time Sky':
        scene['campus_previous_world'] = scene.world.name
        if not scene.world.library:
            scene.world.use_fake_user = True
    world = bpy.data.worlds.get('Campus Time Sky') or bpy.data.worlds.new('Campus Time Sky')
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    def node(kind, name, x, y):
        n = nt.nodes.new(kind); n.label = name; n.location = (x,y); return n
    def link(a,b): nt.links.new(a,b)
    out = node('ShaderNodeOutputWorld','Campus sky',1100,0)
    bg = node('ShaderNodeBackground','Atmosphere illumination',880,0)
    drive(bg.inputs['Strength'],'default_value',scene,f'0.14+0.55*({DAY})+0.22*({GLOW})')
    link(bg.outputs[0],out.inputs['Surface'])
    tc = node('ShaderNodeTexCoord','Sky direction',-1100,0)
    sep = node('ShaderNodeSeparateXYZ','Altitude',-880,200)
    direction = node('ShaderNodeVectorMath','Outward sky direction',-1030,-80)
    direction.operation='SCALE'; direction.inputs['Scale'].default_value=-1
    link(tc.outputs['Normal'],direction.inputs[0])
    link(direction.outputs['Vector'],sep.inputs[0])
    ramp = node('ShaderNodeValToRGB','Peach horizon to lavender zenith',-590,240)
    link(sep.outputs['Z'],ramp.inputs[0])
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    palettes=[(0.0,(.012,.016,.035),(.55,.72,1.0),(1.0,.42,.23)),(.16,(.008,.011,.027),(.20,.43,.8),(.53,.20,.42)),(.58,(.003,.005,.018),(.065,.22,.55),(.18,.12,.34)),(1.0,(.002,.003,.012),(.035,.12,.36),(.055,.07,.20))]
    for i,(p,night,day,sunset) in enumerate(palettes):
        e = ramp.color_ramp.elements[0] if i == 0 else ramp.color_ramp.elements.new(p)
        e.position=p
        for k in range(3):
            drive(e,'color',scene,f'{night[k]}+({day[k]}-{night[k]})*({DAY})+({sunset[k]}-{night[k]})*({GLOW})',k)
        e.color[3]=1
    mapping=node('ShaderNodeVectorMath','Long layered clouds',-890,-200)
    mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(2.2,2.2,9.0)
    link(direction.outputs['Vector'],mapping.inputs[0])
    noise=node('ShaderNodeTexNoise','Soft turbulent cloud layers',-650,-160)
    noise.inputs['Scale'].default_value=2.7; noise.inputs['Detail'].default_value=5; noise.inputs['Roughness'].default_value=.68
    link(mapping.outputs['Vector'],noise.inputs['Vector'])
    mask=node('ShaderNodeValToRGB','Feathered cloud edges',-400,-150)
    mask.color_ramp.elements[0].position=.42; mask.color_ramp.elements[1].position=.69
    link(noise.outputs['Fac'],mask.inputs[0])
    altitude=node('ShaderNodeMapRange','Cloud hemisphere fade',-400,-400)
    altitude.inputs['From Min'].default_value=.015; altitude.inputs['From Max'].default_value=.18
    link(sep.outputs['Z'],altitude.inputs['Value'])
    mult=node('ShaderNodeMath','Cloud opacity',-120,-120); mult.operation='MULTIPLY'
    link(mask.outputs[0],mult.inputs[0]); link(altitude.outputs[0],mult.inputs[1])
    cloud=node('ShaderNodeValToRGB','Pink cloud highlights and violet shadows',-120,-360)
    link(noise.outputs['Fac'],cloud.inputs[0])
    for e,n,d,s in [(cloud.color_ramp.elements[0],(.006,.008,.018),(.33,.40,.55),(.22,.07,.19)),(cloud.color_ramp.elements[1],(.025,.03,.055),(1,1,.95),(1.5,.49,.62))]:
        for k in range(3): drive(e,'color',scene,f'{n[k]}+({d[k]}-{n[k]})*({DAY})+({s[k]}-{n[k]})*({GLOW})',k)
        e.color[3]=1
    mix=node('ShaderNodeMixRGB','Clouds over atmosphere',570,0)
    link(mult.outputs[0],mix.inputs[0]); link(ramp.outputs[0],mix.inputs[1]); link(cloud.outputs[0],mix.inputs[2]); link(mix.outputs[0],bg.inputs['Color'])
    # Replace only collection paths containing linked suns; never edit a library.
    linked_suns={ob for ob in scene.objects if ob.type=='LIGHT' and ob.data.type=='SUN' and not ob.name.startswith('Campus ') and (ob.library or ob.data.library)}
    def filtered_collection(col):
        changed_children=[]
        for child in col.children:
            repl=filtered_collection(child)
            if repl is not child: changed_children.append((child,repl))
        removed=[ob for ob in col.objects if ob in linked_suns]
        if not removed and not changed_children: return col
        clone=col.copy()
        clone.name=col.name+' Campus Lighting'
        for ob in removed: clone.objects.unlink(ob)
        for old,new in changed_children:
            clone.children.unlink(old); clone.children.link(new)
        return clone
    for col in list(scene.collection.children):
        replacement=filtered_collection(col)
        if replacement is not col:
            scene.collection.children.unlink(col); scene.collection.children.link(replacement)
    for ob in list(scene.collection.objects):
        if ob in linked_suns: scene.collection.objects.unlink(ob)
    for ob in scene.objects:
        if ob.type=='LIGHT' and ob.data.type=='SUN' and not ob.name.startswith('Campus '):
            if 'campus_original_energy' not in ob.data: ob.data['campus_original_energy']=ob.data.energy
            ob.data.energy=0
    def sun(name):
        ob=bpy.data.objects.get(name)
        if not ob:
            ob=bpy.data.objects.new(name,bpy.data.lights.new(name,'SUN')); scene.collection.objects.link(ob)
        return ob
    key=sun('Campus Sunset Sun'); key.rotation_mode='XYZ'; key.data.angle=math.radians(4)
    drive(key,'rotation_euler',scene,'pi/2-1.15*sin((t-5)*pi/14)',0)
    drive(key,'rotation_euler',scene,'(t-12)*pi/12+0.7',2)
    drive(key.data,'energy',scene,'max(0,3.2*sin((t-5)*pi/14))')
    for k,ex in enumerate(['1.0',f'0.35+0.6*({DAY})',f'0.18+0.7*({DAY})']): drive(key.data,'color',scene,ex,k)
    fill=sun('Campus Twilight Fill'); fill.rotation_euler=(.4,-.5,-.7); fill.data.angle=.6; fill.data.color=(.38,.49,1)
    drive(fill.data,'energy',scene,f'0.08+0.12*({GLOW})')
    scene.view_settings.exposure=-0.65
    # The campus has hundreds of lights; its default pool overflows in EEVEE.
    if hasattr(scene, 'eevee'):
        options={i.identifier for i in scene.eevee.bl_rna.properties['shadow_pool_size'].enum_items}
        if '512' in options: scene.eevee.shadow_pool_size='512'
    scene['campus_sky_notes']='Artistic 24-hour cycle; not astronomical. Set campus_time in Scene Custom Properties; optional Campus Sky sidebar panel.'
    scene.frame_set(scene.frame_current)
    bpy.context.view_layer.update()
    return world

class CAMPUS_OT_time_preset(bpy.types.Operator):
    bl_idname='campus.time_preset'
    bl_label='Set Campus Time'
    time: bpy.props.FloatProperty(default=18)
    def execute(self,context):
        context.scene['campus_time']=self.time
        context.scene.update_tag()
        context.scene.frame_set(context.scene.frame_current)
        context.view_layer.update()
        return {'FINISHED'}

class CAMPUS_PT_sky(bpy.types.Panel):
    bl_label='Campus Sky'; bl_idname='CAMPUS_PT_sky'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='Campus Sky'
    def draw(self,context):
        layout=self.layout
        if 'campus_time' not in context.scene: return
        layout.prop(context.scene,'["campus_time"]',text='Time',slider=True)
        row=layout.row(align=True)
        for name,time in [('Dawn',6),('Noon',12),('Sunset',18),('Night',0)]: row.operator('campus.time_preset',text=name).time=time
        layout.label(text='Artistic local time (0–24 hours)')

def register():
    for cls in (CAMPUS_OT_time_preset,CAMPUS_PT_sky):
        old=getattr(bpy.types,cls.__name__,None)
        if old:
            try: bpy.utils.unregister_class(old)
            except RuntimeError: pass
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed((CAMPUS_OT_time_preset,CAMPUS_PT_sky)):
        old=getattr(bpy.types,cls.__name__,None)
        if old:
            bpy.utils.unregister_class(old)

if __name__=='__main__':
    build_sky()
    register()
