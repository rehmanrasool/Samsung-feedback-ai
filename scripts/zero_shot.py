# scripts/zero_shot.py
from transformers import pipeline
# Initialize once (this will download a model the first time)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

CANDIDATES = ["product issue", "platform/website/app issue", "service center issue", "other"]

def classify_zero_shot(text, threshold=0.6):
    if not text:
        return "other", 0.0
    res = classifier(text, candidate_labels=CANDIDATES, multi_class=False)
    # res: {'labels': [...], 'scores': [...]}
    label = res['labels'][0]
    score = float(res['scores'][0])
    # map text label to our short category keys
    if label.startswith("product"):
        return "product", score
    if label.startswith("platform"):
        return "platform", score
    if label.startswith("service"):
        return "service_center", score
    return "other", score
