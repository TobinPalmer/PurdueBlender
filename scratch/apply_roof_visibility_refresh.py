import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings')
OUT=os.path.join(ROOT,'audit','material_review','roof_visibility_refresh')
os.makedirs(OUT,exist_ok=True)
FILES=['walc.blend','felix_haas_hall.blend','mccutcheon_hall.blend']
def set_ramp(ramp, base, amount, lo=0.0, hi=1.0):
    ramp.interpolation='EASE'
    while len(ramp.elements)>2: ramp.elements.remove(ramp.elements[-1])
    a=ramp.elements[0]; b=ramp.elements[1]
    a.position=lo; b.position=hi
    a.color=tuple(max(0,min(1,c*(1-amount))) for c in base[:3])+(1.0,)
    b.color=tuple(max(0,min(1,c*(1+amount))) for c in base[:3])+(1.0,)
def add_roughness_range(nt, noise, bsdf, label, low, high):
    ramp=next((n for n in nt.nodes if n.label==label),None)
    if ramp is None:
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.label=label
    ramp.color_ramp.interpolation='EASE'
    ramp.color_ramp.elements[0].position=.12; ramp.color_ramp.elements[0].color=(low,low,low,1)
    ramp.color_ramp.elements[1].position=.88; ramp.color_ramp.elements[1].color=(high,high,high,1)
    if not any(l.to_node==ramp and l.to_socket==ramp.inputs['Fac'] for l in nt.links): nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    for l in list(bsdf.inputs['Roughness'].links): nt.links.remove(l)
    nt.links.new(ramp.outputs['Color'],bsdf.inputs['Roughness'])
for fn in FILES:
    path=os.path.join(ASSET,fn)
    bpy.ops.wm.open_mainfile(filepath=path)
    changed=[]
    mats=([bpy.data.materials.get('Roof.009'),bpy.data.materials.get('WALC_Reference_Roof')] if fn=='walc.blend' else
          [bpy.data.materials.get('HAAS_Slate_Roof')] if fn=='felix_haas_hall.blend' else
          [bpy.data.materials.get('Roof_Membrane')])
    for mat in mats:
        if not mat or not mat.use_nodes: continue
        nt=mat.node_tree; bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
        noise=next((n for n in nt.nodes if n.type=='TEX_NOISE'),None)
        if not bsdf or not noise: continue
        noise.inputs['Scale'].default_value=.55 if fn!='felix_haas_hall.blend' else .48
        noise.inputs['Detail'].default_value=1.0
        noise.inputs['Roughness'].default_value=.56
        base=tuple(bsdf.inputs['Base Color'].default_value)
        cr=next((n for n in nt.nodes if n.type=='VALTORGB' and ('Color Grain' in n.label or 'color variation' in n.label.lower())),None)
        if fn=='mccutcheon_hall.blend':
            mr=next((n for n in nt.nodes if n.type=='MAP_RANGE' and 'color range' in n.label.lower()),None)
            if mr:
                mr.inputs['From Min'].default_value=.10; mr.inputs['From Max'].default_value=.90
                mr.inputs['To Min'].default_value=.91; mr.inputs['To Max'].default_value=1.09
            # Existing multiply chain preserves the authored slate hue.
            rr=next((n for n in nt.nodes if n.type=='MAP_RANGE' and 'roughness' in n.label.lower()),None)
            if rr:
                rr.inputs['From Min'].default_value=.12; rr.inputs['From Max'].default_value=.88
                rr.inputs['To Min'].default_value=.72; rr.inputs['To Max'].default_value=.85
        else:
            if cr: set_ramp(cr.color_ramp,base,.085)
            add_roughness_range(nt,noise,bsdf,'Broad roof roughness variation',.73,.85)
        if fn=='felix_haas_hall.blend':
            bump=next((n for n in nt.nodes if n.type=='BUMP' and 'relief' in n.label.lower()),None)
            if bump: bump.inputs['Strength'].default_value=.018; bump.inputs['Distance'].default_value=.0002
        # Preserve existing small relief/metal/color networks; only broaden the low-frequency roof grain.
        mat['roof_grain_visibility_pass']='Broad low-contrast tonal and roughness drift for campus-scale visibility'
        changed.append(mat.name)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print('SAVED',fn,changed)
