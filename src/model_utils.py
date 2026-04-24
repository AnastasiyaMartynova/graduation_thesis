from pathlib import Path
import ast
import pandas as pd
from gensim import corpora

PROJECT_ROOT = Path(r"C:\Users\anmrt\Desktop\Useful shit\Диплом\graduation_thesis")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path.cwd()
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"
for p in (OUTPUT_DIR, MODELS_DIR, FIGURES_DIR):
    p.mkdir(parents=True, exist_ok=True)

def load_preprocessed():
    df = pd.read_csv(OUTPUT_DIR / "preprocessed_corpus.csv")
    df["tokens"] = df["tokens"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    texts = df["tokens"].tolist()
    dictionary = corpora.Dictionary.load(str(MODELS_DIR / "gensim_dictionary.dict"))
    corpus = corpora.MmCorpus(str(MODELS_DIR / "gensim_corpus.mm"))
    return df, texts, dictionary, corpus

def print_gensim_topics(model, title, num_topics=10, num_words=10):
    print(f"\n{title}")
    for idx, topic in model.show_topics(num_topics=min(num_topics, model.num_topics), num_words=num_words, formatted=False):
        words = " + ".join([f"{word}({weight:.3f})" for word, weight in topic])
        print(f"Тема {idx + 1}: {words}")