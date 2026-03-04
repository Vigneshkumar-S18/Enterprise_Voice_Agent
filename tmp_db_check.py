import sqlite3, pathlib

db = pathlib.Path('data/voxops.db')
print('DB exists:', db.exists(), 'path=', db)
if not db.exists():
    raise SystemExit(1)
conn = sqlite3.connect(str(db))
cur = conn.cursor()
cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name;")
tables = cur.fetchall()
print('tables:')
for name, ttype in tables:
    print(' -', name, '(', ttype, ')')
for t in ('orders','warehouses','vehicles','routes'):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}:", cur.fetchone()[0])
    except Exception as e:
        print(f"{t}: ERROR ->", e)
conn.close()
