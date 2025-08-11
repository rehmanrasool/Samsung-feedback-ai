# scripts/classify_rules.py
import re

CATS = {
    "product": [
        r"\bbattery\b", r"\boverheat", r"\bcamera\b", r"\bscreen\b",
        r"\bdisplay\b", r"\bcharging\b", r"\bmic\b", r"\bspeaker\b",
        r"\bnetwork issue\b", r"\bhardware\b", r"\bback cover\b",
    ],
    "platform": [
        r"\b(app|application|update|login|sign in|signup|checkout|cart|payment|wallet|emi|transaction|points|rewards|crash|slow|lag|force close|force-close|error|exception|page not found)\b",
        r"\bwebsite\b", r"\bweb\b", r"\bcheckout\b"
    ],
    "service_center": [
        r"\bservice center\b", r"\bservicecentre\b", r"\brepair\b", r"\btechnician\b",
        r"\bspare part\b", r"\bpart not available\b", r"\bAMC\b", r"\bservice charge\b",
        r"\bstaff\b", r"\brude\b", r"\bbehavior\b"
    ]
}

# compile
PAT = {k: [re.compile(p, re.I) for p in v] for k, v in CATS.items()}

def classify_by_rules(text):
    if not text:
        return None, 0.0
    t = text.lower()
    hits = {}
    for cat, patterns in PAT.items():
        for p in patterns:
            if p.search(t):
                hits.setdefault(cat, 0)
                hits[cat] += 1
    if not hits:
        return None, 0.0
    # pick highest hit count, confidence = normalized hits
    cat = max(hits, key=lambda k: hits[k])
    total = sum(hits.values())
    confidence = min(0.99, 0.4 + 0.6 * (hits[cat]/total))  # heuristic scaling
    return cat, confidence
