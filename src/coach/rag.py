"""
RAG local: indexa .md de /kb y recupera pasajes relevantes.
Usa TF-IDF + similitud coseno (ligero y sin dependencias externas pesadas).
"""

import os
import glob
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords


@dataclass
class Doc:
    title: str
    path: str
    text: str


class LocalRAG:
    def __init__(self, kb_dir: str = "kb"):
        self.kb_dir = kb_dir

        # 🧠 Descargar stopwords si no están disponibles
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        # Lista de stopwords en español
        stop_words_es = stopwords.words('spanish')

        # 🧩 Vectorizador TF-IDF optimizado para español
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=stop_words_es,  # Usa stopwords en español
            ngram_range=(1, 2)
        )

        self.docs: List[Doc] = []
        self.matrix = None

    def load_kb(self) -> None:
        """Carga todos los archivos .md de la carpeta KB"""
        paths = glob.glob(os.path.join(self.kb_dir, "*.md"))
        self.docs = []
        for p in paths:
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            title = os.path.splitext(os.path.basename(p))[0]
            self.docs.append(Doc(title=title, path=p, text=txt))
        if not self.docs:
            raise RuntimeError(f"No se encontraron archivos .md en {self.kb_dir}")

    def build(self) -> None:
        """Crea la matriz TF-IDF del corpus"""
        corpus = [d.text for d in self.docs]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Doc, float]]:
        """Recupera los documentos más relevantes según la similitud coseno"""
        if self.matrix is None:
            raise RuntimeError("RAG no indexado. Llama a load_kb() y build().")
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).ravel()
        idx = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in idx]

    @staticmethod
    def format_context(hits: List[Tuple[Doc, float]]) -> str:
        """Formatea los resultados para usarlos como contexto del LLM"""
        lines = []
        for doc, score in hits:
            lines.append(f"# {doc.title} (score={score:.2f})\n{doc.text.strip()}\n")
        return "\n\n".join(lines)
