from flask import Flask, render_template, url_for, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from forms import CreateForm
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home Sweet Home')


@app.route("/about")
def about():
    return render_template('about.html', title='About Me')

@app.route("/create", methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        # newPost = Post(title=form.title.data, date_posted=form.date_posted.data, content=form.content.data, user_id=form.user_id.data)
        # add newPost
        # commit newPost
        flash('Thanks for your post!', 'success')
    return render_template('create.html', title='Create Post', form=form)

@app.route("/blog", methods=['GET', 'POST'])
def lab():
    # get info from db
    return render_template('blog.html', posts=posts, title='Blog Time')


if __name__ == '__main__':
    app.run(debug=True)
