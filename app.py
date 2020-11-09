from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import sqlalchemy
import urllib
from google.cloud import language_v1
import os

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

def formatPhone(phone):
    phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
    return phone

def get_post(post_id):
    conn = get_db_connection()
    id = urllib.parse.unquote(post_id)
    query = "SELECT * FROM rest WHERE name = %s"
    post = conn.execute(query, (id,)).fetchone()
    query = "SELECT comment FROM comments WHERE restaurant = %s"
    comments = conn.execute(query, (id,)).fetchall()
    comment_list = []
    if comments:
        for comment in comments:
            comment_list.append(dict(comment.items())['comment'])
    post_dict = dict(post.items())
    post_dict['comments'] = comment_list
    post_dict['phone'] = formatPhone(str(post_dict['phone']))
    conn.close()
    if post is None:
        abort(404)
    return post_dict

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

@app.route('/restaurant/<post_id>', methods=('GET', 'POST'))
def restaurant(post_id):
    if request.method == 'POST':
        comment = request.form['comment']

        if not comment:
            flash('comment is required!')
        else:
            conn = get_db_connection()
            print (urllib.parse.unquote(post_id), comment)
            conn.execute('INSERT INTO comments (restaurant, comment) VALUES (%s, %s)',
                         (urllib.parse.unquote(post_id), comment))
            
            # compute sentiment score for restaurant
            rest_name = urllib.parse.unquote(post_id)
            sent_score = sample_analyze_sentiment(comment)
            query = "SELECT score FROM rest WHERE name = %s"
            old_score = conn.execute(query, (rest_name,)).fetchone()[0]
            query = "SELECT num_comments FROM rest WHERE name = %s"
            old_num = conn.execute(query, (rest_name,)).fetchone()[0]
            print(old_num, old_score, sent_score)

            query = "UPDATE rest SET score = " + str((sent_score + old_score * old_num)/old_num) + ", num_comments = " + str(old_num + 1) + " WHERE name = %s"
            conn.execute(query, (rest_name,))

            conn.close()
            return redirect(url_for('restaurant', post_id=post_id))
    
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

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="yhack-d85d8882337a.json"
def sample_analyze_sentiment(text_content):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    client = language_v1.LanguageServiceClient()

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})
    # Get overall sentiment of the input document
    return response.document_sentiment.score