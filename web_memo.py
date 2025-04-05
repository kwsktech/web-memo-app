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
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Webメモアプリ</title>
  <link rel="manifest" href="/manifest.json">
<style>
  body {
    font-family: sans-serif;
    font-size: 18px;
    padding: 20px;
    background-color: #121212;
    color: #f0f0f0;
  }
  textarea {
    width: 100%;
    font-size: 18px;
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #333;
    border-radius: 5px;
    padding: 10px;
  }
  button {
    font-size: 16px;
    padding: 8px 16px;
    margin-top: 10px;
    border-radius: 6px;
    border: none;
    background-color: #4CAF50;
    color: white;
    cursor: pointer;
  }
  .memo {
    background-color: #1f1f1f;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(255,255,255,0.05);
  }
  .memo:hover {
    transform: scale(1.01);
  }
  .timestamp {
    font-size: 14px;
    color: #aaaaaa;
    margin-bottom: 5px;
  }
</style>


</head>
<body>
  <h1>メモを追加</h1>
  <form method="post">
    <textarea name="content" rows="4"></textarea><br>
    <button type="submit">保存</button>
  </form>

  <h2>保存されたメモ</h2>
  {% for memo in memos %}
    <div class="memo">
      <div class="timestamp">{{ memo[2] }}</div>
      <div>{{ memo[1] }}</div>
      <form method="post" action="/delete/{{ memo[0] }}" style="margin-top: 5px;">
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import send_from_directory

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')
