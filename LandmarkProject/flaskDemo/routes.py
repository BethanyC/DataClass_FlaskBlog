import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt, conn
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, HomeForm, HomeForm2, AddFavForm, AddFavForm2, DeleteFavForm, UpdateFavForm
from flaskDemo.models import User, Landmarks, Favorites, Neighborhoods
from flask_login import login_user, current_user, logout_user, login_required
import mysql.connector

def find_favs():
    favorites = Favorites.query.filter_by(user_id=current_user.id) \
    .join(Landmarks,Landmarks.id == Favorites.landmark_id) \
    .add_columns(Landmarks.name, Favorites.visited).all()
    return favorites

# this wasn't updating without restarting the program, after googling I believe it was because it is on a separate db connection than the update
# def get_num_favs():
#     if conn.is_connected():
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT count(landmark_id) FROM favorites WHERE user_id=" + str(current_user.id) + ";")
#         return cursor.fetchone()
def get_num_favs():
    return Favorites.query.filter_by(user_id=current_user.id).count()


def user_setup():
    image_file = ''
    name = ''
    favorites = ''
    num_favs = ''
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        name = current_user.username
        favorites = find_favs()
        num_favs = get_num_favs()
    return [image_file, name, favorites, num_favs]

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    usr = user_setup()
    form1 = HomeForm()
    form2 = HomeForm2()
    neighborhood = ''
    if form1.submit1.data and form1.validate():
        neighborhood = Landmarks.query.filter_by(neighborhood=form1.neighborhood.data).all()
        for landmark in neighborhood:
            count = Favorites.query.filter_by(landmark_id=landmark.id).count()
            landmark.count = count
    if form2.submit2.data and form2.validate():
        neighborhood = Landmarks.query.filter_by(architect=form2.architect.data).all()
        for landmark in neighborhood:
            count = Favorites.query.filter_by(landmark_id=landmark.id).count()
            landmark.count = count
    return render_template('home.html', form1=form1, form2=form2, neighborhood=neighborhood, image_file=usr[0], name=usr[1], favorites=usr[2], num_favs=usr[3])

@app.route("/landmark/<landmark_id>", methods=['GET', 'POST'])
def landmark(landmark_id):
    usr = user_setup()
    form = AddFavForm2()
    landmark = Landmarks.query.filter_by(id=landmark_id).first()
    already_saved = ''
    landmark_string = "(" + str(landmark_id) + ",)"
    if current_user.is_authenticated:
        already_saved = str(Favorites.query.filter_by(user_id=current_user.id).with_entities(Favorites.landmark_id).all())
    if form.validate_on_submit():
        favorite = Favorites(user_id=current_user.id, landmark_id=landmark.id, visited=form.visited.data)
        db.session.add(favorite)
        db.session.commit()
        flash('Landmark favorited!', 'success')
        return redirect(url_for('home'))
    return render_template('landmark.html', form=form, landmark=landmark, already_saved=already_saved, landmark_string=landmark_string, image_file=usr[0], name=usr[1], favorites=usr[2], num_favs=usr[3])

@app.route("/about")
def about():
    usr = user_setup()
    landmarks = ''
    if conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, (SELECT count(user_id) FROM favorites WHERE favorites.landmark_id = landmarks.id) AS count FROM landmarks ORDER BY name LIMIT 20;")
        landmarks = cursor.fetchall()
    return render_template('about.html', title='About', landmarks=landmarks, image_file=usr[0], name=usr[1], favorites=usr[2], num_favs=usr[3])


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
            neighborhood=form.neighborhood.data, password=hashed_password, image_file='default.jpg')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    usr = user_setup()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.neighborhood = form.neighborhood.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.neighborhood.data = current_user.neighborhood
    return render_template('account.html', title='Account', form=form, image_file=usr[0], name=usr[1], favorites=usr[2], num_favs=usr[3])


@app.route("/update", methods=['GET', 'POST'])
@login_required
def update():
    usr = user_setup()
    form1 = AddFavForm()
    if form1.submit1.data and form1.validate():
        favorite = Favorites(user_id=current_user.id, landmark_id=form1.landmark.data.id, visited=form1.visited.data)
        db.session.add(favorite)
        db.session.commit()
        flash('Landmark favorited!', 'success')
        return redirect(url_for('home'))
    form2 = UpdateFavForm()
    if form2.submit2.data and form2.validate():
        favorite = Favorites.query.filter(Favorites.user_id==current_user.id, Favorites.landmark_id==form2.landmark.data.id).first()
        favorite.visited = form2.visited.data
        db.session.commit()
        flash('Landmark updated!', 'success')
        return redirect(url_for('home'))
    form3 = DeleteFavForm()
    if form3.submit3.data and form3.validate():
        favorite = Favorites.query.filter(Favorites.user_id==current_user.id, Favorites.landmark_id==form3.landmark.data.id).first()
        db.session.delete(favorite)
        db.session.commit()
        flash('Landmark removed', 'success')
        return redirect(url_for('home'))
    return render_template('update.html', title='New Favorite', form1=form1, form2=form2, form3=form3, image_file=usr[0], name=usr[1], favorites=usr[2], num_favs=usr[3])
