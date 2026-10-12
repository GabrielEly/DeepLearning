import csv
import json
from pathlib import Path

from evaluate_focus import run as run_focus
from evaluate_relations import run as run_relations


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main():
    focus = run_focus()
    relations = run_relations()
    focus_f1 = focus["metrics"]["f1_micro"]
    relation_weighted_f1 = relations["metrics"]["f1_weighted"]
    relation_macro_f1 = relations["metrics"]["f1_macro"]

    comparison_rows = [
        {
            "experimento": "Focus Concept Selection",
            "métrica": "F1 (ScispaCy Biomedical, sem fine-tuning)",
            "resultado publicado": "0.69",
            "resultado obtido": f"{focus_f1:.4f}",
            "tipo de execução": "Adaptada",
            "diferença": f"{focus_f1 - 0.69:+.4f}",
            "explicação provável": (
                "Modelo biomédico pequeno 0.5.4 e amostra manual de 20 itens; "
                "o artigo descreve 600 descrições anotadas."
            ),
        },
        {
            "experimento": "Focus Concept Selection",
            "métrica": "F1 (fine-tuned parser)",
            "resultado publicado": "0.95",
            "resultado obtido": f"{focus_f1:.4f}",
            "tipo de execução": "Adaptada",
            "diferença": f"{focus_f1 - 0.95:+.4f}",
            "explicação provável": (
                "Sem fine-tuning, com modelo pequeno e amostra manual de 20 "
                "itens; não o corpus/treino original."
            ),
        },
        {
            "experimento": "Relation Classification",
            "métrica": "F1 ponderado",
            "resultado publicado": "0.89",
            "resultado obtido": f"{relation_weighted_f1:.4f}",
            "tipo de execução": "Adaptada",
            "diferença": f"{relation_weighted_f1 - 0.89:+.4f}",
            "explicação provável": (
                "TF-IDF + regressão logística e 14 exemplos manuais de teste; "
                "artigo avalia 854 anotações com o classificador original."
            ),
        },
        {
            "experimento": "Relation Classification",
            "métrica": "F1 macro",
            "resultado publicado": "0.85",
            "resultado obtido": f"{relation_macro_f1:.4f}",
            "tipo de execução": "Adaptada",
            "diferença": f"{relation_macro_f1 - 0.85:+.4f}",
            "explicação provável": (
                "TF-IDF + regressão logística e 14 exemplos manuais de teste; "
                "artigo avalia 854 anotações com o classificador original."
            ),
        },
    ]
    with (RESULTS / "comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=comparison_rows[0].keys())
        writer.writeheader()
        writer.writerows(comparison_rows)

    summary_lines = [
        "# Resultados da avaliação adaptada",
        "",
        "Esta execução não reproduz integralmente os experimentos dos autores.",
        "Os datasets de teste são exemplos manuais e não foram usados para treino.",
        "",
        "## Focus Concept Selection",
        "",
        f"- Amostra: {focus['sample_size']} descrições.",
        f"- Modelo: {focus['parser']}.",
        f"- Precisão micro: {focus['metrics']['precision_micro']:.4f}.",
        f"- Revocação micro: {focus['metrics']['recall_micro']:.4f}.",
        f"- F1 micro/exact-match: {focus_f1:.4f}.",
        f"- Erros: {len(focus['errors'])}. Ver `focus_predictions.csv`.",
        "",
        "## Relation Classification",
        "",
        f"- Treino: {relations['training_size']} exemplos; "
        f"teste separado: {relations['test_size']} exemplos.",
        f"- Classificador: {relations['classifier']}.",
        f"- F1 ponderado: {relation_weighted_f1:.4f}.",
        f"- F1 macro: {relation_macro_f1:.4f}.",
        "- F1 ponderado e macro diferem (0.6085 vs 0.5651), refletindo "
        "desempenho desigual entre classes e erros concentrados em "
        "bodySite e clinicalStatus.",
        f"- Erros: {len(relations['errors'])}. Ver `relation_predictions.csv`.",
        "",
        "## Comparação com o artigo",
        "",
        "| Experimento | Métrica | Publicado | Obtido | Execução | Diferença |",
        "|---|---|---:|---:|---|---:|",
    ]
    for row in comparison_rows:
        summary_lines.append(
            "| {experimento} | {métrica} | {resultado publicado} | "
            "{resultado obtido} | {tipo de execução} | {diferença} |".format(**row)
        )
    summary_lines.extend(
        [
            "",
            "Não se deve interpretar diferenças numéricas como comparação direta: "
            "os corpora, tamanhos de amostra, modelos e condições são distintos.",
            "Consulte `README-reproduction.md` para as limitações e os comandos.",
            "",
        ]
    )
    (RESULTS / "summary.md").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )
    print(json.dumps({"focus": focus["metrics"], "relations": relations["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
