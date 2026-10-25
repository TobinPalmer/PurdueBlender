"""Correct R3 coping/joint placement to follow the 0.12 m roof fall."""
import bpy
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');P=ROOT/'modular/buildings/niswonger_aviation_tech.blend';a=bpy.data.collections['Asset_niswonger_aviation_tech']
# Recreate R3 metal caps and seams as mesh strips whose height follows each roof plane.
for o in list(a.objects):
 if o.name.startswith(('NISW_R3_Roof_Edge_','NISW_R3_Roof_Lap_')):bpy.data.objects.remove(o,do_unlink=True)
metal=bpy.data.materials['NISW_R3_Roof_Edge_Metal'];seam=bpy.data.materials['NISW_R3_Roof_Lap_Seam']
def prism(name, coords, material, bevel=.004):
 # coords are four bottom perimeter points followed by corresponding four top perimeter points.
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(coords,[],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]);me.materials.append(material);me.update()
 ob=bpy.data.objects.new(name,me);a.objects.link(ob)
 if bevel:
  m=ob.modifiers.new('Soft sheet edge','BEVEL');m.width=bevel;m.segments=2
  m=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return ob
def endcap(name,x0,x1,y0,y1,zfun,lower=.012,upper=.045):
 # Rectangular strip along a roof boundary, with top/bottom elevations following roof fall in x.
 p=[(x0,y0,zfun(x0)-lower),(x1,y0,zfun(x1)-lower),(x1,y1,zfun(x1)-lower),(x0,y1,zfun(x0)-lower),
    (x0,y0,zfun(x0)+upper),(x1,y0,zfun(x1)+upper),(x1,y1,zfun(x1)+upper),(x0,y1,zfun(x0)+upper)]
 return prism(name,p,metal)
# Existing wing roof height interpolation from the retained four-corner roof mesh.
zB=lambda x:7.84-.12*(x+31.7)/(4.84+31.7)
zA=lambda x:4.72-.12*(x+39.45)/(-31.85+39.45)
# Roof perimeter and transitions. Approximate locations retained from R2; caps are thin edge metal, not walls.
endcap('NISW_R3_Roof_Edge_Brick_West',-39.51,-39.39,7.15,42.35,zA)
endcap('NISW_R3_Roof_Edge_Brick_North',-39.45,-31.85,42.29,42.41,zA)
endcap('NISW_R3_Roof_Edge_Brick_South',-39.45,-31.85,7.09,7.21,zA)
endcap('NISW_R3_Roof_Edge_Classroom_North',-31.7,4.84,43.89,44.01,zB)
endcap('NISW_R3_Roof_Edge_Classroom_West',-31.76,-31.64,7.15,43.95,zB)
endcap('NISW_R3_Roof_Edge_Classroom_South',-31.7,4.84,7.09,7.21,zB)
# Sparse low lap lines follow the plane and are only 12 mm proud; pitch indicates a qualitative panel break, not a measured module.
def seam_y(name,x,y0,y1,z,dx=.018):
 return prism(name,[(x-dx/2,y0,z+.001),(x+dx/2,y0,z+.001),(x+dx/2,y1,z+.001),(x-dx/2,y1,z+.001),
                    (x-dx/2,y0,z+.013),(x+dx/2,y0,z+.013),(x+dx/2,y1,z+.013),(x-dx/2,y1,z+.013)],seam,.002)
for i,x in enumerate([-29.0,-23.0,-17.0,-11.0,-5.0,1.0]):seam_y(f'NISW_R3_Roof_Lap_Classroom_{i:02d}',x,7.35,43.75,zB(x))
seam_y('NISW_R3_Roof_Lap_Brick_00',-35.70,7.35,42.15,zA(-35.70))
# The visible Hangar 1 roof is dark gray in the overhead imagery; give only its roof mesh a restrained gray membrane finish.
hmat=bpy.data.materials.get('NISW_R3_Hangar_Roof_Aerial_Gray') or bpy.data.materials.new('NISW_R3_Hangar_Roof_Aerial_Gray')
hmat.diffuse_color=(.22,.24,.25,1);hmat.use_nodes=True;hbs=hmat.node_tree.nodes.get('Principled BSDF');hbs.inputs['Base Color'].default_value=(.22,.24,.25,1);hbs.inputs['Roughness'].default_value=.68;hbs.inputs['Metallic'].default_value=.08
hmat['source_basis']='Qualitative dark-gray tone of the Hangar 1 roof visible in the Esri World Imagery overhead tiles; surface material identity unverified.'
h=bpy.data.objects['NISW_Flat_Roof_Membrane'];h.data.materials.clear();h.data.materials.append(hmat);h.hide_render=False
bpy.data.objects['NISW_Photographic_Sloping_Roof'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(P))
print('Aligned 13 roof detail strips; enabled both existing roof shells; updated Hangar 1 membrane response.')
