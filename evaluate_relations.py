import csv
import json
from pathlib import Path

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline

from runtime_info import get_runtime_versions


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
TRAIN_DATASET = HERE / "relation_train.csv"
TEST_DATASET = HERE / "relation_test.csv"


def load_rows(path):
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def model_text(row):
    return " ".join((row["context"], row["source"], row["target"]))


def run():
    train_rows = load_rows(TRAIN_DATASET)
    test_rows = load_rows(TEST_DATASET)
    if not train_rows or not test_rows:
        raise ValueError("Both relation training and test sets must be non-empty.")

    train_ids = {row["id"] for row in train_rows}
    test_ids = {row["id"] for row in test_rows}
    if train_ids & test_ids:
        raise ValueError("Relation training and test IDs overlap.")
    train_texts = {model_text(row).casefold() for row in train_rows}
    test_texts = {model_text(row).casefold() for row in test_rows}
    if train_texts & test_texts:
        raise ValueError("Relation training and test examples overlap.")

    train_labels = [row["label"] for row in train_rows]
    test_labels = [row["label"] for row in test_rows]
    labels = sorted(set(train_labels) | set(test_labels))
    missing_training_labels = sorted(set(test_labels) - set(train_labels))
    if missing_training_labels:
        raise ValueError(
            "Test labels absent from training data: "
            + ", ".join(missing_training_labels)
        )

    classifier = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        LogisticRegression(max_iter=2000, random_state=42),
    )
    classifier.fit([model_text(row) for row in train_rows], train_labels)
    predictions = classifier.predict([model_text(row) for row in test_rows])

    weighted = precision_recall_fscore_support(
        test_labels, predictions, labels=labels, average="weighted", zero_division=0
    )
    macro = precision_recall_fscore_support(
        test_labels, predictions, labels=labels, average="macro", zero_division=0
    )
    per_class = classification_report(
        test_labels,
        predictions,
        labels=labels,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    rows = []
    for example, prediction in zip(test_rows, predictions):
        rows.append(
            {
                "id": example["id"],
                "context": example["context"],
                "source": example["source"],
                "target": example["target"],
                "expected_relation": example["label"],
                "predicted_relation": prediction,
                "correct": example["label"] == prediction,
            }
        )
    errors = [row for row in rows if not row["correct"]]
    metrics = {
        "experiment": "Relation Classification",
        "execution_type": "adapted",
        "dataset_origin": "Manually authored examples",
        "training_size": len(train_rows),
        "test_size": len(test_rows),
        "training_labels": sorted(set(train_labels)),
        "test_labels": sorted(set(test_labels)),
        "classifier": "TF-IDF unigram/bigram features with scikit-learn LogisticRegression",
        "runtime": {
            **get_runtime_versions(),
            "scikit_learn_version": sklearn.__version__,
        },
        "metrics": {
            "precision_weighted": float(weighted[0]),
            "recall_weighted": float(weighted[1]),
            "f1_weighted": float(weighted[2]),
            "precision_macro": float(macro[0]),
            "recall_macro": float(macro[1]),
            "f1_macro": float(macro[2]),
        },
        "per_class": per_class,
        "errors": errors,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "relation_predictions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with (RESULTS / "relation_metrics.json").open("w", encoding="utf-8") as output:
        json.dump(metrics, output, indent=2, ensure_ascii=False)
        output.write("\n")

    return metrics


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["metrics"], indent=2))
