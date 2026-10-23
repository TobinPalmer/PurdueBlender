exec(open('audit/complete_me/check_partition.py').read().split('bad=[]')[0]);out=[]
for line in ns['lines']:
 g=LineString([ns['pt'](*v) for v in line]).intersection(poly.buffer(-.3))
 for seg in ([g] if g.geom_type=='LineString' else getattr(g,'geoms',[])):
  if seg.length>.25:out.append(list(seg.coords))
Path('audit/complete_me/clipped_lines.json').write_text(json.dumps(out))
p=Path('audit/complete_me/partitions.py');s=p.read_text().replace('for idx,line in enumerate(lines):','for idx,line in enumerate(json.loads((D/\'clipped_lines.json\').read_text())):').replace('for vv in [[pt(*p) for p in line]]:','for vv in [line]:');p.write_text(s)
