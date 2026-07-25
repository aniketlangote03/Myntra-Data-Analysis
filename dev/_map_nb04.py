import json
from pathlib import Path

p = Path("notebooks/04_Exploratory_Data_Analysis.ipynb")
data = json.loads(p.read_text(encoding="utf-8"))
lines = []
for i, c in enumerate(data["cells"]):
    t = c["cell_type"][:4]
    text = "".join(c.get("source", [])).replace("\n", " | ")[:100]
    lines.append(f"{i:3d} [{t}]: {text}")

Path("scripts/_nb04_map.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {len(lines)} lines")
