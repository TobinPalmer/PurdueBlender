import sys,json
sys.path.insert(0,'audit/complete_me/deps');import pymupdf as f
r=json.load(open('audit/official_building_references.json'));doc=f.open();page=doc.new_page(width=1000,height=1000)
for a in r['buildings']:
 if a['fid'] not in(857,108):continue
 q=[f.Point(x*6,950-y*6) for x,y in a['rings_xy_m'][0]];shape=page.new_shape();shape.draw_polyline(q);shape.finish(width=2,color=(0,0,0));shape.commit()
 for i,p in enumerate(q):
  if i%5==0:page.insert_text(p,str(i),fontsize=12,color=(1,0,0))
page.get_pixmap().save('audit/complete_me/gis.png')
