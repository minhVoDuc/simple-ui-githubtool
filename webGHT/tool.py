from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from webGHT.auth import login_required
from webGHT.db import get_db
from webGHT import get_data
from api import github_action

bp = Blueprint('tool', __name__)

# view tools
## view home
@bp.route('/', methods=('GET', 'POST'))
def index():  
  '''Display homepage'''
  if session['user_id'] is not None:
    org_info = dict()
    org_info['name'] = get_data.get_org_name(session['user_id'])
    org_info['token'] = get_data.get_token_id(session['user_id'])
    teams = get_data.get_def_teams(session['user_id'])
    return render_template('tool/index.html', cred=org_info, teams=teams)
  else:
    flash('Please login!')
    return render_template('tool/index.html')

## change org name
@bp.route('/change-orgname', methods=('POST',))
def change_orgname():  
  '''Change github organization's name'''
  new_orgname = request.form['orgname']
  error = None
  
  if new_orgname == "" or new_orgname is None:
    error = '[ERR] New organization name is empty!'
  
  if error is not None:
    flash(error)
  else:
    db = get_db()
    checking = db.execute(
      'SELECT *'
      ' FROM cred'
      ' WHERE user_id = ?',
      (session['user_id'],)
    ).fetchall()
    if len(checking) == 0:
      db.execute(
        'INSERT OR IGNORE INTO cred'
        ' (user_id, org_name) VALUES (?, ?)',
        (session['user_id'], new_orgname,)
      )
    else:
      db.execute(
        ' UPDATE cred'
        ' SET org_name=?'
        ' WHERE user_id=?',
        (new_orgname, session['user_id'],)
      )
    db.commit()
    github_action.set_org_name(new_orgname)
  return redirect(url_for('index'))
  
## change token id
@bp.route('/change-token', methods=('POST',))
def change_tokenid():
  '''Change personal access token'''
  new_token = request.form['token']
  error = None
  
  if new_token == "" or new_token is None:
    error = '[ERR] Token is empty!'
    
  if error is not None:
    flash(error)
  else:
    db = get_db()
    checking = db.execute(
      'SELECT *'
      ' FROM cred'
      ' WHERE user_id = ?',
      (session['user_id'],)
    ).fetchall()
    if len(checking) == 0:
      db.execute(
        'INSERT OR IGNORE INTO cred'
        ' (user_id, token) VALUES (?, ?)',
        (session['user_id'], new_token,)
      )
    else:
      db.execute(
        ' UPDATE cred'
        ' SET token=?'
        ' WHERE user_id=?',
        (new_token, session['user_id'],)
      )
    db.commit()
    github_action.set_token(new_token)
  return redirect(url_for('index'))  
  
## change token id
@bp.route('/add-team', methods=('POST',))
def add_def_team():
  '''Add to default teams'''
  new_team = dict()
  new_team['name'] = request.form['team-name']
  new_team['permission'] = request.form['team-permission']
  error = None
  db = get_db()
  
  if new_team['name'] == "" or new_team['name'] is None:
    error = '[ERR] New team name is empty!'
  else:
    checking = db.execute(
      'SELECT *'
      ' FROM org_teams'
      ' WHERE team_name = ?',
      (new_team['name'],)
    ).fetchall()
    if len(checking) > 0:
      error = '[ERR] This team already existed!'
    
    if error is not None:
      flash(error)
    else:    
      if new_team['permission'] not in ['pull', 'triage', 'push', 'maintain', 'admin']:
        new_team['permission'] = 'pull'
      org_id = get_data.get_org_id(session['user_id'])
      db.execute(
        'INSERT INTO org_teams'
        ' (org_id, team_name, team_permission) VALUES (?, ?, ?)',
        (org_id, new_team['name'], new_team['permission'])
      )
      db.commit()
      github_action.add_teams([new_team])
  return redirect(url_for('index'))  
  
# create repo
## main 
@bp.route('/create_repo', methods=('GET', 'POST'))
@login_required
def create_repo():
  '''Create repo'''
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