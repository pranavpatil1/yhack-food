from flask import Flask, render_template
from werkzeug.exceptions import abort
import sqlalchemy
import urllib

app = Flask(__name__)

def get_db_connection():
    username = 'postgres'  # DB username
    password = 'mitsucks'  # DB password
    host = '35.236.20.170'  # Public IP address for your instance
    port = '5432'
    database = 'postgres'  # Name of database ('postgres' by default)

    db_url = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
        username, password, host, port, database)

    engine = sqlalchemy.create_engine(db_url)

    conn = engine.connect()
    return conn

def get_post(post_id):
    conn = get_db_connection()
        # urllib.parse.quote('/', safe='')
    post = conn.execute('SELECT * FROM rest WHERE name = ?',
                        (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eat/')
def eat():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM rest LIMIT 5').fetchall()
    conn.close()
    return render_template('eat.html', posts=posts)

@app.route('/restaurant/<string:post_id>')
def restaurant(post_id):
    post = get_post(post_id)
    return render_template('restaurant.html', post=post)
