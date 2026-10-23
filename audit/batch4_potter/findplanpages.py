import pymupdf
p=pymupdf.open('audit/complete_potter/study.pdf')
for i in range(0,len(p)):
 t=p[i].get_text()
 if '7,789 SF' in t or '1,708 SF' in t or '3,547 SF' in t:
  print(i+1,repr(t[:130].replace('\n',' | ')), 'PAGE',repr(t[-150:].replace('\n',' | ')))
  if i>60:break
