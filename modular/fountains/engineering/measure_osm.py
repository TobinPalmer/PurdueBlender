import xml.etree.ElementTree as E,json,math
from pathlib import Path
D=Path('modular/fountains/engineering');r=E.parse(D/'osm.xml').getroot();nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in r.findall('node')};pts=[nodes[n.attrib['ref']] for n in r.find('way').findall('nd')];origin=(-86.9137,40.4274);p=[((a-origin[0])*84810.60416539927,(b-origin[1])*111040) for a,b in pts];A=Cx=Cy=0
for (x,y),(xx,yy) in zip(p,p[1:]):
 cross=x*yy-xx*y;A+=cross;Cx+=(x+xx)*cross;Cy+=(y+yy)*cross
c=[Cx/(3*A),Cy/(3*A)];result={'osm_way':283274213,'centroid_local_m':c,'width_m':max(x for x,y in p)-min(x for x,y in p),'length_m':max(y for x,y in p)-min(y for x,y in p),'old_center':[0,195],'old_error_to_osm_m':math.hypot(c[0],195-c[1]),'survey_accuracy':'unknown','area_m2':abs(A)/2};(D/'position_measurement.json').write_text(json.dumps(result,indent=2));print(result)
