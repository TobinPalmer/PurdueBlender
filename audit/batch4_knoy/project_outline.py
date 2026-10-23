import json
vs=json.load(open('audit/batch4_knoy/gis_vertices_local.json'))
for i,(x,y) in enumerate(vs):
 col=(y+46)/.13+64; row=(x+15)/.126+100
 print(i,round(col,1),round(row,1),round(x,2),round(y,2))
