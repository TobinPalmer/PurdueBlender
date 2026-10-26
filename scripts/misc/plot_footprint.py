import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Coordinates
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

xs = [p[0] for p in rings]
ys = [p[1] for p in rings]

fig, ax = plt.subplots(figsize=(10, 10))
ax.plot(xs, ys, 'b-o', markersize=4)
for i, (x, y) in enumerate(rings[:-1]):
    ax.annotate(str(i), (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title("Official Harrison Hall Footprint (29 vertices)")
plt.savefig("harrison_footprint_analysis.png", dpi=150)
print("Saved harrison_footprint_analysis.png")
