from flask import Flask, render_template
from werkzeug.exceptions import abort

app = Flask(__name__)

# database code
posts = [
    {
        'id': 0,
        'title': 'big tasty snack',
        'created': '11/7'
    },
    {
        'id': 1,
        'title': 'potato',
        'created': '11/5'
    }
]

def get_db_connection():
    #conn = sqlite3.connect('database.db')
    #conn.row_factory = sqlite3.Row
    #return conn
    return None


def get_post(post_id):
    # conn = get_db_connection()
    # post = conn.execute('SELECT * FROM posts WHERE id = ?',
    #                    (post_id,)).fetchone()
    # conn.close()
    post = posts[post_id] if post_id < len(posts) else None
    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eat/')
def eat():
    return render_template('eat.html', posts=posts)

@app.route('/restaurant/<int:post_id>')
def restaurant(post_id):
    post = get_post(post_id)
    return render_template('restaurant.html', post=post)
