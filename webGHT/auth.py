import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from webGHT.db import get_db
from webGHT.update_api_data import *

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '[ERR] Username is required.'
        elif not password:
            error = '[ERR] Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, permission) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), 'member'),
                )
                db.commit()
            except db.IntegrityError:
                error = f'[ERR] User is already registered.'
            else:
                return redirect(url_for("index"))

        flash(error) # stores messages that can be retrieved when rendering the template
    auto_update()
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute (
            'SELECT * FROM user WHERE username = ?', 
            (username,)
        ).fetchone()

        if user is None:
            error = '[ERR] User is not exist'
        elif not check_password_hash(user['password'], password):
            error = '[ERR] Incorrect password'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_permission'] = user['permission']
            update_data('all')
            return redirect(url_for('index'))
        
        flash(error)
    auto_update()
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
    
        return view(**kwargs)
    
    return wrapped_view