"""Aggressive NB4 consolidation: remove junk, duplicate sections, empty cells."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "notebooks" / "04_Exploratory_Data_Analysis.ipynb"


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def strip_outputs(nb: dict) -> None:
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None


def is_empty_markdown(cell: dict) -> bool:
    return cell["cell_type"] == "markdown" and not cell_text(cell).strip()


def section_d_duplicate(text: str) -> bool:
    """Section D repeats brand rating/engagement analyses already in Section B."""
    markers = [
        "# Business Question 2\n\n## Which brands have the highest average customer ratings?",
        "# Business Question 3\n\n## Which brands receive the highest customer engagement?",
    ]
    return any(text.strip().startswith(m) for m in markers)


def is_junk_block(i: int, cell: dict, cells: list) -> bool:
    text = cell_text(cell)

    # Stray duplicate import header (markdown only, no code follows)
    if (
        cell["cell_type"] == "markdown"
        and text.strip().startswith("# Import Required Libraries")
        and i > 10
    ):
        return True

    # Stray df.head() mid-notebook
    if cell["cell_type"] == "code" and text.strip() in ("df.head()", "df.head()\n"):
        if i > 10:
            return True

    # Duplicate "Display Top 10 Least Expensive" header appearing twice in a row
    if (
        cell["cell_type"] == "markdown"
        and "### Display Top 10 Least Expensive Products" in text
        and i > 0
        and "### Display Top 10 Least Expensive Products"
        in cell_text(cells[i - 1])
    ):
        return True

    return False


def consolidate(nb: dict) -> list[str]:
    changes: list[str] = []
    cells = nb["cells"]

    # Fix wrong record counts
    for i, cell in enumerate(cells):
        text = cell_text(cell)
        if "35,073" in text or "35073" in text:
            new_text = text.replace("35,073", "31,527").replace("35073", "31527")
            cell["source"] = [new_text]
            changes.append(f"Fixed record count at cell {i}")

    # Mark cells for removal
    to_remove: set[int] = set()
    in_section_d = False
    in_dup_block = False
    dup_block_depth = 0

    for i, cell in enumerate(cells):
        text = cell_text(cell)

        if "# Section D" in text:
            in_section_d = True

        if is_empty_markdown(cell):
            to_remove.add(i)
            changes.append(f"Removed empty markdown at cell {i}")
            continue

        if is_junk_block(i, cell, cells):
            to_remove.add(i)
            changes.append(f"Removed junk block at cell {i}")
            continue

        if in_section_d and section_d_duplicate(text):
            in_dup_block = True
            dup_block_depth = 0
            to_remove.add(i)
            changes.append(f"Removed duplicate Section D block start at cell {i}")
            continue

        if in_dup_block:
            # Remove until next top-level BQ or section summary
            first_line = text.strip().split("\n")[0] if text.strip() else ""
            if first_line.startswith("# Business Question") and not section_d_duplicate(text):
                in_dup_block = False
            elif first_line.startswith("# Section"):
                in_dup_block = False
            else:
                to_remove.add(i)
                continue

    # Remove consecutive duplicate Observation markdown (keep last before insight)
    i = 0
    while i < len(cells):
        if i in to_remove:
            i += 1
            continue
        if cells[i]["cell_type"] != "markdown":
            i += 1
            continue
        obs_run = []
        j = i
        while j < len(cells):
            if j in to_remove:
                j += 1
                continue
            t = cell_text(cells[j]).strip()
            if t.startswith("### Observation"):
                obs_run.append(j)
                j += 1
            else:
                break
        if len(obs_run) > 1:
            for idx in obs_run[:-1]:
                to_remove.add(idx)
                changes.append(f"Merged duplicate observations, removed cell {idx}")
        i = j if j > i else i + 1

    new_cells = [c for i, c in enumerate(cells) if i not in to_remove]
    nb["cells"] = new_cells
    changes.append(f"Cells: {len(cells)} -> {len(new_cells)}")
    return changes


def main() -> None:
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    changes = consolidate(nb)
    strip_outputs(nb)
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Applied {len(changes)} changes:")
    for c in changes:
        print(f"  {c}")


if __name__ == "__main__":
    main()
