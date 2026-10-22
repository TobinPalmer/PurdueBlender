import gzip,struct,json
from pathlib import Path
D=Path(__file__).parent
rows=[]
for frame in [1,24,48,72,96]:
 p=D/'cache/attempt1/data'/('pp_%04d.uni'%frame)
 if not p.exists():continue
 d=gzip.open(p,'rb').read();n=struct.unpack_from('<i',d,4)[0];off=len(d)-n*16;vv=[struct.unpack_from('<3f',d,off+i*16) for i in range(n)];rows.append({'frame':frame,'particles':n,'cache_header':d[:4].decode(),'header_bytes':off,'grid_bounds':[[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)] if n else None,'method':'Mantaflow PB02 header count then16byteXYZ+flag entries; grid coordinates, cell14/192m; not independently calibrated real discharge'})
(D/'particle_verification.json').write_text(json.dumps(rows,indent=2));print(rows)
