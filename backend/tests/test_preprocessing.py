from app.ml.preprocessing import clean_text

def test_clean_text_removes_html():
    # "is" survives our custom filter (kept to preserve negation context)
    # "this" and "a" are removed. Verify HTML tags are stripped and meaningful words kept.
    text = "<p>This is a test.</p>"
    cleaned = clean_text(text)
    assert "<p>" not in cleaned
    assert "test" in cleaned

def test_clean_text_preserves_negation():
    text = "I don't like this product."
    cleaned = clean_text(text)
    assert "not" in cleaned
    assert "like" in cleaned

def test_clean_text_removes_stopwords():
    text = "this is a very good item"
    cleaned = clean_text(text)
    assert "very" not in cleaned
    assert "good" in cleaned

def test_clean_text_empty_string():
    assert clean_text("") == ""

def test_clean_text_removes_urls():
    text = "Check http://example.com for details"
    cleaned = clean_text(text)
    assert "http" not in cleaned
    assert "example" not in cleaned
