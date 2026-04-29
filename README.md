# Тематическое моделирование и автоматическое реферирование математических публикаций

Дипломная работа по автоматизированному анализу коллекции математических статей в формате LaTeX. Реализованы методы тематического моделирования (LSI, LDA, BERTopic, BigARTM) и автоматического реферирования на основе LLM (Ollama + Qwen2.5).

---

## Структура репозитория

```
graduation_thesis/
├── src/
│   ├── text_preprocessing.py   # Очистка LaTeX, токенизация, лемматизация
│   └── model_utils.py          # Вспомогательные функции для моделей
│
├── 01_data_preprocessing.ipynb # Загрузка и предобработка корпуса
├── 02_lda.ipynb                # Тематическая модель LDA
├── 03_lsi.ipynb                # Тематическая модель LSI
├── 04_bertopic.ipynb           # Тематическая модель BERTopic
├── 05_bigartm.ipynb            # Тематическая модель BigARTM (отдельное окружение)
├── 06_summarization.ipynb      # Автоматическое реферирование (Ollama + Qwen2.5)
│
├── data_corpus_tex/            # Исходные .tex файлы (не включены в репозиторий)
├── outputs/                    # Результаты: CSV-файлы с корпусом и метриками
├── models/                     # Сохранённые модели
└── figures/                    # Графики и визуализации
```

---

## Описание задачи

Исходные данные - набор математических статей в формате `.tex`.

Задачи:
1. Предобработка текстов с учётом специфики LaTeX и математических формул
2. Построение тематических моделей четырьмя методами с подбором и оптимизацией гиперпараметров
3. Оценка качества моделей по когерентности (c_v, u_mass) и перплексии
4. Генерация кратких аннотаций к статьям с помощью LLM
5. Оценка качества рефератов по метрикам ROUGE и BERTScore

---

## Методы

| Ноутбук | Метод | Особенности |
|---|---|---|
| `02_lda.ipynb` | LDA | Grid search по `num_topics`, `alpha`, `eta`, `passes` |
| `03_lsi.ipynb` | LSI | TF-IDF корпус, подбор числа тем |
| `04_bertopic.ipynb` | BERTopic | Эмбеддинги `multilingual-e5-small`, UMAP + HDBSCAN |
| `05_bigartm.ipynb` | BigARTM | Регуляризаторы SparsePhi, SparseTheta, Decorrelator |
| `06_summarization.ipynb` | Qwen2.5:7b | Локальная LLM через Ollama, оценка ROUGE + BERTScore |

---

## Установка и запуск

### Требования

- Python 3.10+
- [Ollama](https://ollama.com/download) (для ноутбука `06_summarization.ipynb`)
- BigARTM устанавливается в **отдельное виртуальное окружение** (см. ниже)

### Основное окружение (ноутбуки 01–04, 06)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### Окружение для BigARTM (ноутбук 05)

BigARTM на Windows требует отдельной установки. Инструкция:
[https://bigartm.readthedocs.io/en/stable/installation/windows.html](https://bigartm.readthedocs.io/en/stable/installation/windows.html)

```bash
python -m venv venv_bigartm
venv_bigartm\Scripts\activate
pip install bigartm pandas matplotlib seaborn tqdm gensim
```

### Ollama + модель (для ноутбука 06)

```bash
# Скачать и установить Ollama: https://ollama.com/download
ollama pull qwen2.5:7b
ollama serve                   # запустить сервер перед запуском ноутбука
```

---

## Порядок запуска ноутбуков

Ноутбуки запускаются последовательно - каждый следующий читает результаты предыдущего.

```
01_data_preprocessing  →  outputs/clean_corpus.csv
                           models/gensim_dictionary.dict
                           models/gensim_corpus.mm
       ↓
02_lda                 →  models/lda_model_best.model
                           outputs/lda_final_metrics.csv
       ↓
03_lsi                 →  models/lsi_model_best.model
                           outputs/lsi_final_metrics.csv
       ↓
04_bertopic            →  models/bertopic_model/
                           outputs/documents_with_topics.csv
       ↓
05_bigartm             →  models/bigartm_model_best
                           outputs/bigartm_documents_topics.csv
       ↓
06_summarization       →  outputs/summaries.csv
                           outputs/summarization_metrics.csv
```

> `05_bigartm.ipynb` запускается в отдельном окружении `venv_bigartm` и не зависит от порядка с 02–04.

---

## Предобработка текстов

Модуль `src/text_preprocessing.py` реализует полный пайплайн очистки LaTeX:

- Удаление комментариев, математических окружений (`equation`, `align` и др.)
- Удаление служебных окружений (`figure`, `table`, `bibliography` и др.)
- Сохранение содержимого заголовков и подписей (`\section`, `\caption` и др.)
- Удаление всех LaTeX-команд
- Токенизация, лемматизация (pymorphy3), фильтрация стоп-слов
- Фильтрация слишком редких и слишком частых токенов

---

## Результаты (выходные файлы)

| Файл | Содержимое |
|---|---|
| `outputs/clean_corpus.csv` | Очищенный корпус с токенами |
| `outputs/lda_optimization_results.csv` | Результаты grid search LDA |
| `outputs/lsi_optimization_results.csv` | Результаты подбора тем LSI |
| `outputs/bigartm_topics_search.csv` | Подбор числа тем BigARTM |
| `outputs/bigartm_regularization_search.csv` | Подбор регуляризаторов BigARTM |
| `outputs/documents_with_topics.csv` | Документы с метками тем BERTopic |
| `outputs/bigartm_documents_topics.csv` | Документы с метками тем BigARTM |
| `outputs/summaries.csv` | Сгенерированные аннотации + метрики ROUGE/BERTScore |
| `outputs/summarization_metrics.csv` | Детальные метрики по каждому документу |

---

## Зависимости

Основные библиотеки:

```
gensim
bertopic
sentence-transformers
umap-learn
hdbscan
pymorphy3
nltk
rouge-score
bert-score
sentencepiece
pandas
numpy
matplotlib
seaborn
tqdm
requests
scikit-learn
scipy
```

---

