import sys
print(sys.executable)
for name in ['PIL','cv2','numpy']:
 try:
  m=__import__(name); print(name,getattr(m,'__version__','available'))
 except Exception as e: print(name,e)
