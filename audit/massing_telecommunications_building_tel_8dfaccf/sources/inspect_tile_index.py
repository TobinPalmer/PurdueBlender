from pathlib import Path
import struct,json
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[2]
idx=ROOT/'massing_johnson_hall_of_nursing_jnsn_823fca7'/'sources'
dbf=(idx/'TIPPECANOE_IN_TILE5000.dbf').read_bytes(); count=struct.unpack('<I',dbf[4:8])[0]; hlen=struct.unpack('<H',dbf[8:10])[0]; rlen=struct.unpack('<H',dbf[10:12])[0]
name='in2018_29951885_12'; index=next(i for i in range(count) if dbf[hlen+i*rlen+1:hlen+(i+1)*rlen].decode('ascii','ignore').find(name)>=0)
shp=(idx/'TIPPECANOE_IN_TILE5000.shp').read_bytes(); pos=100; recs=[]
while pos<len(shp):
 recno,nwords=struct.unpack('>2i',shp[pos:pos+8]); nbytes=nwords*2; data=shp[pos+8:pos+8+nbytes]; st=struct.unpack('<i',data[:4])[0]; bbox=struct.unpack('<4d',data[4:36]); recs.append((recno,bbox,st)); pos+=8+nbytes
rec=recs[index]
feature=json.loads((ROOT/'massing_telecommunications_building_tel_8dfaccf'/'sources'/'purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]
ring=feature['geometry']['rings'][0]; lon=sum(p[0] for p in ring[:-1])/(len(ring)-1); lat=sum(p[1] for p in ring[:-1])/(len(ring)-1)
xy=Transformer.from_crs(4326,2968,always_xy=True).transform(lon,lat)
print(json.dumps({'index_record':index,'tile_name':dbf[hlen+index*rlen+1:hlen+(index+1)*rlen].decode().strip(),'shape_record':rec[0],'shape_type':rec[2],'tile_bbox_epsg2968':rec[1],'tel_center_lonlat':[lon,lat],'tel_center_epsg2968':xy},indent=2))
