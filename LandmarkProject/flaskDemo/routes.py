import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, HomeForm, AddFavForm, DeleteFavForm, UpdateFavForm
from flaskDemo.models import User, Landmarks, Favorites, Neighborhoods
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    image_file = ''
    name = ''
    favorites = ''
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        name = current_user.username
        favorites = find_favs()
    form = HomeForm()
    neighborhood = ''
    if form.validate_on_submit():
        neighborhood = Landmarks.query.filter_by(neighborhood=form.neighborhood.data).all()
    return render_template('home.html', image_file=image_file, form=form, neighborhood=neighborhood, favorites=favorites, name=name)

@app.route("/about")
def about():
    image_file = ''
    name = ''
    favorites = ''
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        name = current_user.username
        favorites = find_favs()
    return render_template('about.html', title='About', image_file=image_file, favorites=favorites, name=name)


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
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    name = current_user.username
    favorites = find_favs()
    return render_template('account.html', title='Account', image_file=image_file, form=form, name=name, favorites=favorites)


@app.route("/update", methods=['GET', 'POST'])
@login_required
def update():
    favorites = find_favs()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
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
    return render_template('update.html', title='New Favorite', form1=form1, form2=form2, form3=form3, image_file=image_file, favorites=favorites)


def find_favs():
    favorites = Favorites.query.filter_by(user_id=current_user.id) \
    .join(Landmarks,Landmarks.id == Favorites.landmark_id) \
    .add_columns(Landmarks.name, Favorites.visited).all()
    return favorites
