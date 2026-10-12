# Resultados da avaliação adaptada

Esta execução não reproduz integralmente os experimentos dos autores.
Os datasets de teste são exemplos manuais e não foram usados para treino.

## Focus Concept Selection

- Amostra: 25 descrições.
- Modelo: en_core_sci_sm 0.5.4 (ScispaCy Biomedical; not fine-tuned).
- Precisão micro: 0.7200.
- Revocação micro: 0.7200.
- F1 micro/exact-match: 0.7200.
- Erros: 7. Ver `focus_predictions.csv`.

## Relation Classification

- Treino: 40 exemplos; teste separado: 26 exemplos.
- Classificador: TF-IDF unigram/bigram features with scikit-learn LogisticRegression.
- F1 ponderado: 0.6085.
- F1 macro: 0.5651.
- F1 ponderado e macro diferem (0.6085 vs 0.5651), refletindo desempenho desigual entre classes e erros concentrados em bodySite e clinicalStatus.
- Erros: 9. Ver `relation_predictions.csv`.

## Comparação com o artigo

| Experimento | Métrica | Publicado | Obtido | Execução | Diferença |
|---|---|---:|---:|---|---:|
| Focus Concept Selection | F1 (ScispaCy Biomedical, sem fine-tuning) | 0.69 | 0.7200 | Adaptada | +0.0300 |
| Focus Concept Selection | F1 (fine-tuned parser) | 0.95 | 0.7200 | Adaptada | -0.2300 |
| Relation Classification | F1 ponderado | 0.89 | 0.6085 | Adaptada | -0.2815 |
| Relation Classification | F1 macro | 0.85 | 0.5651 | Adaptada | -0.2849 |

Não se deve interpretar diferenças numéricas como comparação direta: os corpora, tamanhos de amostra, modelos e condições são distintos.
Consulte `README-reproduction.md` para as limitações e os comandos.
