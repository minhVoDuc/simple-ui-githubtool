import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from webGHT.db import get_db
from webGHT.get_data import get_org_name, get_token_id, get_def_teams
from api import github_action

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
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f'[ERR] User is already registered.'
            else:
                return redirect(url_for("index"))

        flash(error) # stores messages that can be retrieved when rendering the template
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
            github_action.set_org_name(get_org_name(session['user_id']))
            github_action.set_token(get_token_id(session['user_id']))
            github_action.set_default_team(get_def_teams(session['user_id']))
            return redirect(url_for('index'))
        
        flash(error)
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