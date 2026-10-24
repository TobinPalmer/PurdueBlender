import bpy,os
p=os.path.abspath(r'modular/buildings/university_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
m=bpy.data.materials['Univ_Chalkboard_Slate']; nt=m.node_tree; ns=nt.nodes; links=nt.links
pr=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
cr=next((n for n in ns if n.name=='PurdueMap | surface variation | Color Grain'),None)
rr=next((n for n in ns if n.name=='PurdueMap | surface variation | Roughness Grain'),None)
if cr:
 base=tuple((cr.color_ramp.elements[0].color[i]+cr.color_ramp.elements[1].color[i])*.5 for i in range(4)); links.remove(next(l for l in links if l.to_socket==pr.inputs['Base Color']));pr.inputs['Base Color'].default_value=base
if rr:
 rough=(rr.color_ramp.elements[0].color[0]+rr.color_ramp.elements[1].color[0])*.5;links.remove(next(l for l in links if l.to_socket==pr.inputs['Roughness']));pr.inputs['Roughness'].default_value=rough
for n in list(ns):
 if n.get('purdue_surface_variation') or 'PurdueMap | surface variation' in n.name: ns.remove(n)
 # Remove newly added object-coordinate/noise nodes by label/name.
 elif n.name in ('PurdueMap | surface variation | Object Coordinates','PurdueMap | surface variation | Meter Scale Noise'): ns.remove(n)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=p);print('restored indoor chalkboard material')
