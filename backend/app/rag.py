from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.hash_embeddings import HashEmbeddingFunction
from app.schemas import Source


SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass
class KnowledgeFile:
    path: Path
    title: str
    category: str
    text: str


class DevOpsRAG:
    def __init__(self):
        config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.embedding_function = HashEmbeddingFunction()
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=150,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        )

    def collection(self):
        return self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection().count()

    def ingest(self) -> int:
        files = self._load_knowledge_files()

        try:
            self.client.delete_collection(config.COLLECTION_NAME)
        except ValueError:
            pass

        collection = self.collection()
        documents: list[str] = []
        metadatas: list[dict] = []
        ids: list[str] = []

        for knowledge_file in files:
            chunks = self.splitter.split_text(knowledge_file.text)
            relative_source = knowledge_file.path.relative_to(config.PROJECT_ROOT).as_posix()

            for index, chunk in enumerate(chunks):
                clean_chunk = chunk.strip()
                if not clean_chunk:
                    continue

                documents.append(clean_chunk)
                metadatas.append(
                    {
                        "title": knowledge_file.title,
                        "source": relative_source,
                        "category": knowledge_file.category,
                        "chunk": index,
                    }
                )
                safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", relative_source)
                ids.append(f"{safe_id}_{index}")

        if documents:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)

        return collection.count()

    def search(self, question: str, top_k: int = 4) -> list[Source]:
        if self.count() == 0:
            self.ingest()

        collection = self.collection()
        result_count = min(top_k, max(collection.count(), 1))
        results = collection.query(
            query_texts=[question],
            n_results=result_count,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        sources: list[Source] = []
        for document, metadata, distance in zip(documents, metadatas, distances):
            score = max(0.0, min(1.0, 1.0 - float(distance)))
            sources.append(
                Source(
                    title=str(metadata.get("title", "Untitled")),
                    source=str(metadata.get("source", "unknown")),
                    category=str(metadata.get("category", "knowledge")),
                    snippet=self._shorten(document),
                    score=round(score, 3),
                )
            )

        return sources

    def build_prompt(self, question: str, sources: list[Source]) -> str:
        context = "\n\n".join(
            f"Source {index}: {source.title} ({source.source})\n{source.snippet}"
            for index, source in enumerate(sources, start=1)
        )

        return f"""You are a DevOps assistant helping an on-call engineer.
Answer only from the provided context. If the context is not enough, say what is missing.
Give practical troubleshooting steps and mention the source titles used.

Context:
{context}

Question:
{question}

Answer:"""

    def fallback_answer(self, question: str, sources: list[Source]) -> str:
        if not sources:
            return "I could not find relevant runbook or incident content. Try re-indexing the documents."

        keywords = self._keywords(question)
        selected_points: list[str] = []

        for source in sources[:3]:
            sentences = re.split(r"(?<=[.!?])\s+", source.snippet)
            best_sentence = self._best_sentence(sentences, keywords)
            if best_sentence:
                selected_points.append(f"- {best_sentence}")

        source_titles = ", ".join(dict.fromkeys(source.title for source in sources[:3]))
        points = "\n".join(selected_points)

        return (
            "I found relevant DevOps knowledge in the indexed documents.\n\n"
            f"{points}\n\n"
            f"Sources used: {source_titles}.\n\n"
            "Tip: Install and run Ollama to turn this retrieved context into a more natural GenAI answer."
        )

    def _load_knowledge_files(self) -> list[KnowledgeFile]:
        if not config.DATA_DIR.exists():
            return []

        files: list[KnowledgeFile] = []
        for path in sorted(config.DATA_DIR.rglob("*")):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue

            files.append(
                KnowledgeFile(
                    path=path,
                    title=self._extract_title(path, text),
                    category=self._category_for(path),
                    text=text,
                )
            )

        return files

    def _extract_title(self, path: Path, text: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").strip()

        return path.stem.replace("-", " ").title()

    def _category_for(self, path: Path) -> str:
        parts = {part.lower() for part in path.parts}
        if "incidents" in parts:
            return "incident"
        if "runbooks" in parts:
            return "runbook"
        return "knowledge"

    def _shorten(self, text: str, limit: int = 1200) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) <= limit:
            return clean
        return clean[:limit].rsplit(" ", 1)[0] + "..."

    def _keywords(self, text: str) -> set[str]:
        stopwords = {
            "what",
            "when",
            "where",
            "which",
            "should",
            "about",
            "with",
            "from",
            "have",
            "that",
            "this",
            "into",
            "does",
            "for",
            "the",
            "and",
            "how",
        }
        return {
            token
            for token in re.findall(r"[a-z0-9][a-z0-9_-]+", text.lower())
            if token not in stopwords and len(token) > 2
        }

    def _best_sentence(self, sentences: list[str], keywords: set[str]) -> str:
        best = ""
        best_score = -1

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_tokens = set(re.findall(r"[a-z0-9][a-z0-9_-]+", sentence.lower()))
            score = len(sentence_tokens.intersection(keywords))
            if score > best_score:
                best = sentence
                best_score = score

        return best
