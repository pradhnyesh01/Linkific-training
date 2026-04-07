import psycopg2
from config import DB_URI

# Read and parse sql_queries.sql
with open("sql_queries.sql", "r") as f:
    raw = f.read()

statements = [s.strip() for s in raw.split(";") if s.strip()]

conn = psycopg2.connect(DB_URI, sslmode="require")
cur = conn.cursor()

for stmt in statements:
    first_word = stmt.split()[0].upper()

    # Skip CREATE TABLE — table already exists via SQLAlchemy
    if first_word == "CREATE":
        print(f"[SKIP] {stmt[:60]}...")
        continue

    try:
        cur.execute(stmt)

        if first_word == "SELECT":
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            print(f"\n[SELECT] {stmt}")
            print("  Columns:", col_names)
            for row in rows:
                print("  ", row)

        else:
            conn.commit()
            print(f"[{first_word}] {stmt[:80]} — {cur.rowcount} row(s) affected")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {stmt[:60]}\n  {e}")

cur.close()
conn.close()
print("\nDone.")
