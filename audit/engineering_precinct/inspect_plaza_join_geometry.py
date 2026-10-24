import bpy, math, xml.etree.ElementTree as ET
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
root=ET.parse(r'audit/engineering_precinct/osm_snapshot.xml').getroot(); nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')}
w=next(w for w in root.findall('way') if w.attrib['id']=='283274215'); pts=[nodes[n.attrib['ref']] for n in w.findall('nd')][:-1]; xy=[((x+86.9137)*84810.60416539927,(y-40.4274)*111040.0) for x,y in pts]
area=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))/2
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in xy]])
tarea=0
for t in tris:
 a,b,c=[xy[int(i)] for i in t]; tarea=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2; tarea+=0; tarea_sum=tarea
print('POLY',len(xy),'signed_area',area,'triangles',len(tris),'triangle_area_sum',sum(abs((xy[int(t[1])][0]-xy[int(t[0])][0])*(xy[int(t[2])][1]-xy[int(t[0])][1])-(xy[int(t[1])][1]-xy[int(t[0])][1])*(xy[int(t[2])][0]-xy[int(t[0])][0]))/2 for t in tris))
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
col=bpy.data.collections['Engineering_Mall_Groundwork_Patch']
for ob in col.objects:
 if ob.name.startswith(('Engineering_Fountain_Plaza','OSM_Grass_','OSM_Way_')):
  if ob.name.startswith(('Engineering_Fountain_Plaza','OSM_Grass_')):
   print(ob.name,ob.location[:],ob.dimensions[:],len(ob.data.polygons) if ob.type=='MESH' else '')
