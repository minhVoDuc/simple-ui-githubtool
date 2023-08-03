from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from webGHT.auth import login_required
from webGHT.db import get_db
from api import github_action
import json

bp = Blueprint('tool', __name__)

# view tools
@bp.route('/', methods=('GET', 'POST'))
def index():
  if request.method == 'POST':
    new_token = request.form['token']
    error = None
    
    if error is not None:
      flash(error)
    else:
      db = get_db()
      db.execute(
        'INSERT OR IGNORE INTO cred'
        ' (user_id, token) VALUES (?, ?)',
        (session['user_id'], new_token,)
      )
      db.execute(
        ' UPDATE cred'
        ' SET token=?'
        ' WHERE user_id=?',
        (new_token, session['user_id'],)
      )
      db.commit()
      return redirect(url_for('index'))
  db = get_db()
  if g.user is not None:
    cred = db.execute (
      'SELECT *'
      ' FROM cred'
      ' WHERE user_id = ?',
      (g.user['id'],)
    ).fetchone()
    return render_template('tool/index.html', cred=cred)
  else:
    flash('Please login!')
    return render_template('tool/index.html')
  
# create repo
## main 
@bp.route('/create_repo', methods=('GET', 'POST'))
@login_required
def create_repo():
  if request.method == 'POST':
    new_repos = list(eval('['+request.form['json-list']+']'))
    containReadme = request.form['readme-switch']
    print("DEMOO", type(new_repos))
    for new_repo in new_repos:
      print(new_repo)
      if containReadme == 'yes':
        new_repo['auto_init'] = True
      else:
        new_repo['auto_init'] = False
      log = github_action.create_a_repo(new_repo)
      print(log)
    return redirect(url_for('tool.create_repo'))
 
  g.active_side_item = 'create_repo'
  return render_template('tool/create_repo.html')

# support function
def get_post(id, check_author=True):
  post = get_db().execute(
    'SELECT p.id, title, body, created, author_id, username'
    ' FROM post p JOIN user u ON p.author_id = u.id'
    ' WHERE p.id = ?',
    (id,)
  ).fetchone()
  
  if post is None:
    abort(404, f"[ERR] Post id {id} doesn't exist")
  
  if check_author and post['author_id'] != g.user['id']:
    abort(403)
    
  return post