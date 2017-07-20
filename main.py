from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:2funky44@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'LINDAN_IS_MY_WOMAN'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    #below should have after allowed_routes- and user not in session
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()

    if 'user' in request.args:
        username = request.args['user']
        owner = User.query.filter_by(username=username).first()
        user_posts = Blog.query.filter_by(owner=owner).all()
        return render_template('single_user.html', user_posts=user_posts)

    return render_template('index.html', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')

        if username != user.username or password != user.password:
            flash("Incorrect Username/Password. Please try again.")

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()


        if len(username) < 3:
            flash("Username must be longer than 3 characters")

        elif existing_user:
            flash("Username already exists")

        elif len(password) < 3:
            flash("Password must be longer than 3 characters")

        elif password != verify:
            flash("Passwords do not match")

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    title_error = ''
    post_error = ''
    error_check = False

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == '':
            title_error = "Please enter a title"
            error_check = True
        if body == '':
            post_error = "Please enter a blog post"
            error_check = True
        if error_check == True:
            return render_template('new_post.html', title_error=title_error, post_error=post_error)
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            id_param = new_blog.id
            return redirect('/blog?id={0}'.format(id_param))

    return render_template('new_post.html')

@app.route('/blog', methods=['GET', 'POST'])
def list_blogs():
    blogs = Blog.query.all()
    if 'id' in request.args:
        blog_id = request.args['id']
        blog_post = Blog.query.get(blog_id)
        return render_template('single_post.html', blog=blog_post)

    return render_template('blog.html', blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
