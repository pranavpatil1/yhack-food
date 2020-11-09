from flask import Flask, render_template, request, url_for, flash, redirect
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
    id = urllib.parse.unquote(post_id)
    query = "SELECT * FROM rest WHERE name = %s"
    post = conn.execute(query, (id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def formatPhone(phone):
    phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
    return phone

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eat/')
def eat():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM rest').fetchall()
    conn.close()
    posts_parsed = []
    for row in posts:
        d = dict(row.items())
        d['id'] = urllib.parse.quote(d['name'], safe='')
        d['menu'] = ". ".join(d['menu'][:40].split(";")[:-1])
        d['phone'] = formatPhone(str(d['phone']))
        d['tags'] = d['tags'].split(", ")
        d['full_add'] = ", ".join(d['full_add'].split(", ")[:3])
        posts_parsed.append(d)
    return render_template('eat.html', posts=posts_parsed)

@app.route('/restaurant/<post_id>')
def restaurant(post_id):
    post = get_post(post_id)
    menu_items = post['menu'].split(";")
    for i in range(len(menu_items)):
        split = menu_items[i].split(":")
        menu_items[i] = split[0] + "    $" + split[1]
    return render_template('restaurant.html', post=post, menu=menu_items)

@app.route('/chef', methods=('GET', 'POST'))
def chef():
    if request.method == 'POST':
        name = request.form['name']
        phone = str(request.form['phone'])
        menu = request.form['menuItems']
        tags = request.form['tags']
        genre = request.form['genre'] 
        des = request.form['desc']
        full_add = request.form['street'] + ", " + request.form['city'] + ", " + request.form['state'] + ", " + request.form['zip'] + ", USA"

        if not name or not phone:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO rest (name, phone, menu, tags, genre, des, full_add) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                         (name, phone, menu, tags, genre, des, full_add))
            conn.close()
            return redirect(url_for('eat'))
    return render_template('chef.html')
