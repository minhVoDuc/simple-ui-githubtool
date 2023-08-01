from flask import (
  Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from webGHT.auth import login_required
from webGHT.db import get_db

bp = Blueprint('tool', __name__)

# view tools
@bp.route('/')
def index():
  db = get_db()
  posts = db.execute (
    'SELECT p.id, title, body, created, author_id, username'
    ' FROm post p JOIN user u ON p.author_id = u.id'
    ' ORDER BY created DESC'
  ).fetchall()
  return render_template('tool/index.html', posts=posts)

# create repo
@bp.route('/create_repo', methods=('GET', 'POST'))
@login_required
def create():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None
    
    if not title:
      error = '[ERR] Title is required.'
    
    if error is not None:
      flash(error)
    else:
      db = get_db()
      db.execute(
        'INSERT INTO post (title, body, author_id)'
        ' VALUES (?, ?, ?)',
        (title, body, g.user['id'])
      )
      db.commit()
      return redirect(url_for('tool.index'))
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