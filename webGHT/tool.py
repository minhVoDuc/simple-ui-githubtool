from flask import (
  Blueprint, flash, jsonify, g, redirect, render_template, request, session, url_for, abort
)
from webGHT.auth import login_required
from webGHT.db import get_db
from webGHT.get_data import *
from webGHT.update_api_data import *
from api import github_action
bp = Blueprint('tool', __name__)

# View tools
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
    team_name = [team['team_name'] for team in teams]
    webhook_url = get_def_webhooks(session['user_id'])
    org_teams = get_all_teams()
    free_teams = [
      {
        'name': team['name'],
        'slug': team['slug']
      }
      for team in org_teams
      if team['slug'] not in team_name
    ]
    auto_update()
    return render_template('tool/index.html',
                           cred=org_info,
                           teams=teams,
                           org_teams=free_teams,
                           webhook_urls=webhook_url)
  else:
    flash('[INFO] Please login!')
    return render_template('tool/index.html')

## change org name
@bp.route('/change_orgname', methods=('POST',))
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
@bp.route('/change_token', methods=('POST',))
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
  
## add def teams
@bp.route('/add_def_team', methods=('POST',))
@login_required
def add_default_team():
  '''Add to default teams'''
  team_name = request.form['team']
  error = None
  db = get_db()
  
  checking = db.execute(
      'SELECT *'
      ' FROM org_teams'
      ' WHERE team_name = ?',
      (team_name,)
    ).fetchall()
  if len(checking) > 0:
    error = '[ERR] team '+team_name+' already existed!'
  
  if error is not None:
    flash(error)
  else:    
    org_id = get_org_id(session['user_id'])
    db.execute(
      'INSERT INTO org_teams'
      ' (org_id, team_name) VALUES (?, ?)',
      (org_id, team_name)
    )
    db.commit()
  update_data('default_teams')
      
  return redirect(url_for('index'))  

## clear all def teams
@bp.route('/clear_all_def_teams', methods=('POST',))
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
  return redirect(url_for('index'))  
  
## add default webhooks
@bp.route('/add_def_webhook', methods=('POST',))
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
  
# Repo
## main 
@bp.route('/repo', methods=('GET', 'POST'))
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
  g.active_side_item = 'repo'
  return render_template('tool/repos.html', repos=repos)

## delete repo
@bp.route('/clear_all_repo', methods=('POST',))
def clear_all_repo():
  '''Clear All Existed Repo'''
  raw_repos = github_action.list_all_repos()
  print(raw_repos)
  repos = [repo['name'] for repo in raw_repos]
  print(repos)
  for repo in repos:
    github_action.api_github.delete_repo(repo)
  return redirect(url_for('tool.create_repo'))

# Branch
## main 
@bp.route('/branch/')
@login_required
def create_branch():
  '''Create branch'''
  auto_update()
  g.active_side_item = 'branch'
  lacking_repos = list()
  branch = ""
  if 'branch' in session:
    branch = session['branch']
  if 'lacking_repos' in session:
    lacking_repos = session['lacking_repos']
  return render_template('tool/branches.html', branch=branch, repos=lacking_repos)

## create new branch for list of repo
@bp.route('/branch/create', methods=('POST',))
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

## choose branch to scan repo
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
  session['org_teams'] = [
    {
      'slug': team['slug'],
      'permission': team['permission']
    }
    for team in org_teams
  ]
  org_members = get_all_members()
  org_invitations = get_all_invitations()
  repos = get_all_repos()
  
  repo_teams = list()
  if 'repo_teams' in session:
    repo_teams = session['repo_teams']
  print("repo_teams:", repo_teams)
  free_teams = list()
  if 'free_teams' in session:
    free_teams = session['free_teams']
    
  g.active_side_item = 'collaborator'
  return render_template('tool/collaborators.html',
                         org_name=org_name,
                         org_teams=org_teams,
                         org_members=org_members,
                         invitations=org_invitations,
                         repos=repos,
                         repo_teams=repo_teams,
                         free_teams=free_teams)

## scan teams in a repo
@bp.route('/collaborator/scan_repo/teams', methods=('POST',))
@login_required
def scan_repo_team():
  repo_name = request.form['sr-select']
  session['repo_name'] = repo_name
  session['repo_teams'] = get_teams(repo_name)
  repo_teams_name = [team['slug'] for team in session['repo_teams']]
  print("org teams:",session['org_teams'])
  session['free_teams'] = [team for team in session['org_teams'] 
                          if team['slug'] not in repo_teams_name]
  return redirect(url_for('tool.display_collaborator'))

## add teams to a repo
@bp.route('/collaborator/add_repo_teams', methods=('POST',))
@login_required
def add_repo_teams():
  teams = request.form.getlist('selected_teams[]')
  permissions = request.form.getlist('permission[]')
  team_list = [
    {
      'slug': team,
      'permission': permission
    }
    for team, permission in zip(teams, permissions)
  ]
  if len(team_list) == 0:
    abort(400, description="[ERR] Please choose at least one team!")
  error = github_action.add_teams(session['repo_name'], team_list)
  if error is not None:
    abort(400, description="[ERR] Could not add team to "+session['repo_name']+"!")
  tmp = session['free_teams']
  session['free_teams'] = [team for team in tmp
                           if team['slug'] not in teams]
  session['repo_teams'].extend([team for team in tmp
                                if team['slug'] in teams])
  return redirect(url_for('tool.display_collaborator'))

## remove teams in a repo
@bp.route('/collaborator/remove_repo_teams', methods=('POST',))
@login_required
def remove_repo_teams():
  teams = request.form.getlist('selected_teams[]')
  if len(teams) == 0:
    abort(400, description="[ERR] Please choose at least one team!")
  error = github_action.remove_teams(session['repo_name'], teams)
  if error is not None:
    abort(400, description="[ERR] Could not remove team!")
  tmp = session['repo_teams']
  session['repo_teams'] = [team for team in tmp
                           if team['slug'] not in teams]
  session['free_teams'].extend([team for team in tmp
                                if team['slug'] in teams])
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
  
# Protection
## display
@bp.route('/protection/')
@login_required
def display_protection():
  auto_update()
  repos = get_all_repos()
  g.active_side_item = 'protection'
  return render_template('tool/branch_rules.html',
                         repos=repos)

## add protection rule
@bp.route('/protection/add_protection', methods=('POST',))
@login_required
def add_protection():
  branches = request.form.getlist('branches[]')
  repos = request.form.getlist('repos[]')
  if len(branches) == 0:    
    abort(400, description="[ERR] Please choose at least one branch!")
  if len(repos) == 0:    
    abort(400, description="[ERR] Please choose at least one repo!")
  
  for repo in repos:
    error = apply_branch_rule(repo, branches)
    if error is not None:
      flash(error)
  
  return redirect(url_for('tool.display_protection'))

## rm protection rule
@bp.route('/protection/rm_protection', methods=('POST',))
@login_required
def rm_protection():
  branches = request.form.getlist('branches[]')
  repos = request.form.getlist('repos[]')
  if len(branches) == 0:    
    abort(400, description="[ERR] Please choose at least one branch!")
  if len(repos) == 0:    
    abort(400, description="[ERR] Please choose at least one repo!")
  
  for repo in repos:
    error = delete_branch_rule(repo, branches)
    if error is not None:
      flash(error)
  
  return redirect(url_for('tool.display_protection'))

# Webhook
## display
@bp.route('/webhook/')
@login_required
def display_webhook():
  g.active_side_item = 'webhook'
  return render_template('tool/webhooks.html') 

## create webhook
@bp.route('/webhook/create', methods=('POST',))
@login_required
def create_webhook():  
  auto_update()
  repos = get_all_repos()
  webhook_urls = get_def_webhooks(session['user_id'])
  print(repos)
  for repo in repos:
    for url in webhook_urls:
      error = create_repo_webhook(repo['name'], url)
      if error is not None: 
        flash(error)
  return redirect(url_for('tool.display_webhook'))