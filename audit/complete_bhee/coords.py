import json,math
r=json.load(open('audit/official_building_references.json'));o=(143.8499984741211,135);a=math.radians(39.24)
for f in r['buildings']:
 if f['fid']==292:
  print([(round((x-o[0])*math.cos(a)+(y-o[1])*math.sin(a),1),round(-(x-o[0])*math.sin(a)+(y-o[1])*math.cos(a),1)) for x,y in f['rings_xy_m'][0]])
