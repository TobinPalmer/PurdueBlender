from pathlib import Path
p=Path('audit/complete_me/partitions.py');s=p.read_text();a=s.index('def pt');b=s.index('# Trace',a);s=s[:a]+'''def pt(x,y):return (128.998992+(x-179)/391*(96.012792-128.998992)+(y-224)/616*(86.567013-128.998992),92.123264+(x-179)/391*(65.063032-92.123264)+(y-224)/616*(144.401325-92.123264))
'''+s[b:];p.write_text(s)
