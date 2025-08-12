# scripts/process_reviews.py
import json, os, uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from helpers import clean_text, preprocess, now_ts
from classify_rules import classify_by_rules
from zero_shot import classify_zero_shot

# DB connect string - change user if needed
DB_URL = "postgresql+psycopg2://d2c-rahiman.s@localhost/samsung_feedback"
engine = create_engine(DB_URL, client_encoding='utf8')

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

# thresholds
ZERO_SHOT_THRESHOLD = 0.60

def fetch_bad_reviews(limit=None):
    sql = "SELECT id, data FROM bad_reviews"
    if limit:
        sql += " LIMIT :lim"
    with engine.connect() as conn:
        rows = conn.execute(text(sql), {"lim": limit} if limit else {}).fetchall()
    results = []
    for r in rows:
        # r.data is JSONB -> mapped to dict by SQLAlchemy
        results.append({"id": r.id, "data": r.data})
    return results

def upsert_classified(row):
    now = datetime.utcnow()
    sql = """
    INSERT INTO classified_reviews (id, data, source, category, confidence, method, created_date, modified_date)
    VALUES (:id, :data, :source, :category, :confidence, :method, :created, :modified)
    ON CONFLICT (id) DO UPDATE
    SET data = EXCLUDED.data,
        source = EXCLUDED.source,
        category = EXCLUDED.category,
        confidence = EXCLUDED.confidence,
        method = EXCLUDED.method,
        modified_date = EXCLUDED.modified_date
    """
    with engine.connect() as conn:
        conn.execute(text(sql), {
            "id": row["id"],
            "data": json.dumps(row["data"], ensure_ascii=False),
            "source": row["data"].get("source") or "google.playstore",
            "category": row["category"],
            "confidence": float(row["confidence"]),
            "method": row["method"],
            "created": now,
            "modified": now
        })

def main():
    print("Fetching bad reviews from DB...")
    bad_reviews = fetch_bad_reviews()
    print(f"Loaded {len(bad_reviews)} bad reviews")

    classified = []
    uncertain = []

    for r in bad_reviews:
        txt = clean_text(r["data"].get("text") or "")
        # RULES
        cat, conf = classify_by_rules(txt)
        method = None
        if cat is not None:
            method = "rules"
            confidence = conf
        else:
            # zero-shot fallback
            zs_label, zs_score = classify_zero_shot(txt, threshold=ZERO_SHOT_THRESHOLD)
            method = "zero-shot"
            confidence = zs_score
            cat = zs_label

        row = {
            "id": r["id"],
            "data": r["data"],
            "category": cat,
            "confidence": confidence,
            "method": method
        }

        # low-confidence handling
        if method == "zero-shot" and confidence < ZERO_SHOT_THRESHOLD:
            row["method"] = "uncertain"
            uncertain.append(row)
        else:
            upsert_classified(row)
            classified.append(row)



    # export classified and uncertain files
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    out_all = os.path.join(EXPORT_DIR, f"classified_reviews_{ts}.json")
    out_uncertain = os.path.join(EXPORT_DIR, f"classified_uncertain_{ts}.json")
    with open(out_all, "w", encoding="utf-8") as f:
        json.dump(classified, f, indent=2, ensure_ascii=False)
    with open(out_uncertain, "w", encoding="utf-8") as f:
        json.dump(uncertain, f, indent=2, ensure_ascii=False)

#insert_into_classified_reviews(classified_reviews)

    print(f"Classified {len(classified)} reviews (saved to DB).")
    print(f"Marked {len(uncertain)} reviews as uncertain (saved to {out_uncertain}).")
    print(f"Full classified export: {out_all}")







if __name__ == "__main__":
    main()



import psycopg2
from datetime import datetime

def insert_into_classified_reviews(classified_data):
    conn = psycopg2.connect(
        dbname="samsung_feedback",
        user="d2c-rahiman.s",  # e.g. 'd2c-rahiman.s'
        password="",          # if you have one, else keep empty
        host="localhost",
        port=5432
    )
    cur = conn.cursor()

    for review in classified_data:
        cur.execute("""
            INSERT INTO classified_reviews (text, score, review_date, category, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            review['text'],
            review['score'],
            review['date'],
            review['category'],
            review['source'],
            datetime.utcnow()
        ))
    
    conn.commit()
    cur.close()
    conn.close()
