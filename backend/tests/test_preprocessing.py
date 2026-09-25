from app.ml.preprocessing import clean_text

def test_clean_text_removes_html():
    text = "<p>This is a test.</p>"
    assert clean_text(text) == "test"

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
