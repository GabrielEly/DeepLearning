# Reprodução simplificada

Este diretório contém uma avaliação parcial e explicitamente adaptada do artigo
de Peterson, Jiang e Liu (2020).

## Inspeção do código do artigo

- `focus/train_parser.py` treina o parser de dependências e requer um
  `training_data.json` que não está incluído. O modelo fine-tuned salvo em
  `data/dep_parse` também não está presente.
- O script de treino importa `spacy.gold.GoldParse` e carrega `en_core_sci_md` e `en_core_sci_lg`.
- `api.py` seleciona o token com dependência `ROOT` como foco. A chamada original
  do parser também usa MetaMap; a reprodução aqui aplica diretamente o mesmo
  critério de raiz ao modelo spaCy, sem invocar MetaMap.
- `rel_models/rel_classifier_clinicalbert.py` implementa o classificador neural
  original. `predict.py` depende de pesos em `models/`, embeddings cui2vec e um
  servidor bert-as-service. `data_handler.py` requer a distribuição SNOMED CT,
  UMLS e MetaMap. Esses pesos, dados e serviços não estão incluídos.
- `data_handler_custom.py` é apenas um modelo de adaptador sem dados.
- Não foram encontrados conjuntos originais de treino, validação ou teste, nem
  arquivos de dependências do projeto. O README original descreve treinamento
  com Snorkel, modelos spaCy, SNOMED CT, UMLS, MetaMap, BERT e cui2vec.

## Ambiente para reprodução de testes

O ambiente utilizado foi Python 3.9.13, isolado em `reproduction\.venv`.
As versões diretas estão fixadas em `requirements-reproduction.txt`. O modelo
biomédico `en_core_sci_sm` 0.5.4 foi escolhido por ser mais leve.

No PowerShell, a partir da raiz do repositório:

```powershell
py -3.9 -m venv reproduction\.venv
.\reproduction\.venv\Scripts\python.exe -m pip install -r reproduction\requirements-reproduction.txt
.\reproduction\.venv\Scripts\python.exe --version
.\reproduction\.venv\Scripts\python.exe -m pip --version
.\reproduction\.venv\Scripts\python.exe -m pip freeze
```

O ambiente desta execução usa Python 3.9.13, pip 22.0.4, spaCy 3.7.5,
scikit-learn 1.6.1 e `en_core_sci_sm` 0.5.4. As dependências diretas e
transitivas instaladas estão fixadas em `requirements-reproduction.txt`.

## Dados e experimentos

Os dados são pequenos exemplos escritos manualmente para esta avaliação, não
são dados clínicos de pacientes.

- `focus_test.csv`: descrições; todas são apenas avaliação e não são usadas
  para treinar ou ajustar o parser.
- `relation_train.csv`: exemplos de treino.
- `relation_test.csv`: exemplos independentes (dois por classe). O script
  verifica IDs e textos duplicados e nunca ajusta o classificador com o teste.

Para executar os experimentos a partir da raiz do projeto:

```powershell
.\reproduction\.venv\Scripts\python.exe .\reproduction\run_reproduction.py
```

Ou execute individualmente:

```powershell
.\reproduction\.venv\Scripts\python.exe .\reproduction\evaluate_focus.py
.\reproduction\.venv\Scripts\python.exe .\reproduction\evaluate_relations.py
```

O experimento de foco aplica o parser de `en_core_sci_sm` 0.5.4 e seleciona seu
token `ROOT`. A comparação usa correspondência exata sem
distinção entre maiúsculas e minúsculas entre a anotação (um token) e a raiz.
Precisão, revocação e F1 micro são reportados; como cada exemplo tem uma única
resposta, essas três métricas coincidem com a acurácia de correspondência exata.

O experimento de relações é uma linha de base adaptada de TF-IDF (unigramas e
bigramas) com regressão logística do scikit-learn, treinada apenas nos
exemplos manuais. São reportados
precisão, revocação e F1 ponderado/macro, além de métricas por classe.

## Resultados e comparação bibliográfica

Os scripts geram em `results/`:

- `focus_predictions.csv` e `relation_predictions.csv`, incluindo os erros;
- `focus_metrics.json` e `relation_metrics.json`, com métricas por classe;
- `comparison.csv` e `summary.md`, com a comparação e as limitações;
- `pip-freeze.txt`, com o inventário exato das distribuições instaladas neste
  ambiente.

Os valores bibliográficos foram conferidos no artigo completo disponível via
Europe PMC (PMCID PMC7701983; DOI
[10.1016/j.jbi.2020.103541](https://doi.org/10.1016/j.jbi.2020.103541)):

- Seleção de foco: F1 0.95 com ScispaCy Biomedical fine-tuned (Tabela 2);
  F1 0.69 com ScispaCy Biomedical sem fine-tuning.
- Classificação de relações: F1 ponderado 0.89 e F1 macro 0.85 (Tabela 5).
- O artigo descreve um corpus de 600 descrições anotadas manualmente; a Tabela 5
  reporta 854 anotações de relação na avaliação do classificador.

Esta reprodução usa apenas alguns exemplos manuais para foco e exemplos manuais
de teste para relações. A fonte dos dados, o tamanho da amostra, o modelo e as
condições diferem.

## Dependências e versões

`requirements-reproduction.txt` fixa as dependências diretas deste caminho
adaptado e as versões transitivas observadas. Para atualizar o inventário do
ambiente após uma nova instalação:

```powershell
.\reproduction\.venv\Scripts\python.exe -m pip freeze > reproduction\results\pip-freeze.txt
```
