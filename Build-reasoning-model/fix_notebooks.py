# automatically repair metadata issues across all notebook

import json
import os

def fix_notebook(nb_path):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    changed = False

    for cell in nb.get("cells", []):
        if "outputs" in cell:
            for output in cell["outputs"]:
                # Case 1: Invalid metadata (e.g. contains None or tags)
                if "metadata" in output:
                    if output["metadata"] is None or (
                        isinstance(output["metadata"], dict)
                        and any(v is None for v in output["metadata"].values())
                    ):
                        output["metadata"] = {}
                        changed = True
                # Case 2: Missing metadata entirely (required for display_data)
                elif output.get("output_type") == "display_data":
                    output["metadata"] = {}
                    changed = True

    if changed:
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print(f"Fixed metadata issues in: {nb_path}")
    else:
        print(f"No fixes needed in: {nb_path}")

if __name__ == "__main__":
    folder = "."
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".ipynb"):
                fix_notebook(os.path.join(root, file))
