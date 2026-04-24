from __future__ import annotations

import os
import re
import glob
import string
from pathlib import Path
from collections import Counter
from typing import Iterable, List, Tuple, Dict, Any

import pandas as pd

try:
    import chardet
except ImportError:
    chardet = None

try:
    import pymorphy3
except ImportError:
    pymorphy3 = None

try:
    from nltk.corpus import stopwords
except ImportError:
    stopwords = None


PROJECT_ROOT = Path(r"C:\Users\anmrt\Desktop\Useful shit\Диплом\graduation_thesis")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path.cwd()

DATA_DIR = PROJECT_ROOT / "data_corpus_tex"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"

for _dir in (OUTPUT_DIR, MODELS_DIR, FIGURES_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


RU_EXTRA_STOPWORDS = {
    # общие местоимения/служебные слова, часто загрязняющие темы
    "который", "которая", "которое", "которые", "некоторый", "некоторая", "некоторое",
    "некоторые", "такой", "такая", "такое", "такие", "данный", "данная", "данное",
    "один", "два", "каждый", "любой", "весь", "всякий", "самый", "являться",
    "иметь", "мочь", "быть", "дать", "получить", "рассмотреть", "показать",
    "следующий", "образ", "случай", "условие", "значение", "величина", "тип",
    "вид", "место", "время", "работа", "результат", "задача", "решение",
    # издательский/метаданный шум
    "переведено", "редакция", "редактор", "оригиналмакет", "отпечатать", "цена",
    "телфакс", "университетский", "унипресс", "лицензия", "редколлегия",
    "учетнизд", "ризограф", "вуз", "вып", "гос", "техн", "унт", "изв",
    "казань", "москва", "санкт", "петербург",
    # слишком общие научные слова — можно убрать/вернуть в зависимости от результата
    "теорема", "доказательство", "лемма", "следствие", "определение", "пример",
    "замечание", "формула", "утверждение", "раздел", "параграф", "таблица",
    "рисунок", "библиография", "литература", "ссылка",
}

EN_EXTRA_STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "were", "are", "was",
    "formula", "russian", "federation", "research", "science", "academy",
    "sciences", "moscow", "control", "federal", "center", "computer",
    "vavilov", "plus", "minus", "informatics", "problem", "problems", "math",
    "mathematical", "mathematics", "equation", "equations", "candidate",
    "amer", "soc", "state", "systems", "theory", "new", "section",
}

LATEX_ENVIRONMENTS_TO_DROP = [
    "figure", "table", "tabular", "thebibliography", "bibliography",
    "tikzpicture", "picture", "lstlisting", "verbatim"
]

MATH_ENVIRONMENTS = [
    "equation", "align", "gather", "multline", "eqnarray", "flalign",
    "alignat", "split", "cases", "matrix", "pmatrix", "bmatrix", "vmatrix"
]


def read_text_file(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1251", "koi8-r", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    if chardet is not None:
        detected = chardet.detect(raw).get("encoding")
        if detected:
            return raw.decode(detected, errors="replace")
    return raw.decode("utf-8", errors="replace")


def load_tex_files(folder_path: Path | str = DATA_DIR) -> pd.DataFrame:
    folder = Path(folder_path)
    rows = []
    for path in sorted(folder.rglob("*.tex")):
        try:
            rows.append({"filename": path.name, "path": str(path), "raw_text": read_text_file(path)})
        except Exception as e:
            print(f"Не удалось прочитать {path}: {e}")
    return pd.DataFrame(rows)


def strip_latex_comments(text: str) -> str:
    # Удаляет комментарии, но не трогает экранированный символ \%
    return re.sub(r"(?<!\\)%.*", " ", text)


def extract_body(text: str) -> str:
    m = re.search(r"\\begin\s*\{document\}(.*?)\\end\s*\{document\}", text, flags=re.S)
    return m.group(1) if m else text


def extract_metadata(tex: str) -> Dict[str, str]:
    def grab(cmd: str) -> str:
        m = re.search(r"\\" + cmd + r"\s*(?:\[[^\]]*\])?\s*\{((?:[^{}]|\{[^{}]*\})*)\}", tex, flags=re.S)
        return clean_latex_to_text(m.group(1)) if m else ""
    abstract = ""
    m_abs = re.search(r"\\begin\s*\{abstract\}(.*?)\\end\s*\{abstract\}", tex, flags=re.S)
    if m_abs:
        abstract = clean_latex_to_text(m_abs.group(1))
    return {"title": grab("title"), "author": grab("author"), "abstract": abstract}


def remove_latex_math(text: str, keep_marker: bool = False) -> str:
    repl = " FORMULA " if keep_marker else " "
    # display math first
    text = re.sub(r"\$\$.*?\$\$", repl, text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", repl, text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)", repl, text, flags=re.S)
    for env in MATH_ENVIRONMENTS:
        text = re.sub(rf"\\begin\s*\{{{env}\*?\}}.*?\\end\s*\{{{env}\*?\}}", repl, text, flags=re.S)
    # inline math
    text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", repl, text, flags=re.S)
    return text


def drop_latex_environments(text: str) -> str:
    for env in LATEX_ENVIRONMENTS_TO_DROP:
        text = re.sub(rf"\\begin\s*\{{{env}\*?\}}.*?\\end\s*\{{{env}\*?\}}", " ", text, flags=re.S)
    return text


def keep_command_argument(text: str) -> str:
    # Сохраняем содержимое смысловых команд: заголовки секций, подписи, выделение.
    commands = [
        "title", "section", "subsection", "subsubsection", "paragraph", "subparagraph",
        "chapter", "part", "caption", "textbf", "textit", "emph", "texttt", "underline"
    ]
    pattern = r"\\(?:" + "|".join(commands) + r")\*?(?:\[[^\]]*\])?\s*\{([^{}]*)\}"
    old = None
    while old != text:
        old = text
        text = re.sub(pattern, r" \1 ", text, flags=re.S)
    return text


def remove_latex_commands(text: str) -> str:
    # Команды со ссылками и служебные команды убираем вместе с аргументами
    text = re.sub(r"\\(?:cite|ref|eqref|label|url|href|includegraphics|bibliographystyle|bibliography)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})+", " ", text)
    # Остальные команды: аргументы вычищаются грубо, но безопасно для BoW
    text = re.sub(r"\\[a-zA-Zа-яА-Я]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*", " ", text)
    # Однобуквенные управляющие последовательности
    text = re.sub(r"\\.", " ", text)
    return text


def clean_latex_to_text(tex: str, keep_formula_marker: bool = False) -> str:
    text = strip_latex_comments(tex)
    text = extract_body(text)
    text = drop_latex_environments(text)
    text = remove_latex_math(text, keep_marker=keep_formula_marker)
    text = keep_command_argument(text)
    text = remove_latex_commands(text)

    # Удаляем остатки TeX-синтаксиса и нормализуем тире/пробелы
    text = text.replace("~", " ")
    text = re.sub(r"[{}_^&#=+*/<>|]", " ", text)
    text = re.sub(r"[–—−]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_stopwords() -> set[str]:
    words = set()
    if stopwords is not None:
        try:
            words |= set(stopwords.words("russian"))
            words |= set(stopwords.words("english"))
        except LookupError:
            pass
    words |= RU_EXTRA_STOPWORDS
    words |= EN_EXTRA_STOPWORDS
    return words


def is_noise_token(token: str) -> bool:
    if len(token) < 3:
        return True
    # удаляем все токены с цифрами: 0040i, 2n1, 182–190, 10pt
    if any(ch.isdigit() for ch in token):
        return True
    # удаляем латиницу/смешанные токены, если для классических моделей нужен русский словарь
    if re.search(r"[a-zA-Z]", token):
        return True
    # оставляем только кириллицу и дефисные кириллические термины
    if not re.fullmatch(r"[а-яё]+(?:-[а-яё]+)?", token):
        return True
    # слишком длинные куски часто являются склейками после удаления TeX
    if len(token) > 30:
        return True
    # односимвольные повторы/мусор
    if len(set(token)) <= 2 and len(token) > 6:
        return True
    return False


def tokenize_and_lemmatize(text: str, stop_words: set[str] | None = None, lemmatize: bool = True) -> List[str]:
    stop_words = stop_words or get_stopwords()
    text = text.lower().replace("ё", "е")
    # Важно: цифры удаляем до токенизации, чтобы не было 182–190 и 0040i.
    text = re.sub(r"\b[\w\-]*\d[\w\-]*\b", " ", text)
    text = re.sub(r"[^\w\s\-а-яА-ЯёЁ]", " ", text)
    raw_tokens = re.findall(r"[а-яё]+(?:-[а-яё]+)?", text)

    morph = pymorphy3.MorphAnalyzer() if lemmatize and pymorphy3 is not None else None
    tokens = []
    for tok in raw_tokens:
        if is_noise_token(tok) or tok in stop_words:
            continue
        lemma = morph.parse(tok)[0].normal_form.replace("ё", "е") if morph else tok
        # Повторная фильтрация после лемматизации — это исправляет «некоторые» -> «некоторый».
        if is_noise_token(lemma) or lemma in stop_words:
            continue
        tokens.append(lemma)
    return tokens


def remove_too_rare_and_too_common(tokens_series: Iterable[List[str]], min_doc_freq: int = 3, max_doc_share: float = 0.55) -> List[List[str]]:
    docs = list(tokens_series)
    n_docs = len(docs)
    df_counter = Counter()
    for tokens in docs:
        df_counter.update(set(tokens))
    allowed = {
        word for word, df in df_counter.items()
        if df >= min_doc_freq and df <= max_doc_share * n_docs
    }
    return [[t for t in tokens if t in allowed] for t in docs]


def build_preprocessed_corpus(
    data_dir: Path | str = DATA_DIR,
    output_dir: Path | str = OUTPUT_DIR,
    min_doc_freq: int = 3,
    max_doc_share: float = 0.55,
    min_tokens_per_doc: int = 30,
) -> pd.DataFrame:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_df = load_tex_files(data_dir)
    rows = []
    stop_words = get_stopwords()

    for _, row in raw_df.iterrows():
        meta = extract_metadata(row["raw_text"])
        cleaned = clean_latex_to_text(row["raw_text"], keep_formula_marker=False)
        tokens = tokenize_and_lemmatize(cleaned, stop_words=stop_words, lemmatize=True)
        rows.append({
            "filename": row["filename"],
            "path": row["path"],
            **meta,
            "cleaned_text": cleaned,
            "tokens": tokens,
            "raw_char_count": len(row["raw_text"]),
            "cleaned_char_count": len(cleaned),
            "token_count_before_df_filter": len(tokens),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"В папке {data_dir} не найдено .tex файлов")

    df["tokens"] = remove_too_rare_and_too_common(df["tokens"], min_doc_freq=min_doc_freq, max_doc_share=max_doc_share)
    df["token_count"] = df["tokens"].apply(len)
    df = df[df["token_count"] >= min_tokens_per_doc].reset_index(drop=True)
    df["text_for_models"] = df["tokens"].apply(" ".join)

    df.to_csv(output_dir / "preprocessed_corpus.csv", index=False, encoding="utf-8")
    return df


def corpus_diagnostics(df: pd.DataFrame, output_dir: Path | str = OUTPUT_DIR) -> pd.DataFrame:
    output_dir = Path(output_dir)
    all_tokens = [t for doc in df["tokens"] for t in doc]
    freq = Counter(all_tokens)
    diag = pd.DataFrame(freq.most_common(), columns=["token", "frequency"])
    diag.to_csv(output_dir / "token_frequencies.csv", index=False, encoding="utf-8")
    summary = pd.DataFrame([{
        "documents": len(df),
        "total_tokens": len(all_tokens),
        "unique_tokens": len(freq),
        "avg_tokens_per_doc": df["token_count"].mean(),
        "median_tokens_per_doc": df["token_count"].median(),
    }])
    summary.to_csv(output_dir / "corpus_summary_statistics.csv", index=False, encoding="utf-8")
    return diag