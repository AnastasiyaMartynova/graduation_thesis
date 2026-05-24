import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font as tkfont
import threading
import os
import sys
from pathlib import Path

# Настройка путей проекта
SCRIPT_DIR = Path(__file__).resolve().parent

for candidate in [
    SCRIPT_DIR,
    SCRIPT_DIR.parent,
    Path(r"C:\Users\anmrt\Desktop\Useful shit\Диплом\graduation_thesis"),
]:
    if (candidate / "outputs").exists() or (candidate / "models").exists():
        PROJECT_ROOT = candidate
        break
else:
    PROJECT_ROOT = SCRIPT_DIR

OUTPUT_DIR  = PROJECT_ROOT / "outputs"
MODELS_DIR  = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"
SRC_DIR     = PROJECT_ROOT / "src"
DATA_DIR    = PROJECT_ROOT / "data_corpus_tex"

for p in [str(PROJECT_ROOT), str(SRC_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"
AUTHOR_NAME  = "Мартынова Анастасия Сергеевна"

# Цветовая схема
CLR = {
    "bg":        "#1e1e2e",
    "surface":   "#2a2a3e",
    "card":      "#313149",
    "accent":    "#7c6af7",
    "accent2":   "#56b6c2",
    "green":     "#50fa7b",
    "red":       "#ff5555",
    "yellow":    "#f1fa8c",
    "fg":        "#cdd6f4",
    "fg_dim":    "#6c7086",
    "border":    "#45475a",
    "lda":       "#ff79c6",
    "lsi":       "#8be9fd",
    "bert":      "#50fa7b",
    "bigartm":   "#ffb86c",
    "summ":      "#bd93f9",
}

MODEL_COLORS = {
    "LDA":     CLR["lda"],
    "LSI":     CLR["lsi"],
    "BERTopic":CLR["bert"],
    "BigARTM": CLR["bigartm"],
}


#  Вспомогательные функции загрузки
def _load_pandas():
    import pandas as pd
    return pd

def safe_load_csv(path, **kwargs):
    try:
        pd = _load_pandas()
        return pd.read_csv(path, **kwargs)
    except Exception:
        return None

def check_file(path) -> bool:
    return Path(path).exists()


#  Главное окно
class ThesisDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тематическое моделирование математических публикаций")
        self.geometry("1200x780")
        self.minsize(900, 620)
        self.configure(bg=CLR["bg"])

        self._apply_style()
        self._build_ui()
        self.after(200, self._startup_check)

    #Стиль ttk
    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".",
            background=CLR["bg"],
            foreground=CLR["fg"],
            fieldbackground=CLR["surface"],
            troughcolor=CLR["surface"],
            bordercolor=CLR["border"],
            focuscolor=CLR["accent"],
        )
        s.configure("TNotebook",
            background=CLR["bg"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
        )
        s.configure("TNotebook.Tab",
            background=CLR["surface"],
            foreground=CLR["fg_dim"],
            padding=[18, 8],
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        s.map("TNotebook.Tab",
            background=[("selected", CLR["card"])],
            foreground=[("selected", CLR["fg"])],
        )
        s.configure("TFrame", background=CLR["bg"])
        s.configure("Card.TFrame", background=CLR["card"])
        s.configure("TLabel",
            background=CLR["bg"],
            foreground=CLR["fg"],
            font=("Segoe UI", 10),
        )
        s.configure("Title.TLabel",
            background=CLR["bg"],
            foreground=CLR["fg"],
            font=("Segoe UI", 16, "bold"),
        )
        s.configure("Sub.TLabel",
            background=CLR["bg"],
            foreground=CLR["fg_dim"],
            font=("Segoe UI", 9),
        )
        s.configure("Status.TLabel",
            background=CLR["bg"],
            foreground=CLR["fg_dim"],
            font=("Segoe UI", 8),
        )
        s.configure("TButton",
            background=CLR["accent"],
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=[14, 7],
            relief="flat",
        )
        s.map("TButton",
            background=[("active", "#9580ff"), ("disabled", CLR["surface"])],
            foreground=[("disabled", CLR["fg_dim"])],
        )
        s.configure("TCombobox",
            fieldbackground=CLR["surface"],
            background=CLR["surface"],
            foreground=CLR["fg"],
            arrowcolor=CLR["accent"],
            selectbackground=CLR["accent"],
            selectforeground="#ffffff",
        )
        s.configure("Treeview",
            background=CLR["surface"],
            foreground=CLR["fg"],
            fieldbackground=CLR["surface"],
            rowheight=26,
            font=("Segoe UI", 9),
        )
        s.configure("Treeview.Heading",
            background=CLR["card"],
            foreground=CLR["accent"],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        s.map("Treeview",
            background=[("selected", CLR["accent"])],
            foreground=[("selected", "#ffffff")],
        )
        s.configure("TScrollbar",
            background=CLR["surface"],
            troughcolor=CLR["bg"],
            arrowcolor=CLR["fg_dim"],
            borderwidth=0,
        )
        s.configure("TProgressbar",
            background=CLR["accent"],
            troughcolor=CLR["surface"],
            borderwidth=0,
        )
        s.configure("TLabelframe",
            background=CLR["bg"],
            foreground=CLR["fg_dim"],
            bordercolor=CLR["border"],
            font=("Segoe UI", 9),
        )
        s.configure("TLabelframe.Label",
            background=CLR["bg"],
            foreground=CLR["fg_dim"],
            font=("Segoe UI", 9),
        )

    #Главный layout
    def _build_ui(self):
        header = tk.Frame(self, bg=CLR["surface"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header,
            text="Тематическое моделирование и автоматическое реферирование",
            bg=CLR["surface"], fg=CLR["fg"],
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=20, pady=16)

        self.status_var = tk.StringVar(value=AUTHOR_NAME)
        tk.Label(header,
            textvariable=self.status_var,
            bg=CLR["surface"], fg=CLR["fg_dim"],
            font=("Segoe UI", 9),
        ).pack(side="right", padx=20)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._tab_overview()
        self._tab_corpus()
        self._tab_topics()
        self._tab_compare()
        self._tab_summarize()

    # Вкладка: Обзор
    def _tab_overview(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  📋 Обзор  ")

        left  = tk.Frame(f, bg=CLR["bg"])
        right = tk.Frame(f, bg=CLR["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(20,8), pady=20)
        right.pack(side="right", fill="both", expand=True, padx=(8,20), pady=20)

        self._section_label(left, "Методы тематического моделирования")
        methods = [
            ("LDA",     CLR["lda"],     "Latent Dirichlet Allocation",
             "Grid search: кол-во тем, alpha, eta, passes\nМетрики: когерентность c_v, u_mass, перплексия"),
            ("LSI",     CLR["lsi"],     "Latent Semantic Indexing",
             "TF-IDF корпус, подбор числа тем\nМетрика: когерентность c_v"),
            ("BERTopic",CLR["bert"],    "Transformer + HDBSCAN кластеризация",
             "Эмбеддинги multilingual-e5-small, UMAP + HDBSCAN\nАвтоматическое определение числа тем"),
            ("BigARTM", CLR["bigartm"], "Regularized Topic Model",
             "Регуляризаторы SparsePhi, SparseTheta, Decorrelator\nGrid search гиперпараметров"),
        ]
        for name, color, subtitle, desc in methods:
            card = tk.Frame(left, bg=CLR["card"], relief="flat", bd=0)
            card.pack(fill="x", pady=4)
            accent_bar = tk.Frame(card, bg=color, width=4)
            accent_bar.pack(side="left", fill="y")
            info = tk.Frame(card, bg=CLR["card"])
            info.pack(side="left", fill="both", expand=True, padx=12, pady=10)
            tk.Label(info, text=name, bg=CLR["card"],
                     fg=color, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(info, text=subtitle, bg=CLR["card"],
                     fg=CLR["fg_dim"], font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(info, text=desc, bg=CLR["card"],
                     fg=CLR["fg"], font=("Segoe UI", 9),
                     justify="left").pack(anchor="w", pady=(4,0))

        self._section_label(left, "Автоматическое реферирование")
        summ_card = tk.Frame(left, bg=CLR["card"])
        summ_card.pack(fill="x", pady=4)
        bar = tk.Frame(summ_card, bg=CLR["summ"], width=4)
        bar.pack(side="left", fill="y")
        sinfo = tk.Frame(summ_card, bg=CLR["card"])
        sinfo.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        tk.Label(sinfo, text="Ollama + Qwen2.5:7b", bg=CLR["card"],
                 fg=CLR["summ"], font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(sinfo, text="Локальная LLM, контекст — тематический профиль\nОценка: ROUGE-1/2/L, BERTScore",
                 bg=CLR["card"], fg=CLR["fg"], font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(4,0))

        self._section_label(right, "Статус файлов проекта")
        self.file_status_frame = tk.Frame(right, bg=CLR["bg"])
        self.file_status_frame.pack(fill="both", expand=True)

        self._section_label(right, "Пайплайн")
        pipeline_text = (
            "01_data_preprocessing  →  clean_corpus.csv\n"
            "         ↓\n"
            "02_lda                 →  lda_model_best.model\n"
            "03_lsi                 →  lsi_model_best.model\n"
            "04_bertopic            →  bertopic_model/\n"
            "05_bigartm             →  bigartm_model_best\n"
            "         ↓\n"
            "06_summarization       →  summaries.csv"
        )
        pt = tk.Text(right, bg=CLR["surface"], fg=CLR["fg_dim"],
                     font=("Courier New", 9), height=9,
                     bd=0, relief="flat", padx=10, pady=8)
        pt.insert("1.0", pipeline_text)
        pt.configure(state="disabled")
        pt.pack(fill="x", pady=4)

    # Вкладка: Корпус
    def _tab_corpus(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  📂 Корпус  ")

        top = tk.Frame(f, bg=CLR["bg"])
        top.pack(fill="x", padx=20, pady=(16,6))
        self._section_label(top, "Предобработанный корпус")

        self.corpus_stats_frame = tk.Frame(f, bg=CLR["bg"])
        self.corpus_stats_frame.pack(fill="x", padx=20, pady=4)

        tbl_frame = tk.Frame(f, bg=CLR["bg"])
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(4,16))

        cols = ("№", "Файл", "Токенов", "Символов")
        self.corpus_tree = ttk.Treeview(tbl_frame, columns=cols,
                                         show="headings", height=18)
        for c in cols:
            self.corpus_tree.heading(c, text=c)
        self.corpus_tree.column("№",        width=50,  anchor="center")
        self.corpus_tree.column("Файл",     width=420)
        self.corpus_tree.column("Токенов",  width=100, anchor="center")
        self.corpus_tree.column("Символов", width=100, anchor="center")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            command=self.corpus_tree.yview)
        self.corpus_tree.configure(yscrollcommand=vsb.set)
        self.corpus_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # Вкладка 3: Темы
    def _tab_topics(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  🔍 Темы моделей  ")

        ctrl = tk.Frame(f, bg=CLR["bg"])
        ctrl.pack(fill="x", padx=20, pady=(16,6))

        tk.Label(ctrl, text="Модель:", bg=CLR["bg"],
                 fg=CLR["fg_dim"], font=("Segoe UI", 9)).pack(side="left")
        self.model_var = tk.StringVar(value="LDA")
        model_cb = ttk.Combobox(ctrl, textvariable=self.model_var,
                                values=["LDA","LSI","BERTopic","BigARTM"],
                                state="readonly", width=14)
        model_cb.pack(side="left", padx=8)
        model_cb.bind("<<ComboboxSelected>>", lambda _: self._load_topics())

        self.topics_info_var = tk.StringVar(value="")
        tk.Label(ctrl, textvariable=self.topics_info_var,
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(side="left", padx=16)

        pane = tk.Frame(f, bg=CLR["bg"])
        pane.pack(fill="both", expand=True, padx=20, pady=(4,16))

        left = tk.Frame(pane, bg=CLR["bg"])
        left.pack(side="left", fill="y", padx=(0,10))
        tk.Label(left, text="Темы", bg=CLR["bg"],
                 fg=CLR["fg_dim"], font=("Segoe UI", 9)).pack(anchor="w")

        self.topics_list = tk.Listbox(left,
            bg=CLR["surface"], fg=CLR["fg"],
            selectbackground=CLR["accent"], selectforeground="#fff",
            font=("Segoe UI", 10), width=26, activestyle="none",
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground=CLR["border"],
        )
        self.topics_list.pack(fill="y", expand=True)
        self.topics_list.bind("<<ListboxSelect>>", self._on_topic_select)

        right_f = tk.Frame(pane, bg=CLR["bg"])
        right_f.pack(side="left", fill="both", expand=True)

        tk.Label(right_f, text="Ключевые слова темы",
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        self.topic_words_text = scrolledtext.ScrolledText(
            right_f, bg=CLR["surface"], fg=CLR["fg"],
            font=("Segoe UI", 11), wrap="word",
            bd=0, relief="flat", padx=12, pady=10,
            insertbackground=CLR["accent"],
        )
        self.topic_words_text.pack(fill="both", expand=True)
        self._topics_data = {}

    #  Вкладка: Метрики
    def _tab_compare(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  📊 Метрики  ")

        det_f = tk.Frame(f, bg=CLR["bg"])
        det_f.pack(fill="both", expand=True, padx=20, pady=(16,16))

        ctrl2 = tk.Frame(det_f, bg=CLR["bg"])
        ctrl2.pack(fill="x", pady=(0,8))
        tk.Label(ctrl2, text="Детали для:",
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(side="left")
        self.detail_model_var = tk.StringVar(value="LDA")
        det_cb = ttk.Combobox(ctrl2, textvariable=self.detail_model_var,
                              values=["LDA", "LSI", "BERTopic", "BigARTM"],
                              state="readonly", width=12)
        det_cb.pack(side="left", padx=8)
        ttk.Button(ctrl2, text="Показать",
                   command=self._load_detail_metrics).pack(side="left")

        self.detail_tree = ttk.Treeview(det_f, show="headings", height=22)
        det_vsb = ttk.Scrollbar(det_f, orient="vertical",
                                command=self.detail_tree.yview)
        det_hsb = ttk.Scrollbar(det_f, orient="horizontal",
                                command=self.detail_tree.xview)
        self.detail_tree.configure(yscrollcommand=det_vsb.set,
                                   xscrollcommand=det_hsb.set)
        det_vsb.pack(side="right", fill="y")
        det_hsb.pack(side="bottom", fill="x")
        self.detail_tree.pack(fill="both", expand=True)

    # Вкладка: Реферирование
    def _tab_summarize(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  ✍️ Реферирование  ")

        top = tk.Frame(f, bg=CLR["bg"])
        top.pack(fill="x", padx=20, pady=(16,6))
        self._section_label(top, "Автоматическое реферирование (Ollama + Qwen2.5:7b)")

        ctrl = tk.Frame(f, bg=CLR["bg"])
        ctrl.pack(fill="x", padx=20, pady=4)

        tk.Label(ctrl, text="Документ:", bg=CLR["bg"],
                 fg=CLR["fg_dim"], font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.summ_doc_var = tk.StringVar()
        self.summ_doc_cb = ttk.Combobox(ctrl, textvariable=self.summ_doc_var,
                                         state="readonly", width=55)
        self.summ_doc_cb.grid(row=0, column=1, padx=8, sticky="w")

        ttk.Button(ctrl, text="▶  Показать аннотацию",
                   command=self._show_summary).grid(row=1, column=1,
                   sticky="w", pady=(8,0), padx=8)

        self.ollama_status_var = tk.StringVar(value="Ollama: проверяется...")
        tk.Label(ctrl, textvariable=self.ollama_status_var,
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).grid(row=1, column=2, padx=4, sticky="w")

        area = tk.Frame(f, bg=CLR["bg"])
        area.pack(fill="both", expand=True, padx=20, pady=(8,16))

        left_a = tk.Frame(area, bg=CLR["bg"])
        left_a.pack(side="left", fill="both", expand=True, padx=(0,8))

        tk.Label(left_a, text="Тематический профиль документа",
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.profile_text = scrolledtext.ScrolledText(
            left_a, bg=CLR["surface"], fg=CLR["fg"],
            font=("Segoe UI", 9), wrap="word",
            bd=0, relief="flat", padx=10, pady=8, height=14,
        )
        self.profile_text.pack(fill="both", expand=True)

        right_a = tk.Frame(area, bg=CLR["bg"])
        right_a.pack(side="right", fill="both", expand=True)

        tk.Label(right_a, text="Сгенерированная аннотация",
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.summ_text = scrolledtext.ScrolledText(
            right_a, bg=CLR["surface"], fg=CLR["fg"],
            font=("Segoe UI", 10), wrap="word",
            bd=0, relief="flat", padx=10, pady=8, height=8,
        )
        self.summ_text.pack(fill="both", expand=True, pady=(0,6))

        tk.Label(right_a, text="Метрики качества",
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4,0))
        self.metrics_text = scrolledtext.ScrolledText(
            right_a, bg=CLR["surface"], fg=CLR["fg"],
            font=("Courier New", 9), wrap="word",
            bd=0, relief="flat", padx=10, pady=8, height=6,
        )
        self.metrics_text.pack(fill="both", expand=True)

    # Проверка файлов
    def _startup_check(self):
        threading.Thread(target=self._do_startup_check, daemon=True).start()

    def _do_startup_check(self):
        files_to_check = [
            ("clean_corpus.csv",         OUTPUT_DIR / "clean_corpus.csv"),
            ("lda_optimization_results", OUTPUT_DIR / "lda_optimization_results.csv"),
            ("lda_final_metrics",        OUTPUT_DIR / "lda_final_metrics.csv"),
            ("lsi_optimization_results", OUTPUT_DIR / "lsi_optimization_results.csv"),
            ("lsi_final_metrics",        OUTPUT_DIR / "lsi_final_metrics.csv"),
            ("bigartm_topics_search",    OUTPUT_DIR / "bigartm_topics_search.csv"),
            ("bigartm_reg_search",       OUTPUT_DIR / "bigartm_regularization_search.csv"),
            ("documents_with_topics",    OUTPUT_DIR / "documents_with_topics.csv"),
            ("bigartm_documents_topics", OUTPUT_DIR / "bigartm_documents_topics.csv"),
            ("summaries",                OUTPUT_DIR / "summaries_from_topics_selected_11.csv"),
            ("lda_model",                MODELS_DIR / "lda_model_best.model"),
            ("lsi_model",                MODELS_DIR / "lsi_model_best.model"),
            ("bertopic_model",           MODELS_DIR / "bertopic_model"),
            ("bigartm_model",            MODELS_DIR / "bigartm_model_best"),
        ]

        for widget in self.file_status_frame.winfo_children():
            widget.destroy()

        for label, path in files_to_check:
            exists = Path(path).exists()
            row = tk.Frame(self.file_status_frame, bg=CLR["bg"])
            row.pack(fill="x", pady=1)
            icon = "✓" if exists else "✗"
            color = CLR["green"] if exists else CLR["red"]
            tk.Label(row, text=icon, bg=CLR["bg"], fg=color,
                     font=("Segoe UI", 9, "bold"), width=2).pack(side="left")
            tk.Label(row, text=label, bg=CLR["bg"], fg=CLR["fg_dim"],
                     font=("Segoe UI", 9)).pack(side="left", padx=4)

        ollama_ok = self._check_ollama()
        self.after(0, lambda: self.ollama_status_var.set(
            "Ollama: запущена" if ollama_ok else "Ollama: не запущена"
        ))
        self.after(0, lambda: self.status_var.set(AUTHOR_NAME))

        self.after(100, self._load_corpus)
        self.after(400, self._load_topics)
        self.after(600, self._load_summaries_list)

    def _check_ollama(self) -> bool:
        try:
            import requests
            r = requests.get("http://localhost:11434", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    # Загрузка корпуса
    def _load_corpus(self):
        threading.Thread(target=self._do_load_corpus, daemon=True).start()

    def _do_load_corpus(self):
        path = OUTPUT_DIR / "clean_corpus.csv"
        df = safe_load_csv(path)
        if df is None:
            self.after(0, lambda: self.status_var.set(AUTHOR_NAME))
            return

        n_docs = len(df)
        tok_col = "tokens" if "tokens" in df.columns else df.columns[0]
        if tok_col == "tokens":
            df["_tok_count"] = df["tokens"].apply(
                lambda x: len(str(x).split()) if isinstance(x, str) else 0
            )
            total_tokens = df["_tok_count"].sum()
            avg_tokens   = df["_tok_count"].mean()
        else:
            total_tokens = 0
            avg_tokens   = 0

        def update():
            for w in self.corpus_stats_frame.winfo_children():
                w.destroy()
            stats = [
                ("Документов",           str(n_docs)),
                ("Всего токенов",        f"{total_tokens:,}"),
                ("Ср. токенов/документ", f"{avg_tokens:.0f}"),
                ("Столбцов",             str(len(df.columns))),
            ]
            for label, value in stats:
                card = tk.Frame(self.corpus_stats_frame, bg=CLR["card"])
                card.pack(side="left", padx=(0,8), pady=4)
                tk.Label(card, text=value, bg=CLR["card"],
                         fg=CLR["accent"], font=("Segoe UI", 16, "bold"),
                         padx=16, pady=4).pack()
                tk.Label(card, text=label, bg=CLR["card"],
                         fg=CLR["fg_dim"], font=("Segoe UI", 8),
                         padx=16).pack()

            for row in self.corpus_tree.get_children():
                self.corpus_tree.delete(row)

            filename_col = next((c for c in ["filename","path","file"] if c in df.columns), None)
            for i, (_, row) in enumerate(df.head(300).iterrows()):
                fname = str(row[filename_col]) if filename_col else f"doc_{i}"
                fname = Path(fname).name
                tok_count = str(row.get("_tok_count", "—"))
                chars = len(str(row.get("tokens","") or ""))
                self.corpus_tree.insert("", "end", values=(i+1, fname, tok_count, chars))

        self.after(0, update)

    # Загрузка тем
    def _load_topics(self):
        threading.Thread(target=self._do_load_topics, daemon=True).start()

    def _do_load_topics(self):
        model_name = self.model_var.get()
        topics = {}
        try:
            if model_name == "LDA":
                topics = self._load_lda_topics()
            elif model_name == "LSI":
                topics = self._load_lsi_topics()
            elif model_name == "BERTopic":
                topics = self._load_bertopic_topics()
            elif model_name == "BigARTM":
                topics = self._load_bigartm_topics()
        except Exception as e:
            topics = {f"Ошибка: {e}": []}

        self._topics_data = topics

        def update():
            self.topics_list.delete(0, "end")
            color = MODEL_COLORS.get(model_name, CLR["accent"])
            for name in topics:
                self.topics_list.insert("end", name)
            self.topics_list.configure(selectbackground=color)
            self.topics_info_var.set(f"Тем: {len(topics)}")
            if topics:
                self.topics_list.selection_set(0)
                self._on_topic_select(None)

        self.after(0, update)

    def _load_lda_topics(self):
        model_path = MODELS_DIR / "lda_model_best.model"
        if not model_path.exists():
            return {"LDA: файл модели не найден": []}
        try:
            from gensim.models import LdaMulticore, LdaModel
            try:
                model = LdaMulticore.load(str(model_path))
            except Exception:
                model = LdaModel.load(str(model_path))
            topics = {}
            for i in range(model.num_topics):
                words = model.show_topic(i, topn=15)
                topics[f"Тема {i+1}"] = words
            return topics
        except Exception as e:
            return {f"Ошибка загрузки LDA: {e}": []}

    def _load_lsi_topics(self):
        model_path = MODELS_DIR / "lsi_model_best.model"
        if not model_path.exists():
            return {"LSI: файл модели не найден": []}
        try:
            from gensim.models import LsiModel
            model = LsiModel.load(str(model_path))
            topics = {}
            for i in range(model.num_topics):
                words = [(w, float(s)) for w, s in model.show_topic(i, topn=15)]
                topics[f"Тема {i+1}"] = words
            return topics
        except Exception as e:
            return {f"Ошибка загрузки LSI: {e}": []}

    def _load_bertopic_topics(self):
        # BERTopic сохраняет только колонку 'topic' (число) в documents_with_topics.csv. 
        # Слова тем берётся из самой модели через BERTopic.load(). Если модель не загружается - показывается хотя бы список тем с ID.
        model_path = MODELS_DIR / "bertopic_model"

        if model_path.exists():
            try:
                from bertopic import BERTopic
                # embedding_model=False - загрузка только топологии
                model = BERTopic.load(str(model_path), embedding_model=False)
                topic_info = model.get_topic_info()
                topics = {}
                for _, trow in topic_info.iterrows():
                    tid = trow["Topic"]
                    if tid == -1:
                        continue
                    name_label = str(trow.get("Name", f"Тема {tid}"))[:40]
                    raw_words = model.get_topic(tid)
                    if raw_words:
                        words = [(str(w), float(s)) for w, s in raw_words[:15]]
                    else:
                        words = []
                    topics[f"Тема {tid}: {name_label}"] = words
                if topics:
                    return topics
            except Exception as e:
                pass

        # Запасной вариант: читается CSV, показываются темы без слов
        docs_path = OUTPUT_DIR / "documents_with_topics.csv"
        df = safe_load_csv(docs_path)
        if df is not None and "topic" in df.columns:
            topic_ids = sorted(t for t in df["topic"].dropna().unique() if int(t) != -1)
            if topic_ids:
                counts = df[df["topic"] != -1]["topic"].value_counts()
                topics = {}
                for tid in topic_ids:
                    cnt = counts.get(tid, 0)
                    topics[f"Тема {int(tid)}  ({cnt} докум.)"] = []
                return topics

        return {"BERTopic: модель и CSV не найдены": []}

    def _load_bigartm_topics(self):
        # Главный вариант: настоящая Phi-матрица сохранённой BigARTM-модели.
        try:
            topics = self._load_bigartm_topics_from_model()
            if topics:
                return topics
        except Exception as e:
            self._bigartm_last_error = str(e)

        # Надёжный fallback для защиты: реконструкция слов по корпусу и весам тем.
        try:
            topics = self._load_bigartm_topics_from_corpus_weights()
            if topics:
                return topics
        except Exception as e:
            self._bigartm_last_error = str(e)

        msg = "BigARTM: слова тем не найдены"
        if getattr(self, "_bigartm_last_error", ""):
            msg += f" ({self._bigartm_last_error})"
        return {msg: []}

    def _load_bigartm_topics_from_model(self):
        # Пробует прочитать темы из сохранённой BigARTM Phi-матрицы
        import artm

        model_paths = self._bigartm_model_candidates()
        if not model_paths:
            return {}

        dictionary = self._load_bigartm_dictionary(artm)
        num_topics = self._bigartm_guess_num_topics()
        errors = []

        for model_path in model_paths:
            for init_first in (False, True):
                try:
                    model = artm.ARTM(
                        num_topics=num_topics,
                        cache_theta=True,
                        theta_columns_naming="title",
                    )
                    if init_first and dictionary is not None:
                        model.initialize(dictionary=dictionary)
                    model.load(str(model_path), model_name="p_wt")
                    phi = model.get_phi()
                    topics = self._topics_from_phi(phi, limit=15)
                    if topics:
                        return topics
                except Exception as e:
                    errors.append(f"{Path(model_path).name}: {e}")

        if errors:
            self._bigartm_last_error = "; ".join(errors[-3:])
        return {}

    def _bigartm_model_candidates(self):
        # Все вероятные имена файла модели, созданной final_model.save(...)
        base = MODELS_DIR / "bigartm_model_best"
        candidates = [
            base,
            Path(str(base) + ".pwt"),
            Path(str(base) + ".phi"),
            Path(str(base) + ".model"),
            MODELS_DIR / "bigartm_model_best.pwt",
            MODELS_DIR / "bigartm_model_best.phi",
        ]
        existing = []
        for p in candidates:
            if p.exists() and p not in existing:
                existing.append(p)
        return existing

    def _load_bigartm_dictionary(self, artm_module):
        # Загрузка словаря BigARTM, если он есть
        dict_path = MODELS_DIR / "bigartm_dictionary.txt"
        batches_dir = PROJECT_ROOT / "bigartm_batches"

        dictionary = artm_module.Dictionary()
        if dict_path.exists():
            try:
                dictionary.load_text(dictionary_path=str(dict_path))
            except TypeError:
                dictionary.load_text(str(dict_path))
            return dictionary

        if batches_dir.exists():
            dictionary.gather(data_path=str(batches_dir))
            return dictionary

        return None

    def _topics_from_phi(self, phi, limit=15):
        # Преобразует Phi DataFrame в {Тема: [(слово, вес), ...]}
        topics = {}
        for i, col in enumerate(phi.columns, 1):
            try:
                series = phi[col].dropna().sort_values(ascending=False).head(300)
            except Exception:
                continue
            raw_words = [(idx, float(score)) for idx, score in series.items()]
            words = self._filter_topic_words(raw_words, limit=limit)
            if words:
                topics[f"Тема {i}"] = words
        return topics

    def _load_bigartm_topics_from_corpus_weights(self):
        # Реконструирует слова тем без artm: берёт токены из clean_corpus.csv
        # и взвешивает частоты слов по topic_*_weight из bigartm_documents_topics.csv.
        # Это запасной вариант для демонстрации
        from collections import Counter, defaultdict
        import math
        import re

        docs_topics_path = OUTPUT_DIR / "bigartm_documents_topics.csv"
        corpus_path = OUTPUT_DIR / "clean_corpus.csv"
        topics_df = safe_load_csv(docs_topics_path)
        corpus_df = safe_load_csv(corpus_path)

        if topics_df is None or corpus_df is None or "tokens" not in corpus_df.columns:
            return {}

        topic_cols = [
            c for c in topics_df.columns
            if c.startswith("topic_") and c.endswith("_weight")
        ]
        if not topic_cols:
            topic_cols = [c for c in topics_df.columns if c.startswith("topic_")]

        def topic_sort_key(col):
            m = re.search(r"topic_(\d+)", str(col))
            return int(m.group(1)) if m else 10**9

        topic_cols = sorted(topic_cols, key=topic_sort_key)

        # Добавляются tokens к строкам с весами. Обычно порядок документов одинаковый,
        # но если есть filename, сначала делается более безопасный merge.
        data = None
        if "filename" in topics_df.columns and "filename" in corpus_df.columns:
            small_corpus = corpus_df[["filename", "tokens"]].copy()
            data = topics_df.merge(small_corpus, on="filename", how="left")
            if data["tokens"].isna().mean() > 0.5:
                data = None

        if data is None:
            data = topics_df.reset_index(drop=True).copy()
            data["tokens"] = corpus_df.reset_index(drop=True)["tokens"]

        # Если есть только dominant_topic, группируются документы по ней.
        if not topic_cols and "dominant_topic" in data.columns:
            grouped = defaultdict(Counter)
            for _, row in data.iterrows():
                topic_name = str(row.get("dominant_topic", "")).strip()
                if not topic_name:
                    continue
                counts = Counter(self._parse_tokens_cell(row.get("tokens", "")))
                for token, cnt in counts.items():
                    grouped[topic_name][token] += cnt
            topics = {}
            for i, topic_name in enumerate(sorted(grouped), 1):
                raw_words = grouped[topic_name].most_common(300)
                words = self._filter_topic_words(raw_words, limit=15)
                if words:
                    topics[f"Тема {i}"] = words
            return topics

        if not topic_cols:
            return {}

        weighted_counts = {col: Counter() for col in topic_cols}
        for _, row in data.iterrows():
            tokens = self._parse_tokens_cell(row.get("tokens", ""))
            if not tokens:
                continue
            counts = Counter(tokens)
            for col in topic_cols:
                try:
                    weight = float(row.get(col, 0.0))
                except Exception:
                    weight = 0.0
                if not math.isfinite(weight) or weight <= 0:
                    continue
                for token, cnt in counts.items():
                    weighted_counts[col][token] += cnt * weight

        topics = {}
        for i, col in enumerate(topic_cols, 1):
            raw_words = weighted_counts[col].most_common(300)
            words = self._filter_topic_words(raw_words, limit=15)
            if words:
                topics[f"Тема {i}"] = words

        return topics

    def _parse_tokens_cell(self, value):
        # Парсит поле tokens из CSV: строка через пробел или Python-list
        import ast

        if value is None:
            return []
        if isinstance(value, list):
            return [str(x) for x in value]

        text = str(value).strip()
        if not text or text.lower() in {"nan", "none"}:
            return []

        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass

        return text.split()

    def _normalize_topic_token(self, token):
        # Достаёт чистый текст токена из индекса Phi BigARTM
        if isinstance(token, tuple) and token:
            token = token[-1]
        text = str(token).strip()

        # На случай строкового представления MultiIndex: "('@default_class', 'word')".
        if text.startswith("(") and "," in text:
            part = text.split(",")[-1]
            text = part.strip(" )'\"")

        text = text.strip().strip("'\"`“”«»()[]{}")
        if text.startswith("@") and " " in text:
            text = text.split()[-1]
        return text.strip()

    def _is_good_topic_token(self, token):
        # Отсекает даты, id статей, имена файлов и технический мусор
        import re

        token = self._normalize_topic_token(token)
        low = token.lower()
        if not low or low in {"nan", "none", "null", "doc", "document", "topic"}:
            return False
        if len(low) < 3 or len(low) > 40:
            return False
        if low.endswith((".tex", ".pdf", ".txt", ".csv", ".bib", ".sty")):
            return False
        if any(ch.isdigit() for ch in low):
            return False
        if "_" in low or "/" in low or "\\" in low:
            return False
        if re.fullmatch(r"[a-zа-яё]{1,2}", low):
            return False
        if re.search(r"[=+*^$#@~:;<>|]", low):
            return False

        letters = re.findall(r"[a-zа-яё]", low, flags=re.IGNORECASE)
        if len(letters) < 3:
            return False
        if len(letters) / max(len(low), 1) < 0.65:
            return False

        return True

    def _filter_topic_words(self, raw_words, limit=15):
        # Нормализует и фильтрует список (token, score)
        result = []
        seen = set()
        for token, score in raw_words:
            word = self._normalize_topic_token(token)
            key = word.lower()
            if key in seen:
                continue
            if not self._is_good_topic_token(word):
                continue
            seen.add(key)
            try:
                score = float(score)
            except Exception:
                score = 0.0
            result.append((word, score))
            if len(result) >= limit:
                break
        return result

    def _bigartm_guess_num_topics(self) -> int:
        # Определяются num_topics из CSV с результатами поиска или из documents_topics
        # Из bigartm_final_metrics.csv
        for fp in [OUTPUT_DIR / "bigartm_final_metrics.csv",
                   OUTPUT_DIR / "bigartm_regularization_search.csv"]:
            df = safe_load_csv(fp)
            if df is not None and "num_topics" in df.columns:
                try:
                    best = df.sort_values("coherence", ascending=False).iloc[0]
                    return int(best["num_topics"])
                except Exception:
                    pass
        # Из documents_topics - считаются колонки topic_*
        df = safe_load_csv(OUTPUT_DIR / "bigartm_documents_topics.csv")
        if df is not None:
            n = len([c for c in df.columns if c.startswith("topic_")])
            if n > 0:
                return n
        return 10  # fallback

    def _on_topic_select(self, event):
        sel = self.topics_list.curselection()
        if not sel:
            return
        name  = self.topics_list.get(sel[0])
        words = self._topics_data.get(name, [])
        model_name = self.model_var.get()
        color = MODEL_COLORS.get(model_name, CLR["accent"])

        self.topic_words_text.configure(state="normal")
        self.topic_words_text.delete("1.0", "end")
        self.topic_words_text.configure(fg=color)

        if not words:
            self.topic_words_text.insert("end",
                f"{name}\n\nСлова недоступны — модель не загружена или тема пуста.")
        else:
            self.topic_words_text.insert("end", f"{name}\n\n")
            max_score = max(abs(s) for _, s in words) or 1.0
            for rank, (word, score) in enumerate(words, 1):
                bar_len = max(1, int(abs(score) / max_score * 30))
                bar = "█" * bar_len
                self.topic_words_text.insert(
                    "end", f"  {rank:2d}.  {word:<22s}  {score:+.4f}  {bar}\n"
                )
        self.topic_words_text.configure(state="disabled")

    #  Детальные метрики
    def _load_detail_metrics(self):
        threading.Thread(target=self._do_load_detail_metrics, daemon=True).start()

    def _do_load_detail_metrics(self):
        model_name = self.detail_model_var.get()

        file_map = {
            "LDA": [
                OUTPUT_DIR / "lda_optimization_results.csv",
                OUTPUT_DIR / "lda_final_metrics.csv",
            ],
            "LSI": [
                OUTPUT_DIR / "lsi_optimization_results.csv",
                OUTPUT_DIR / "lsi_final_metrics.csv",
            ],
            "BERTopic": [
                OUTPUT_DIR / "documents_with_topics.csv",
            ],
            "BigARTM": [
                OUTPUT_DIR / "bigartm_regularization_search.csv",
                OUTPUT_DIR / "bigartm_topics_search.csv",
                OUTPUT_DIR / "bigartm_final_metrics.csv",
            ],
        }

        df = None
        for fp in file_map.get(model_name, []):
            df = safe_load_csv(fp)
            if df is not None:
                break

        if model_name == "BERTopic" and df is not None and "topic" in df.columns:
            pd = _load_pandas()
            grp = df.groupby("topic").size().reset_index(name="count")
            grp = grp[grp["topic"] != -1].sort_values("count", ascending=False)
            grp.columns = ["topic_id", "документов"]
            df = grp

        def update():
            self.detail_tree.delete(*self.detail_tree.get_children())
            if df is None:
                return

            cols = list(df.columns)
            self.detail_tree["columns"] = cols
            self.detail_tree["show"] = "headings"
            for c in cols:
                self.detail_tree.heading(c, text=c)
                self.detail_tree.column(c, width=130, anchor="center")

            sort_col = "coherence" if "coherence" in cols else cols[0]
            try:
                sorted_df = df.sort_values(sort_col, ascending=False) \
                    if sort_col in df.columns else df
            except Exception:
                sorted_df = df

            for _, row in sorted_df.head(200).iterrows():
                vals = []
                for c in cols:
                    v = row[c]
                    vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
                self.detail_tree.insert("", "end", values=vals)

        self.after(0, update)

    #  Реферирование
    def _load_summaries_list(self):
        threading.Thread(target=self._do_load_summaries_list, daemon=True).start()

    def _do_load_summaries_list(self):
        candidates = [
            OUTPUT_DIR / "summaries_from_topics_selected_11.csv",
            OUTPUT_DIR / "summaries_from_topics_without_abstract_10.csv",
            OUTPUT_DIR / "summaries.csv",
        ]
        self._summaries_df = None
        for fp in candidates:
            df = safe_load_csv(fp)
            if df is not None and "generated_summary" in df.columns:
                self._summaries_df = df
                break

        # Метрики ROUGE/BERTScore сохраняются в summary_from_topics_with_abstract_metrics.csv
        metrics_fp = OUTPUT_DIR / "summary_from_topics_with_abstract_metrics.csv"
        metrics_df = safe_load_csv(metrics_fp)
        if metrics_df is not None and self._summaries_df is not None:
            metric_cols = [c for c in metrics_df.columns
                           if any(k in c for k in ["rouge", "bertscore"])]
            if metric_cols and "filename" in metrics_df.columns:
                try:
                    pd = _load_pandas()
                    # Подтягиваются метрики к строке polieces.tex
                    merge_cols = ["filename"] + metric_cols
                    merged = self._summaries_df.merge(
                        metrics_df[merge_cols],
                        on="filename",
                        how="left",
                        suffixes=("", "_metric"),
                    )
                    # Для колонок, которых не было в основном файле, взять из метрик
                    for col in metric_cols:
                        if col not in self._summaries_df.columns:
                            self._summaries_df[col] = merged[col]
                        else:
                            # Если в основном NaN - заполняется из метрик
                            mask = self._summaries_df[col].isna()
                            self._summaries_df.loc[mask, col] = merged.loc[mask, col]
                except Exception:
                    pass

        def update():
            if self._summaries_df is None:
                self.summ_doc_cb["values"] = ["Файл summaries не найден"]
                return
            df = self._summaries_df
            fname_col = next((c for c in ["filename","title","file"] if c in df.columns), None)
            if fname_col:
                items = [
                    f"{i+1}. {Path(str(r[fname_col])).name}" if fname_col == "filename"
                    else f"{i+1}. {str(r[fname_col])[:60]}"
                    for i, (_, r) in enumerate(df.iterrows())
                ]
            else:
                items = [f"Документ {i+1}" for i in range(len(df))]
            self.summ_doc_cb["values"] = items
            if items:
                self.summ_doc_var.set(items[0])

        self.after(0, update)

    def _show_summary(self):
        if not hasattr(self, "_summaries_df") or self._summaries_df is None:
            messagebox.showinfo("Нет данных", "Данные ещё загружаются.")
            return
        sel = self.summ_doc_var.get()
        try:
            idx = int(sel.split(".")[0]) - 1
        except Exception:
            idx = 0
        df = self._summaries_df
        if idx < 0 or idx >= len(df):
            return
        row = df.iloc[idx]

        # Профиль
        self.profile_text.configure(state="normal")
        self.profile_text.delete("1.0", "end")
        profile = str(row.get("topic_profile",
                    row.get("document_topics",
                    row.get("tokens", ""))))[:4000]
        meta = ""
        if "title" in row and str(row.get("title","")).strip():
            meta += f"📄 {row['title']}\n"
        if "author" in row and str(row.get("author","")).strip():
            meta += f"👤 {row['author']}\n"
        if "filename" in row:
            meta += f"📁 {row['filename']}\n"
        self.profile_text.insert("end", meta + "\n" + profile)
        self.profile_text.configure(state="disabled")

        # Аннотация
        self.summ_text.configure(state="normal")
        self.summ_text.delete("1.0", "end")
        summary = str(row.get("generated_summary", "— нет аннотации —"))
        self.summ_text.insert("end", summary)
        self.summ_text.configure(state="disabled")

        # Метрики качества
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", "end")

        metric_keys = [
            ("rouge1_f",           "ROUGE-1 F1"),
            ("rouge1_p",           "ROUGE-1 Precision"),
            ("rouge1_r",           "ROUGE-1 Recall"),
            ("rouge2_f",           "ROUGE-2 F1"),
            ("rouge2_p",           "ROUGE-2 Precision"),
            ("rouge2_r",           "ROUGE-2 Recall"),
            ("rougeL_f",           "ROUGE-L F1"),
            ("rougeL_p",           "ROUGE-L Precision"),
            ("rougeL_r",           "ROUGE-L Recall"),
            ("bertscore_f1",       "BERTScore F1"),
            ("bertscore_p",        "BERTScore Precision"),
            ("bertscore_r",        "BERTScore Recall"),
            ("generation_seconds", "Время генерации, с"),
        ]

        lines = []
        for key, label in metric_keys:
            val = row.get(key, None)
            if val is None:
                continue
            val_str = str(val)
            if val_str in ("", "nan", "None", "NaN"):
                continue
            try:
                lines.append(f"  {label:<28s}: {float(val_str):.4f}")
            except Exception:
                lines.append(f"  {label:<28s}: {val_str}")

        if lines:
            self.metrics_text.insert("end", "\n".join(lines))
        else:
            # Авторский abstract если есть
            abstract = str(row.get("abstract", "")).strip()
            if abstract and abstract.lower() not in ("nan", "none", ""):
                self.metrics_text.insert("end",
                    "Авторский abstract:\n\n" + abstract[:1000])
            else:
                self.metrics_text.insert("end",
                    "Метрики не рассчитаны для этого документа\n"
                    "(авторский abstract отсутствует).")
        self.metrics_text.configure(state="disabled")

    # Утилиты
    def _section_label(self, parent, text):
        tk.Label(parent, text=text,
                 bg=CLR["bg"], fg=CLR["fg_dim"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8,4))


# Точка входа
if __name__ == "__main__":
    app = ThesisDemo()
    app.mainloop()
