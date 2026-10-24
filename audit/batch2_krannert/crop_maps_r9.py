from PIL import Image
p='audit/batch2_krannert/krannert_emergency_map_page-4.png'
im=Image.open(p)
im.crop((0,40,420,1080)).save('audit/batch2_krannert/krannert_emergency_map_page4_crop_review.png')
im.crop((700,900,850,1100)).save('audit/batch2_krannert/krannert_emergency_map_page4_north_review.png')
