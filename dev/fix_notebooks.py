"""Clean up notebooks: remove duplicates, reload blocks, and strip outputs."""

import json
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"


def load_nb(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_nb(path: Path, nb: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def strip_outputs(nb: dict) -> None:
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None


def is_import_block(text: str) -> bool:
    return (
        "import pandas as pd" in text
        and "import matplotlib.pyplot as plt" in text
        and "read_csv" not in text
    )


def is_reload_block(text: str) -> bool:
    return 'pd.read_csv("../data/myntra_cleaned.csv")' in text and "df =" in text


def fix_notebook_05(nb: dict) -> list[str]:
    changes = []
    cells = nb["cells"]
    to_remove = []

    # Remove duplicate import + duplicate "Load" header (cells 5-6 after first load header)
    for i, cell in enumerate(cells):
        if i < 4:
            continue
        text = cell_text(cell)
        if cell["cell_type"] == "code" and is_import_block(text):
            to_remove.append(i)
            changes.append(f"Removed duplicate import block at cell {i}")
        if (
            cell["cell_type"] == "markdown"
            and text.strip() == "## Load the Clean Dataset\n\nLoad the cleaned dataset prepared during the data cleaning stage."
            and i > 4
        ):
            # keep first load header only
            prev = cell_text(cells[i - 1]) if i > 0 else ""
            if is_import_block(prev) or "Load the Clean Dataset" in cell_text(cells[i - 2]):
                to_remove.append(i)
                changes.append(f"Removed duplicate load header at cell {i}")

    for idx in sorted(set(to_remove), reverse=True):
        del cells[idx]

    return changes


def fix_notebook_04(nb: dict) -> list[str]:
    changes = []
    cells = nb["cells"]
    to_remove = []

    seen_md = {}
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "markdown":
            continue
        text = cell_text(cell).strip()
        if not text or len(text) < 40:
            continue
        key = text[:200]
        if key in seen_md and "### Observation" in text:
            to_remove.append(i)
            changes.append(f"Removed duplicate observation at cell {i} (dup of {seen_md[key]})")
        else:
            seen_md[key] = i

    # Remove mid-notebook reload sequence: import block followed by read_csv reload
    for i in range(len(cells) - 2):
        t0 = cell_text(cells[i])
        t1 = cell_text(cells[i + 1]) if i + 1 < len(cells) else ""
        if is_import_block(t0):
            # find read_csv within next 3 cells
            for j in range(i + 1, min(i + 4, len(cells))):
                if cells[j]["cell_type"] == "code" and is_reload_block(cell_text(cells[j])):
                    for k in range(i, j + 1):
                        if k not in to_remove:
                            to_remove.append(k)
                    # also remove immediate df.head() verification if present
                    if j + 1 < len(cells):
                        t_next = cell_text(cells[j + 1])
                        if cells[j + 1]["cell_type"] == "code" and t_next.strip() in (
                            "df.head()",
                            'df.head()\n',
                        ):
                            to_remove.append(j + 1)
                    changes.append(f"Removed mid-notebook reload block cells {i}-{j}")
                    break

    for idx in sorted(set(to_remove), reverse=True):
        del cells[idx]

    # Insert summary stats cell after first data load
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "code" and is_reload_block(cell_text(cell)):
            stats_cell = {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Reproducible summary statistics (used across this notebook)\n",
                    "summary = {\n",
                    '    "avg_price": df["price"].mean(),\n',
                    '    "median_price": df["price"].median(),\n',
                    '    "min_price": df["price"].min(),\n',
                    '    "max_price": df["price"].max(),\n',
                    '    "avg_rating": df["ratings"].mean(),\n',
                    '    "avg_discount": df["discount_percent"].mean(),\n',
                    '    "total_products": len(df),\n',
                    "}\n",
                    "print(\"Dataset Summary Statistics:\")\n",
                    "for k, v in summary.items():\n",
                    '    print(f"  {k}: {v:,.2f}" if isinstance(v, float) else f"  {k}: {v:,}")\n',
                ],
                "outputs": [],
                "execution_count": None,
            }
            cells.insert(i + 1, stats_cell)
            changes.append(f"Inserted summary stats cell after load at index {i + 1}")
            break

    return changes


def add_savefig_helpers(nb: dict, prefix: str) -> list[str]:
    """Add plt.savefig after plt.show() calls that lack savefig."""
    changes = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        text = "".join(src)
        if "plt.show()" not in text or "plt.savefig" in text:
            continue
        if "plt.figure" not in text and "sns." not in text and "plt." not in text:
            continue

        chart_name = f"{prefix}_{i:03d}.png"
        new_lines = []
        show_count = 0
        for line in src:
            new_lines.append(line)
            if "plt.show()" in line:
                show_count += 1
                indent = line[: len(line) - len(line.lstrip())]
                save_line = (
                    f'{indent}plt.savefig("../images/{chart_name}", dpi=120, bbox_inches="tight")\n'
                )
                new_lines.insert(-1, save_line)
                changes.append(f"Added savefig for chart in cell {i} -> images/{chart_name}")
        cell["source"] = new_lines
    return changes


def main():
    all_changes = []

    nb05_path = NOTEBOOKS / "05_Advanced_Business_Insights.ipynb"
    nb05 = load_nb(nb05_path)
    all_changes.extend(("05", c) for c in fix_notebook_05(nb05))
    strip_outputs(nb05)
    save_nb(nb05_path, nb05)

    nb04_path = NOTEBOOKS / "04_Exploratory_Data_Analysis.ipynb"
    nb04 = load_nb(nb04_path)
    # Skip legacy cleanup on lean rebuilt NB4 (< 80 cells)
    if len(nb04["cells"]) >= 80:
        all_changes.extend(("04", c) for c in fix_notebook_04(nb04))
        all_changes.extend(("04", c) for c in add_savefig_helpers(nb04, "eda"))
    else:
        all_changes.append(("04", "Skipped legacy cleanup (lean notebook)"))
    strip_outputs(nb04)
    save_nb(nb04_path, nb04)

    nb05 = load_nb(nb05_path)
    all_changes.extend(("05", c) for c in add_savefig_helpers(nb05, "insights"))
    save_nb(nb05_path, nb05)

    print(f"Applied {len(all_changes)} changes:")
    for nb, change in all_changes:
        print(f"  [{nb}] {change}")


if __name__ == "__main__":
    main()
