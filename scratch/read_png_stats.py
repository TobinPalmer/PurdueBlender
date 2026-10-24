import bpy
img=bpy.data.images.load(r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\audit\\texture_final_two\\niswonger_aviation_tech_overview.png',check_existing=False)
p=list(img.pixels); n=4; step=max(1,(len(p)//(n*20))*n); sm=[tuple(round(v,3) for v in p[i:i+3]) for i in range(0,len(p),step)]; print('dims',img.size[:],'ranges',[(min(x[c] for x in sm),max(x[c] for x in sm)) for c in range(3)],'sample',sm[:20])

