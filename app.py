from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eat')
def eat():
    # database code
    posts = [
        {
            'title': 'big tasty snack',
            'created': '11/7'
        },
        {
            'title': 'potato',
            'created': '11/5'
        }
    ]
    return render_template('eat.html', posts=posts)

@app.route('/eat/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('single-eat.html', post=post)
