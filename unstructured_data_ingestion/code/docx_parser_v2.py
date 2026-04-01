from docx import Document


def is_title_case_like(text: str) -> bool:
    words = text.split()
    if not words:
        return False

    meaningful_words = [w for w in words if w.isalpha()]
    if not meaningful_words:
        return False

    title_like_count = sum(1 for w in meaningful_words if w[:1].isupper())
    return (title_like_count / len(meaningful_words)) >= 0.7


def paragraph_has_bold(para) -> bool:
    return any(run.bold for run in para.runs)


def score_heading_likelihood(para) -> tuple[int, dict]:
    text = para.text.strip()
    style_name = para.style.name if para.style else ""

    score = 0
    reasons = {}

    if not text:
        return score, {"empty_text": True}

    word_count = len(text.split())
    has_bold = paragraph_has_bold(para)
    lower_style = style_name.lower()

    # Positive signals
    if word_count <= 12:
        score += 2
        reasons["short_text"] = True

    if has_bold:
        score += 2
        reasons["has_bold"] = True

    if not text.endswith((".", ";", ":", ",")):
        score += 1
        reasons["no_sentence_punctuation"] = True

    if is_title_case_like(text):
        score += 1
        reasons["title_case_like"] = True

    if text.isupper() and len(text) <= 40:
        score += 1
        reasons["all_caps_short"] = True

    # Negative signals
    if word_count > 20:
        score -= 3
        reasons["long_text"] = True

    if "list" in lower_style or "bullet" in lower_style:
        score -= 2
        reasons["list_or_bullet_style"] = True

    if "annotation" in lower_style:
        score -= 2
        reasons["annotation_style"] = True

    if text.startswith(("•", "-", "*")):
        score -= 2
        reasons["starts_like_bullet"] = True

    return score, reasons

file_path = "unstructured_data_ingestion\\data\\ZS SOW - Project Diamond - OneCI enhancements.docx"
# file_path = "sample.docx"
doc = Document(file_path)

current_section = None
parsed_paragraphs = []

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue

    style_name = para.style.name if para.style else "No Style"
    score, reasons = score_heading_likelihood(para)

    is_heading_like = score >= 3

    if is_heading_like:
        current_section = text
    
    parsed_paragraphs.append({
        "text": text,
        "style_name": style_name,
        "heading_score": score,
        "is_heading_like": is_heading_like,
        "section_path": [current_section] if current_section else [],
        "reasons": reasons
    })

for item in parsed_paragraphs:
    print(item)