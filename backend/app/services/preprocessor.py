import re
import html
import unicodedata
from typing import List, Optional

CONTRACTIONS_DICT = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "i'm": "i am",
    "it's": "it is",
    "he's": "he is",
    "she's": "she is",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
    "where's": "where is",
    "who's": "who is",
    "'ve": " have",
    "'re": " are",
    "'d": " would",
    "'ll": " will",
}

# Optional spaCy integration
_spacy_nlp = None


def get_spacy_nlp():
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except Exception:
            _spacy_nlp = False
    return _spacy_nlp


class TextPreprocessor:
    def __init__(self):
        self.url_pattern = re.compile(r"https?://\S+|www\.\S+")
        self.html_pattern = re.compile(r"<.*?>")
        self.whitespace_pattern = re.compile(r"\s+")
        self.special_char_pattern = re.compile(r"[^a-zA-Z0-9\s.,!?'-]")

    def expand_contractions(self, text: str) -> str:
        """Expand common English contractions."""
        lower_text = text.lower()
        for contraction, expansion in CONTRACTIONS_DICT.items():
            lower_text = lower_text.replace(contraction, expansion)
        return lower_text

    def clean(self, text: Optional[str]) -> str:
        """Clean raw text: remove HTML, URLs, emojis, normalize unicode and whitespace."""
        if not text or not isinstance(text, str):
            return ""

        # Unescape HTML entities & strip tags
        text = html.unescape(text)
        text = self.html_pattern.sub(" ", text)

        # Remove URLs
        text = self.url_pattern.sub(" ", text)

        # Normalize unicode (accents, emojis)
        text = unicodedata.normalize("NFKD", text)

        # Expand contractions
        text = self.expand_contractions(text)

        # Remove strange characters while preserving sentiment punctuation
        text = self.special_char_pattern.sub(" ", text)

        # Collapse excessive whitespace
        text = self.whitespace_pattern.sub(" ", text).strip()

        return text

    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """Tokenize and lemmatize cleaned text."""
        cleaned = self.clean(text)
        if not cleaned:
            return []

        nlp = get_spacy_nlp()
        if nlp:
            try:
                doc = nlp(cleaned)
                tokens = [
                    token.lemma_.lower()
                    for token in doc
                    if not token.is_stop and not token.is_punct and len(token.text) > 1
                ]
                return tokens
            except Exception:
                pass

        # Fast rule-based fallback
        words = re.findall(r"\b[a-zA-Z]{2,}\b", cleaned.lower())
        stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "in", "on", "at", "to", "for", "of", "with", "by", "from", "up",
            "about", "into", "over", "after", "it", "this", "that", "these", "those"
        }
        return [w for w in words if w not in stopwords]


preprocessor = TextPreprocessor()
