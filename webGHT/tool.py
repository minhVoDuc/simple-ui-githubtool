from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from webGHT.auth import login_required
from webGHT.db import get_db
from webGHT.get_data import *
from webGHT.update_api_data import *
from api import github_action
bp = Blueprint('tool', __name__)

# view tools
## view home
@bp.route('/', methods=('GET', 'POST'))
def index():  
  '''Display homepage'''
  if 'user_id' in session and session['user_id'] != '':
    org_info = dict()
    org_info['name'] = get_org_name(session['user_id'])
    if (org_info['name'] is None) or (org_info['name'] == ''):
      flash("Please insert orgname to use tools")
    org_info['token'] = get_token_id(session['user_id'])
    if (org_info['token'] is None) or (org_info['token'] == ''):
      flash("Please insert token to use tools")
    teams = get_def_teams(session['user_id'])
    webhook_url = get_def_webhooks(session['user_id'])
    auto_update()
    return render_template('tool/index.html', cred=org_info, teams=teams, webhook_urls=webhook_url)
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
    update_data('org_name')
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
    update_data('token')
  return redirect(url_for('index'))  
  
## add default webhooks
@bp.route('/add-def-webhook', methods=('POST',))
def add_def_webhook():
  '''Add to default webhooks'''
  new_webhook = request.form['webhook']
  error = None
  db = get_db()
  
  if new_webhook == "" or new_webhook is None:
    error = '[ERR] Webhook URL is empty!'
  else:
    checking = db.execute(
      'SELECT *'
      ' FROM org_webhooks'
      ' WHERE webhook_url = ?',
      (new_webhook,)
    ).fetchall()
    if len(checking) > 0:
      error = '[ERR] This team already existed!'
    
    if error is not None:
      flash(error)
    else:    
      org_id = get_org_id(session['user_id'])
      db.execute(
        'INSERT INTO org_webhooks'
        ' (org_id, webhook_url) VALUES (?, ?)',
        (org_id, new_webhook)
      )
      db.commit()
      update_data('webhook')
  return redirect(url_for('index'))  
  
# create repo
## main 
@bp.route('/create_repo', methods=('GET', 'POST'))
@login_required
def create_repo():
  '''Create repo'''
  if request.method == 'POST':
    new_repos = list(eval('['+request.form['json-list']+']'))
    opt_create_prod = False
    opt_apply_p_rule = False
    if 'readme-switch' in request.form:
      containReadme = request.form['readme-switch']
      if 'prod-switch' in request.form:
        opt_create_prod = True
      if 'protect-switch' in request.form:
        opt_apply_p_rule = True
    else:
      containReadme = 'no'
    for new_repo in new_repos:
      repo_name = new_repo['name']
      if containReadme == 'yes':
        new_repo['auto_init'] = True
      else:
        new_repo['auto_init'] = False
      log = github_action.create_a_repo(new_repo)
      print(log)
      # create branch production (if yes)
      if opt_create_prod:
        log = github_action.create_branch(repo_name, 'production')
        print(log)
      # apply branch protection rule (if yes)
      if opt_apply_p_rule:
        branches = github_action.api_github.list_all_branches(repo_name)
        repo_info = {
          'name': repo_name,
          'branches': branches
        }
        github_action.apply_branch_rule(repo_info)
    return redirect(url_for('tool.create_repo'))
  auto_update()
  repos = github_action.list_all_repos()
  print(repos)
  g.active_side_item = 'create_repo'
  return render_template('tool/create_repo.html', repos=repos)

## delete repo
@bp.route('/clear-all-repo', methods=('POST',))
def clear_all_repo():
  '''Clear All Existed Repo'''
  raw_repos = github_action.list_all_repos()
  print(raw_repos)
  repos = [repo['name'] for repo in raw_repos]
  print(repos)
  for repo in repos:
    github_action.api_github.delete_repo(repo)
  return redirect(url_for('tool.create_repo'))

# create branch
## main 
@bp.route('/create_branch/', methods=('GET', 'POST'))
@login_required
def create_branch():
  '''Create branch'''
  if request.method == 'POST':
    return redirect(url_for('tool.create_branch'))
  auto_update()
  g.active_side_item = 'create_branch'
  lacking_repos = list()
  branch = ""
  if 'branch' in session:
    branch = session['branch']
  if 'lacking_repos' in session:
    lacking_repos = session['lacking_repos']
  return render_template('tool/create_branch.html', branch=branch, repos=lacking_repos)

## create new branch for list of repo
@bp.route('/create_branch/create', methods=('POST',))
@login_required
def create_spec_branch():
  '''create branch for repo list'''
  repos = request.form.getlist('repos[]')
  branch = request.form['branch']
  for repo in repos:
    log = github_action.create_branch(repo, branch)
    print(log)
  get_lacking_repo(session['branch'])
  return redirect(url_for('tool.create_branch'))

# action choose branch to scan repo
@bp.route('/scan_branch', methods=('POST',))
@login_required
def scan_branch():
  if 'scanbranch-select' in request.form:
    branch = request.form['scanbranch-select']
    get_lacking_repo(branch)
  else:
    flash('[ERR] Please choose a branch!')
  return redirect(url_for('tool.create_branch'))

# add team
## main 
@bp.route('/collaborator', methods=('GET',))
@login_required
def display_collaborator():
  auto_update()
  org_name = get_org_name(session['user_id'])
  org_teams = get_all_teams()
  org_members = get_all_members()
  org_invitations = get_all_invitations()
  repos = get_all_repos()
  g.active_side_item = 'add_teams'
  print(org_invitations)
  return render_template('tool/add_teams.html',
                         org_name=org_name,
                         org_teams=org_teams,
                         org_members=org_members,
                         invitations=org_invitations,
                         repos=repos)

## add def teams
@bp.route('/collaborator/add_def_teams', methods=('POST',))
@login_required
def add_default_teams():
  '''Add to default teams'''
  teams = request.form.getlist('teams[]')
  print("DEMO", request.data)
  for new_team in teams:
    print("DEMO", type(new_team))
    error = None
    db = get_db()
    
    checking = db.execute(
        'SELECT *'
        ' FROM org_teams'
        ' WHERE team_name = ?',
        (new_team['name'],)
      ).fetchall()
    if len(checking) > 0:
      error = '[ERR] team '+new_team['name']+' already existed!'
    
    if error is not None:
      flash(error)
    else:    
      if new_team['permission'] not in ['pull', 'triage', 'push', 'maintain', 'admin']:
        new_team['permission'] = 'pull'
      org_id = get_org_id(session['user_id'])
      db.execute(
        'INSERT INTO org_teams'
        ' (org_id, team_name, team_permission) VALUES (?, ?, ?)',
        (org_id, new_team['name'], new_team['permission'])
      )
      db.commit()
  update_data('default_teams')
      
  return redirect(url_for('tool.display_collaborator'))  

## clear all def teams
@bp.route('/collaborator/clear_all_def_teams', methods=('POST',))
@login_required
def clear_all_def_teams():
  db = get_db()
  error = None
  if error is not None:
    flash(error)
  else:
    org_id = get_org_id(session['user_id'])
    print(org_id)
    db.execute(
      'DELETE FROM org_teams'
      ' WHERE org_id = ?',
      (org_id,)
    )
    db.commit()
  update_data('default_team')
  return redirect(url_for('tool.display_collaborator'))

## invite new member
@bp.route('/collaborator/invite_member', methods=('POST',))
@login_required
def invite_member():
  emails = request.form['invitation_email'].split(',')
  invite_members(emails)
  return redirect(url_for('tool.display_collaborator'))  

## remove an invitation
@bp.route('/collaborator/clear_invitation', methods=('POST',))
@login_required
def clear_invitation():
  invitation_id = request.form['invitation_id']
  status_code = cancel_invitations(invitation_id)
  if status_code == 404:
    flash('[ERR] Invitation not found!')
  elif status_code == 422:
    flash('[ERR] Cannot cancel an accepted invitation!')
  else:
    return redirect(url_for('tool.display_collaborator'))