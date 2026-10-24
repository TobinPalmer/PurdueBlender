import bpy,numpy as np
p=r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\audit\\complete_knoy\\knoy_typical_plan_crop.png'
im=bpy.data.images.load(p,check_existing=False); a=np.array(im.pixels[:],dtype=np.float32).reshape((im.size[1],im.size[0],4))
g=a[:,:,:3].mean(axis=2)
print('size',im.size,'gray quantiles',np.quantile(g,[0,.01,.05,.1,.2,.5,.9,1]),'dark pixels',[(v,float((g<v).mean())) for v in [.2,.35,.5,.65,.8]])
