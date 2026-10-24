import bpy,os
for f in ['mccutcheon_hall_roof_close.png','niswonger_aviation_tech_roof_close.png']:
 img=bpy.data.images.load(os.path.abspath('audit/texture_final_two/'+f),check_existing=False); a=list(img.pixels); vals=[a[i:i+3] for i in range(0,len(a),4)]; print(f,[(round(min(v[c] for v in vals),3),round(max(v[c] for v in vals),3),round(sum(v[c] for v in vals)/len(vals),3)) for c in range(3)])
