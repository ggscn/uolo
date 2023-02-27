import flask
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify

from urllib.parse import urljoin

from flask_login import (
    login_required, login_user, current_user,logout_user)

from flask_app.blueprints.user.forms import NewUserForm, LoginForm, PasswordResetForm, GeneratePasswordResetForm, PasswordUpdateForm
from flask_app.blueprints.user.models import User
from flask_app.blueprints.user.decorators import anonymous_required

from datetime import datetime, timedelta
from datetime import date as date_module

user = Blueprint('user', __name__, template_folder='templates',)


@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.with_email(form.email.data)

        if user and user.is_authenticated(form.password.data):
            login_user(user)

            flash('Logged in successfully.', 'success')

            next = flask.request.args.get('next',None)
            if not urljoin(request.host_url, next):
                return flask.abort(400)
        else:
            next = None
            flash('Incorrect password or email', 'warning')

        return redirect(next or url_for('analysis.home'))
    return render_template('user/login.html', form=form)

@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
def new():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User()
        user.password_hash = User.hash_password(form.password.data)
        user.slug = User.generate_slug(form.email.data)
        user.email = form.email.data
        user.save()

        login_user(user)

        flash('Logged in successfully.', 'success')

        return redirect(url_for('analysis.home'))
    return render_template('user/new.html', form=form)

@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('analysis.home'))

@user.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html',user=current_user)

@user.route('/reset-password', methods=['GET', 'POST'])
@anonymous_required()
def reset_password():
    form = GeneratePasswordResetForm()

    if form.validate_on_submit():
        email = form.email.data
        user = User.with_email(email)
        if user:
            reset_token = user.generate_token()
            from flask_app.blueprints.user.tasks import send_password_reset_email
            send_password_reset_email.delay(user.email, reset_token)
        return redirect(url_for('analysis.home'))
    return render_template('user/password_reset.html', form=form)

@user.route('/new-password', methods=['GET', 'POST'])
@anonymous_required()
def new_password():

    form = PasswordResetForm()
    form.reset_token.data = request.args.get('reset_token')

    if form.validate_on_submit():
        try:
            plaintext_token = User.decrypt_token(request.form.get('reset_token'))
            user_email = plaintext_token.get('user_email')
            user = User.with_email(user_email)
            user.password_hash = User.hash_password(form.password.data)
            user.save()

            from flask_app.blueprints.user.tasks import send_password_reset_confirmation_email
            send_password_reset_confirmation_email.delay(user.email)
        except Exception as e:
            print(e)
            flash('There is something wrong with your password reset token.', 'warning')
        return redirect(url_for('analysis.home'))
    return render_template('user/new_password.html', form=form)

@user.route('/settings/update-password', methods=['GET', 'POST'])
def update_password():
    form = PasswordUpdateForm()
    
    user = User.with_email(current_user.email)

    if form.validate_on_submit():
        if user.is_authenticated(form.old_password.data):
            user.password_hash = User.hash_password(form.password.data)
            user.save()
            flash('Password successfully updated', 'success')
        else:
            flash('Incorrect password','warning')
        return redirect(url_for('user.settings'))
        
    return render_template('user/update-password.html', form=form)


