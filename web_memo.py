from flask import Flask, request, redirect, render_template_string
import sqlite3
import os
import datetime

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(__file__), 'memos.db')

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()

def get_memos():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, created_at FROM memos ORDER BY id DESC")
        return cursor.fetchall()

def save_memo(content):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO memos (content, created_at) VALUES (?, ?)", (content, timestamp))
        conn.commit()

def delete_memo(memo_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
        conn.commit()

HTML_TEMPLATE = '''
<!doctype html>
<html>
<head><title>Webメモアプリ（削除機能つき）</title></head>
<body>
  <h1>メモを追加</h1>
  <form method="post">
    <textarea name="content" rows="4" cols="50"></textarea><br>
    <button type="submit">保存</button>
  </form>

  <h2>保存されたメモ</h2>
  {% for memo in memos %}
    <div style="margin-bottom: 1em; border-bottom: 1px solid #ccc; padding-bottom: 1em;">
      <strong>{{ memo[2] }}</strong><br>
      {{ memo[1] }}<br>
      <form method="post" action="/delete/{{ memo[0] }}" style="display:inline;">
        <button type="submit">削除</button>
      </form>
    </div>
  {% endfor %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        if content:
            save_memo(content)
            return redirect("/")  # リロードで再送信を防止
    memos = get_memos()
    return render_template_string(HTML_TEMPLATE, memos=memos)

@app.route("/delete/<int:memo_id>", methods=["POST"])
def delete(memo_id):
    delete_memo(memo_id)
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
