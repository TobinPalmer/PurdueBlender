import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon
root=Path(__file__).resolve().parents[2]
src=root/'audit/alpha_kappa_lambda/sources'
main=json.loads((src/'purdue_gis_fid784_2026-10-25.json').read_text(encoding='utf-8'))
lidar=json.loads((src/'indiana_lidar_building_footprints_at_alpha_kappa_lambda_2026-10-25.json').read_text(encoding='utf-8'))
main2968=json.loads((src/'purdue_gis_fid784_2026-10-25_stateplane_2968.json').read_text(encoding='utf-8'))
lidar2968=json.loads((src/'indiana_lidar_building_footprints_at_alpha_kappa_lambda_2026-10-25_stateplane_2968.json').read_text(encoding='utf-8'))

def poly(doc):
    r=doc['features'][0]['geometry']['rings'][0]
    return Polygon(r[:-1])
def metrics(doc):
    g=doc['features'][0]['geometry']['rings'][0][:-1]
    p=Polygon(g)
    area_ft2=p.area; perimeter_ft=p.length
    k=.3048006096012192
    return {'point_count':len(g),'valid':p.is_valid,'area_m2':area_ft2*k*k,'perimeter_m':perimeter_ft*k,'area_ftUS2':area_ft2,'perimeter_ftUS':perimeter_ft}
A=poly(main2968); B=poly(lidar2968)
inter=A.intersection(B).area
union=A.union(B).area
# overlay on source orthophoto using requested EPSG:4326 extent from export JSON
im=Image.open(src/'indiana_current_orthophoto_417_waldron.png').convert('RGBA')
box=(-86.9189,40.42825,-86.9177,40.42915)
w,h=im.size
layer=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
def pixels(doc):
    r=doc['features'][0]['geometry']['rings'][0][:-1]
    return [((x-box[0])/(box[2]-box[0])*w,(box[3]-y)/(box[3]-box[1])*h) for x,y in r]
mainpx=pixels(main); lidarpx=pixels(lidar)
d.polygon(mainpx,fill=(240,20,150,45),outline=(255,0,180,255),width=4)
d.line(mainpx+[mainpx[0]],fill=(255,0,180,255),width=5,joint='curve')
d.polygon(lidarpx,fill=(0,230,255,45),outline=(0,210,255,255),width=4)
d.line(lidarpx+[lidarpx[0]],fill=(0,210,255,255),width=5,joint='curve')
out=Image.alpha_composite(im,layer).convert('RGB')
legend=Image.new('RGBA',(w,h),(0,0,0,0)); ld=ImageDraw.Draw(legend); ld.rectangle((0,0,w,72),fill=(10,10,10,190))
ld.rectangle((18,18,48,48),outline=(255,0,180),width=5);ld.text((58,22),'Purdue GIS FID 784 (WGS84 coordinates)',fill='white')
ld.rectangle((570,18,600,48),outline=(0,210,255),width=5);ld.text((610,22),'Indiana 2018 LiDAR footprint',fill='white')
out=Image.alpha_composite(out.convert('RGBA'),legend).convert('RGB')
out.save(root/'audit/alpha_kappa_lambda/orthophoto_footprint_comparison.png',quality=95)
report={'coordinate_system_for_metrics':'EPSG:2968 NAD83(HARN) Indiana West US Survey Foot (service layer metadata); converted with exact 0.3048006096012192 m/ftUS','purdue_gis_geometry':metrics(main2968),'indiana_lidar_geometry':metrics(lidar2968),'purdue_gis_shape_attributes':{k:main['features'][0]['attributes'][k] for k in ('Shape__Area','Shape__Length')},'indiana_lidar_shape_attributes':{k:lidar['features'][0]['attributes'][k] for k in ('SHAPE__Area','SHAPE__Length')},'field_unit_factor_comparison':{'purdue_length_field_divided_by_native_ft_length':main['features'][0]['attributes']['Shape__Length']/metrics(main2968)['perimeter_ftUS'],'purdue_area_field_divided_by_native_ft2_area':main['features'][0]['attributes']['Shape__Area']/metrics(main2968)['area_ftUS2'],'indiana_lidar_length_field_divided_by_native_ft_length':lidar['features'][0]['attributes']['SHAPE__Length']/metrics(lidar2968)['perimeter_ftUS'],'indiana_lidar_area_field_divided_by_native_ft2_area':lidar['features'][0]['attributes']['SHAPE__Area']/metrics(lidar2968)['area_ftUS2']},'purdue_vs_lidar_polygon_overlap_iou':inter/union,'intersection_area_m2':inter*(.3048006096012192**2),'union_area_m2':union*(.3048006096012192**2),'orthophoto_overlay':'audit/alpha_kappa_lambda/orthophoto_footprint_comparison.png'}
(root/'audit/alpha_kappa_lambda/footprint_registration.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

