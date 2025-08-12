#!/usr/bin/env python3
import json, uuid, datetime, os
import psycopg2
from psycopg2.extras import Json

DB_PARAMS = {
    "dbname": "samsung_feedback",
    "user": "d2c-rahiman.s",   # change if your DB user differs
    "host": "localhost",
    "port": 5432
}

INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "refined_problem_solutions.json")

def load_input(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def upsert_problem(conn, cluster_id, rec):
    cur = conn.cursor()
    now = datetime.datetime.now(datetime.UTC)  # fixed deprecation warning
    idval = str(uuid.uuid4())
    cur.execute("""
    INSERT INTO problem_solutions (
        id, cluster_id, problem_statement, solutions, category, module, issue,
        impact_score, solvability_score, occurrence, source, created_date, modified_date
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (id) DO NOTHING
    """, (
        idval,
        str(cluster_id),
        rec.get("Refined Problem Statement"),
        Json(rec.get("Solutions", [])),
        rec.get("Category"),
        rec.get("Module"),
        rec.get("Issue"),
        int(rec.get("Impact score") or 0),
        int(rec.get("Solvability score") or 0),
        int(rec.get("Occurrence") or 0),
        rec.get("Source", "google.playstore"),
        now,
        now
    ))
    cur.close()

def main():
    data = load_input(INPUT)
    conn = psycopg2.connect(**DB_PARAMS)
    inserted = 0
    for cid, rec in data.items():
        cat = (rec.get("Category") or "").strip().lower()
        if cat == "platform":     # only platform entries
            try:
                upsert_problem(conn, cid, rec)
                inserted += 1
            except Exception as e:
                print(f"Error inserting cluster {cid}", e)
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} platform problem(s) into problem_solutions.")

if __name__ == "__main__":
    main()
