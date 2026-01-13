import sqlite3

db = sqlite3.connect("jobs.db")
db.execute("""
CREATE TABLE IF NOT EXISTS jobs (
 id TEXT PRIMARY KEY,
 title TEXT,
 company TEXT,
 url TEXT,
 score INTEGER
)
""")

def seen(id):
    return db.execute("SELECT 1 FROM jobs WHERE id=?", (id,)).fetchone()

def save(job):
    db.execute("INSERT INTO jobs VALUES (?,?,?,?,?)",
               (job["id"], job["title"], job["company"], job["url"], job["score"]))
    db.commit()
