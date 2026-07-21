"""Strip outputs from all notebooks."""

import json
from pathlib import Path

NOTEBOOKS = Path(__file__).resolve().parent.parent / "notebooks"

for path in NOTEBOOKS.glob("*.ipynb"):
    nb = json.loads(path.read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Stripped outputs: {path.name} ({len(nb['cells'])} cells)")
