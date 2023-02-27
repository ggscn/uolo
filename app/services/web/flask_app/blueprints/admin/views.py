from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify

from flask_login import (
    login_required, login_user, current_user,logout_user)

from flask_app.blueprints.user.models import User
from flask_app.blueprints.admin.forms import UserForm

from lib.flask_login_utils import authorized_role

from flask_app.extensions import db

admin = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')

@admin.route('/dashboard')
@login_required
@authorized_role('admin')
def dashboard():
    columns = ['email','role','slug']
    return render_template('admin/dashboard.html', columns=columns)


@admin.route('/user/view/<string:slug>', methods=['GET','POST'])
@login_required
@authorized_role('admin')
def view_user(slug):
    user = User.find_by_slug(slug)
    form = UserForm(obj=user)

    stats = {
      
    }

    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/view_user.html', form=form, user=user, stats=stats)

@admin.route('/search-users', methods=['GET','POST'])
@login_required
@authorized_role('admin')
def search_users():
    r = request.json
    q = r.get('q', None)
    p = r.get('p', None)

    if q == None and q != '':
        users = User.query.order_by(User.email.asc()).paginate(int(p), 5)
    else:
        keyword_filter = User.email.ilike('%{}%'.format(q))
        users = User.query.filter(keyword_filter).order_by(User.email.asc()).paginate(int(p), 5)

    users = User.serialize_query(users, is_paginated=True)

    return jsonify(results=users)