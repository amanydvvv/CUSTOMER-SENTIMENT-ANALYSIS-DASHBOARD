import re
from typing import List, Dict, Optional
from backend.app.services.preprocessor import preprocessor, get_spacy_nlp

COMMON_ASPECT_STOPWORDS = {
    "product", "item", "thing", "everything", "nothing", "anything", "something",
    "review", "order", "day", "days", "week", "weeks", "month", "months", "year", "years",
    "time", "way", "lot", "bit", "one", "amazon", "yelp", "store", "place", "guy", "people"
}

SENTIMENT_MODIFIERS = {
    "positive": {"great", "good", "excellent", "amazing", "crisp", "fast", "stunning", "fantastic", "perfection", "love", "super", "flawless", "durable", "smooth", "comfortable", "hydrated", "quiet"},
    "negative": {"bad", "terrible", "awful", "horrible", "poor", "broken", "cheap", "slow", "loud", "cracked", "peeling", "overpriced", "rude", "damaged", "inaccurate", "useless", "stale", "burnt"}
}


class AspectExtractor:
    def __init__(self):
        self._keybert_model = None
        self._keybert_ready = False

    def _init_keybert(self):
        if not self._keybert_ready:
            try:
                from keybert import KeyBERT
                self._keybert_model = KeyBERT()
                self._keybert_ready = True
            except Exception:
                self._keybert_ready = False

    def extract_aspects(self, text: str, overall_sentiment: str = "neutral", top_n: int = 4) -> List[Dict]:
        """
        Extract aspect phrases from review and assign aspect-level sentiment polarity.
        Returns list of dicts: [{'aspect': 'sound quality', 'sentiment': 'positive', 'relevance': 0.88}]
        """
        cleaned = preprocessor.clean(text)
        if not cleaned:
            return []

        # Attempt KeyBERT if ready
        self._init_keybert()
        if self._keybert_ready and self._keybert_model:
            try:
                keywords = self._keybert_model.extract_keywords(
                    cleaned,
                    keyphrase_ngram_range=(1, 3),
                    stop_words="english",
                    use_mmr=True,
                    diversity=0.6,
                    top_n=top_n
                )
                if keywords:
                    results = []
                    for phrase, score in keywords:
                        phrase_clean = phrase.strip().lower()
                        if phrase_clean in COMMON_ASPECT_STOPWORDS or len(phrase_clean) < 3:
                            continue
                        aspect_sentiment = self._determine_aspect_sentiment(phrase_clean, text, overall_sentiment)
                        results.append({
                            "aspect": phrase_clean,
                            "sentiment": aspect_sentiment,
                            "relevance": round(float(score), 3)
                        })
                    if results:
                        return results
            except Exception:
                pass

        # Rule-based & POS Noun Phrase Aspect Extraction Fallback
        return self._extract_aspects_rule_based(cleaned, overall_sentiment, top_n)

    def _extract_aspects_rule_based(self, text: str, overall_sentiment: str, top_n: int) -> List[Dict]:
        nlp = get_spacy_nlp()
        aspect_candidates = []

        if nlp:
            try:
                doc = nlp(text)
                for chunk in doc.noun_chunks:
                    chunk_text = chunk.lemma_.strip().lower()
                    # Filter stop words and single short tokens
                    words = [w for w in chunk_text.split() if w not in COMMON_ASPECT_STOPWORDS and len(w) > 2]
                    if words:
                        candidate = " ".join(words)
                        if len(candidate) > 2 and candidate not in aspect_candidates:
                            aspect_candidates.append(candidate)
            except Exception:
                pass

        # If spacy is not loaded or yielded few candidates, use Regex Noun-Phrase heuristics
        if not aspect_candidates:
            patterns = [
                r"\b(?:sound|audio|battery|screen|camera|build|customer|service|wait|staff|food|crust|sauce|bed|room|app|software|delivery|shipping|price|pricing|keyboard|fan|cable|design|comfort|fit|fabric|setup|connection|wifi|massage|meat|pizza|coffee|pastry)\s+(?:quality|life|resolution|support|staff|temperature|cleanliness|speed|fee|stability|comfort|durability|performance|experience)?\b",
                r"\b[a-zA-Z]{3,15}\s+(?:quality|life|support|speed|performance|comfort|design|durability|reliability|service|experience)\b",
                r"\b(?:great|poor|fast|slow|crisp|loud|easy|terrible|excellent)\s+([a-zA-Z]{3,15}(?:\s+[a-zA-Z]{3,15})?)\b"
            ]
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for m in matches:
                    candidate = m.strip().lower() if isinstance(m, str) else m[0].strip().lower()
                    if candidate and candidate not in COMMON_ASPECT_STOPWORDS and len(candidate) > 2:
                        if candidate not in aspect_candidates:
                            aspect_candidates.append(candidate)

        # Fallback to key meaningful words if still empty
        if not aspect_candidates:
            words = preprocessor.tokenize_and_lemmatize(text)
            aspect_candidates = [w for w in words if w not in COMMON_ASPECT_STOPWORDS][:top_n]

        results = []
        for idx, candidate in enumerate(aspect_candidates[:top_n]):
            aspect_sent = self._determine_aspect_sentiment(candidate, text, overall_sentiment)
            # Relevance decay
            relevance = round(max(0.95 - (idx * 0.12), 0.50), 2)
            results.append({
                "aspect": candidate,
                "sentiment": aspect_sent,
                "relevance": relevance
            })

        return results

    def _determine_aspect_sentiment(self, aspect: str, text: str, default_sentiment: str) -> str:
        """Analyze local context around aspect to assign positive, neutral, or negative polarity."""
        lower_text = text.lower()
        aspect_lower = aspect.lower()
        idx = lower_text.find(aspect_lower)

        if idx != -1:
            # Extract +/- 50 characters context window
            start = max(0, idx - 50)
            end = min(len(lower_text), idx + len(aspect_lower) + 50)
            window = lower_text[start:end]

            pos_matches = sum(1 for word in SENTIMENT_MODIFIERS["positive"] if word in window)
            neg_matches = sum(1 for word in SENTIMENT_MODIFIERS["negative"] if word in window)

            if pos_matches > neg_matches:
                return "positive"
            elif neg_matches > pos_matches:
                return "negative"

        return default_sentiment


aspect_extractor = AspectExtractor()
