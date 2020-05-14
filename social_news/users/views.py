from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from social_news import db
from werkzeug.security import generate_password_hash,check_password_hash
from social_news.models import User, NewsItem
from social_news.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from social_news.users.picture_handler import add_profile_pic


users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        if form.check_email(form.email):
            if form.check_username(form.username):
                user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)

                db.session.add(user)
                db.session.commit()
                flash('Спасибо за регистрацию пожалуйста войдите!')
                return redirect(url_for('users.login'))
            else:
                return render_template('error_pages/username_dupl.html', username = form.username.data)
        else:
            return render_template('error_pages/email_dupl.html', email = form.email.data)
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            #Log in the user

            login_user(user)
            flash('Вы успешно вошли')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('core.index')

            return redirect(next)
    return render_template('login.html', form=form)




@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateUserForm()

    if form.validate_on_submit():
        print(form)
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Аккаунт обновлен')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)


@users.route("/<username>")
def user_news(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    news = NewsItem.query.filter_by(author=user).order_by(NewsItem.date.desc( )).paginate(page=page, per_page=5)
    return render_template('user_news.html', news=news, user=user)
