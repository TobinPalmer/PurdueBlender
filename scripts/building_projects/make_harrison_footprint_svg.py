from pathlib import Path

# Generate an SVG
rings = [
  [-1139.761, -266.327], [-1139.894, -256.911], [-1138.459, -256.880], [-1138.323, -250.796],
  [-1135.091, -250.869], [-1135.104, -240.869], [-1118.663, -240.715], [-1118.771, -229.260],
  [-1140.731, -229.331], [-1140.609, -217.081], [-1074.179, -216.778], [-1073.887, -229.276],
  [-1086.581, -229.159], [-1086.546, -240.461], [-1081.166, -240.425], [-1080.890, -279.059],
  [-1086.258, -279.141], [-1086.193, -290.632], [-1073.725, -290.575], [-1073.752, -302.755],
  [-1140.274, -303.152], [-1140.389, -290.868], [-1118.441, -290.843], [-1118.436, -279.352],
  [-1142.413, -279.508], [-1142.536, -267.898], [-1143.864, -267.907], [-1143.871, -266.578],
  [-1139.761, -266.327]
]

min_x = min(p[0] for p in rings) - 5
max_x = max(p[0] for p in rings) + 5
min_y = min(p[1] for p in rings) - 5
max_y = max(p[1] for p in rings) + 5

scale = 10
width = int((max_x - min_x) * scale)
height = int((max_y - min_y) * scale)

svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#222">']
points_str = " ".join(f"{(p[0]-min_x)*scale},{(max_y-p[1])*scale}" for p in rings)
svg.append(f'<polygon points="{points_str}" fill="rgba(255,100,100,0.3)" stroke="cyan" stroke-width="2" />')

for i, p in enumerate(rings[:-1]):
    sx = (p[0] - min_x) * scale
    sy = (max_y - p[1]) * scale
    svg.append(f'<circle cx="{sx}" cy="{sy}" r="4" fill="yellow" />')
    svg.append(f'<text x="{sx+6}" y="{sy+4}" fill="white" font-size="12">{i}</text>')

svg.append('</svg>')

out_path = Path(__file__).resolve().parents[2] / 'audit' / 'benjamin_harrison_hall' / 'harrison_footprint.svg'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    f.write("\n".join(svg))
print(f"Saved {out_path}")
