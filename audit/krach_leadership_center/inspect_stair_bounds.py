import bpy,json
st=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
vs=[tuple(v.co) for v in st.data.vertices]
print('count',len(vs),'bounds',[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)])
print('first',vs[:3]); print('near800',vs[790:810]); print('last',vs[-20:])
