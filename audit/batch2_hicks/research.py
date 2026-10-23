import requests
from pathlib import Path
p=Path('audit/batch2_hicks')
u='https://schooldesigns.com/Projects/purdue-university-hicks-undergraduate-library/'
s=requests.get(u).text;(p/'schooldesigns.html').write_text(s,encoding='utf8')
import re
print('\n'.join(re.findall(r'(?:src|href)=["\']([^"\']+\.(?:jpg|png|jpeg)[^"\']*)',s)))
