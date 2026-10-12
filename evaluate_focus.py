import csv
import json
from pathlib import Path

import spacy
from sklearn.metrics import classification_report, precision_recall_fscore_support

from runtime_info import get_runtime_versions


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DATASET = HERE / "focus_test.csv"


def run():
    with DATASET.open(newline="", encoding="utf-8") as source:
        examples = list(csv.DictReader(source))

    if not examples:
        raise ValueError("The focus test set is empty.")

    nlp = spacy.load("en_core_sci_sm")
    rows = []
    gold = []
    predicted = []

    for example in examples:
        doc = nlp(example["text"])
        roots = [token for token in doc if token.dep_ == "ROOT"]
        if len(roots) != 1:
            raise ValueError(
                "Expected exactly one dependency root for "
                f"{example['id']}: {len(roots)}"
            )

        expected = example["focus"].strip().casefold()
        actual = roots[0].text.strip().casefold()
        gold.append(expected)
        predicted.append(actual)
        rows.append(
            {
                "id": example["id"],
                "text": example["text"],
                "expected_focus": example["focus"],
                "predicted_root": roots[0].text,
                "correct": expected == actual,
            }
        )

    precision, recall, f1, _ = precision_recall_fscore_support(
        gold, predicted, average="micro", zero_division=0
    )
    labels = sorted(set(gold) | set(predicted))
    per_class = classification_report(
        gold,
        predicted,
        labels=labels,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    errors = [row for row in rows if not row["correct"]]
    metrics = {
        "experiment": "Focus Concept Selection",
        "execution_type": "adapted",
        "dataset_origin": "Manually authored examples; held-out evaluation set",
        "sample_size": len(rows),
        "parser": "en_core_sci_sm 0.5.4 (ScispaCy Biomedical; not fine-tuned)",
        "runtime": {
            **get_runtime_versions(),
            "spacy_version": spacy.__version__,
        },
        "selection_rule": "Select the unique spaCy token whose dependency label is ROOT, matching the root-selection rule in api.py.",
        "matching_rule": "Case-insensitive exact match between the annotated focus token and predicted root token.",
        "metrics": {
            "precision_micro": float(precision),
            "recall_micro": float(recall),
            "f1_micro": float(f1),
        },
        "per_class": per_class,
        "errors": errors,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "focus_predictions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with (RESULTS / "focus_metrics.json").open("w", encoding="utf-8") as output:
        json.dump(metrics, output, indent=2, ensure_ascii=False)
        output.write("\n")

    return metrics


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["metrics"], indent=2))
