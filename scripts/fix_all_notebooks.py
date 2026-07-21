"""Fix notebooks 1-3, 5: text errors, duplicate headers, discount docs, scope intro."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"


def load_nb(name: str) -> dict:
    return json.loads((NOTEBOOKS / name).read_text(encoding="utf-8"))


def save_nb(name: str, nb: dict) -> None:
    path = NOTEBOOKS / name
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    cell["source"] = [text]


def md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [text]}


def fix_double_observation(cell: dict) -> bool:
    text = cell_text(cell)
    if cell["cell_type"] != "markdown" or text.count("### Observation") <= 1:
        return False
    fixed = re.sub(r"(### Observation\s*\n\s*){2,}", "### Observation\n\n", text)
    set_cell_text(cell, fixed)
    return True


def strip_outputs(nb: dict) -> None:
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None


def fix_nb01(nb: dict) -> list[str]:
    changes = []
    for cell in nb["cells"]:
        text = cell_text(cell)
        if "8 features" in text:
            set_cell_text(cell, text.replace("8 features", "7 features"))
            changes.append("Fixed 8 -> 7 features")
        if "52,120 products and 8 features" in text:
            set_cell_text(
                cell,
                text.replace(
                    "52,120 products and 8 features",
                    "52,120 products and 7 features",
                ),
            )
    return changes


def fix_nb02(nb: dict) -> list[str]:
    changes = []
    seen_discount_obs = False
    to_remove = []
    for i, cell in enumerate(nb["cells"]):
        text = cell_text(cell).strip()
        if fix_double_observation(cell):
            changes.append(f"Fixed double observation at cell {i}")
        if (
            cell["cell_type"] == "markdown"
            and text.startswith("### Observation")
            and "4,117 records" in text
        ):
            if seen_discount_obs:
                to_remove.append(i)
                changes.append(f"Removed duplicate discount observation at cell {i}")
            elif "inconsistent scraper format" in text:
                seen_discount_obs = True
                set_cell_text(
                    cell,
                    "### Observation\n\n"
                    "A total of **4,117 records** have discount values outside the expected "
                    "decimal range of 0–1 (i.e., values greater than 1).\n\n"
                    "These values (ranging from 1.1 to 64.0) reflect an **inconsistent scraper "
                    "format** — not standard percentage decimals (0.45) or whole percentages "
                    "that can be reliably converted (e.g., dividing by 100 does not match "
                    "price-derived discounts).\n\n"
                    "This issue will be addressed during the data cleaning phase.",
                )
                changes.append("Updated discount observation with scraper-format explanation")
            else:
                seen_discount_obs = True
                changes.append("Kept discount investigation observation at cell {i}")

        # Remove duplicate discount investigation block (second observation after first)
        if (
            cell["cell_type"] == "markdown"
            and "Before classifying these records as invalid" in text
        ):
            to_remove.append(i)
            changes.append(f"Removed duplicate discount investigation at cell {i}")

    for idx in sorted(to_remove, reverse=True):
        del nb["cells"][idx]
    return changes


def fix_nb03(nb: dict) -> list[str]:
    changes = []
    for i, cell in enumerate(nb["cells"]):
        text = cell_text(cell)
        if fix_double_observation(cell):
            changes.append(f"Fixed double observation at cell {i}")

        # Wrong observation after discount unique values
        if (
            cell["cell_type"] == "markdown"
            and "No products were found with a selling price less than or equal to zero"
            in text
        ):
            prev_idx = i - 1
            if prev_idx >= 0:
                prev = cell_text(nb["cells"][prev_idx])
                if "discount_percent" in prev and "unique" in prev.lower():
                    set_cell_text(
                        cell,
                        "### Observation\n\n"
                        "Most discount values are stored as decimals between 0 and 1 "
                        "(e.g., 0.45 for 45% off).\n\n"
                        "However, some records contain values greater than 1 (up to 64.0), "
                        "indicating an inconsistent scraper format that cannot be reliably "
                        "converted to decimals.\n\n"
                        "These inconsistent records will be removed in the next step.",
                    )
                    changes.append("Fixed wrong observation after discount unique values")

        # Update discount removal markdown
        if (
            cell["cell_type"] == "markdown"
            and "invalid discount percentages greater than 100%" in text
        ):
            set_cell_text(
                cell,
                "## Remove Inconsistent Discount Values\n\n"
                "Some products contain discount values **greater than 1**, outside the expected "
                "decimal range (0–1). These values (1.1–64.0) stem from inconsistent scraper "
                "output and cannot be reliably converted — dividing by 100 does not match "
                "price-derived discounts.\n\n"
                "Records with `discount_percent > 1` are removed to ensure accurate analysis.\n\n"
                "This step improves data quality and prevents misleading business insights.",
            )
            changes.append("Updated discount removal explanation")

        if cell["cell_type"] == "code" and "discount_percent" in text and "<= 1" in text:
            # Clean duplicate comment lines
            cleaned = text.replace(
                "# Remove inconsistent discount values (scraper format outside 0-1 decimal range)\n"
                "# Remove invalid discount percentages\n\n",
                "# Remove inconsistent discount values (scraper format outside 0-1 decimal range)\n\n",
            )
            if cleaned != text:
                set_cell_text(cell, cleaned)
                changes.append("Cleaned duplicate comment in discount filter code")

        # Add post-removal observation if missing
        if (
            cell["cell_type"] == "code"
            and "discount_percent" in text
            and "<= 1" in text
            and i + 1 < len(nb["cells"])
        ):
            nxt = cell_text(nb["cells"][i + 1])
            if "3,546" not in nxt and "Cleaning Step 4" not in nxt:
                obs = md_cell(
                    "### Observation\n\n"
                    "**3,546 records** with `discount_percent > 1` were removed "
                    "(inconsistent scraper format, not reliably convertible). "
                    "The dataset now contains **31,527 clean records** ready for analysis."
                )
                nb["cells"].insert(i + 1, obs)
                changes.append("Added post-discount-removal observation with counts")

    return changes


def fix_nb05(nb: dict) -> list[str]:
    changes = []
    intro = (
        "# Notebook 5 – Advanced Business Insights\n\n"
        "## Scope of This Notebook\n\n"
        "Unlike **Notebook 4 (EDA)**, which explores individual variables and basic "
        "relationships, this notebook **combines multiple metrics** into composite scores "
        "to generate actionable prioritization insights.\n\n"
        "## Business Objective\n\n"
        "Identify high-performing brands, evaluate pricing strategies, measure customer "
        "engagement, and support data-driven merchandising and marketing decisions "
        "using Value Score and Business Performance Score."
    )
    if nb["cells"][0]["cell_type"] == "markdown":
        set_cell_text(nb["cells"][0], intro)
        changes.append("Updated NB5 intro with scope clarification")

    for i, cell in enumerate(nb["cells"]):
        if fix_double_observation(cell):
            changes.append(f"Fixed double observation at cell {i}")
    return changes


def main() -> None:
    all_changes: list[tuple[str, str]] = []

    for name, fixer in [
        ("01_Data_Loading.ipynb", fix_nb01),
        ("02_Data_Quality_Assessment.ipynb", fix_nb02),
        ("03_Data_Cleaning.ipynb", fix_nb03),
        ("05_Advanced_Business_Insights.ipynb", fix_nb05),
    ]:
        nb = load_nb(name)
        changes = fixer(nb)
        strip_outputs(nb)
        save_nb(name, nb)
        for c in changes:
            all_changes.append((name, c))

    print(f"Applied {len(all_changes)} fixes:")
    for name, c in all_changes:
        print(f"  [{name}] {c}")


if __name__ == "__main__":
    main()
