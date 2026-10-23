import json
for o in json.load(open('audit/batch4_knoy/objects.json')):
 if 'TracePartition' in o[0]:
  print(o[0], 'min', o[1], 'max', o[2], 'dim', [round(o[2][i]-o[1][i],2) for i in range(3)])
