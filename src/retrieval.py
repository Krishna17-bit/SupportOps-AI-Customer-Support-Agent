from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

from .data_loader import KnowledgeDoc


@dataclass
class EvidenceHit:
    source_title: str
    quote: str
    score: float


_WORD = re.compile(r"[a-zA-Z0-9_'-]+")


def tokenize(text: str) -> set[str]:
    words = [w.lower() for w in _WORD.findall(text or "")]
    stop = {
        "the", "a", "an", "and", "or", "but", "to", "of", "for", "in", "on", "with", "is", "are", "was", "were", "be",
        "this", "that", "it", "as", "by", "from", "at", "we", "you", "your", "our", "can", "will", "should", "would"
    }
    return {w for w in words if len(w) > 2 and w not in stop}


def chunk_document(doc: KnowledgeDoc, max_chars: int = 1050) -> List[EvidenceHit]:
    raw_parts = re.split(r"\n\s*\n|(?<=\.)\s+(?=[A-Z])", doc.content or "")
    chunks: List[EvidenceHit] = []
    buffer = ""
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if len(buffer) + len(part) < max_chars:
            buffer = (buffer + "\n" + part).strip()
        else:
            if buffer:
                chunks.append(EvidenceHit(doc.title, buffer, 0.0))
            buffer = part[:max_chars]
    if buffer:
        chunks.append(EvidenceHit(doc.title, buffer, 0.0))
    return chunks


def retrieve_evidence(query: str, docs: Iterable[KnowledgeDoc], top_k: int = 4) -> List[EvidenceHit]:
    q_tokens = tokenize(query)
    if not q_tokens:
        return []

    scored: List[EvidenceHit] = []
    for doc in docs:
        for chunk in chunk_document(doc):
            c_tokens = tokenize(chunk.quote)
            if not c_tokens:
                continue
            overlap = len(q_tokens & c_tokens)
            jaccard = overlap / max(len(q_tokens | c_tokens), 1)
            phrase_bonus = 0.0
            q_lower = query.lower()
            c_lower = chunk.quote.lower()
            for phrase in ["refund", "return", "sla", "escalat", "bug", "billing", "privacy", "discount", "delivery", "warranty"]:
                if phrase in q_lower and phrase in c_lower:
                    phrase_bonus += 0.04
            score = min(1.0, jaccard * 4.0 + phrase_bonus)
            if score > 0:
                scored.append(EvidenceHit(chunk.source_title, chunk.quote.strip(), round(score, 3)))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]


def evidence_strength(hits: List[EvidenceHit]) -> str:
    if not hits:
        return "No evidence found"
    best = hits[0].score
    if best >= 0.35:
        return "Strong"
    if best >= 0.18:
        return "Moderate"
    return "Weak"
