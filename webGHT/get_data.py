from webGHT.db import get_db
from api.github_action import *
from flask import session

## get org_name
def get_org_name(user_id):
  '''Get current github organization's name'''
  db = get_db()
  db_org_name = db.execute(
    'SELECT org_name'
    ' FROM cred'
    ' WHERE user_id = ?',
    (user_id,)
  ).fetchone()
  if db_org_name is not None:
    db_org_name = db_org_name['org_name']
  return db_org_name

## get curr token_id
def get_token_id(user_id):
  '''Get current personal access token'''
  db = get_db()
  db_token_id = db.execute(
    'SELECT token'
    ' FROM cred'
    ' WHERE user_id = ?',
    (user_id,)
  ).fetchone()     
  if db_token_id is not None:
    db_token_id = db_token_id['token']
  return db_token_id

## get org_id
def get_org_id(user_id):
  '''Get org id'''
  db = get_db()
  org_id = db.execute(
    'SELECT id'
    ' FROM cred'
    ' WHERE user_id = ?',
    (user_id,)
  ).fetchone()
  if org_id is not None:
    org_id = org_id['id']
  return org_id

## get default teams
def get_def_teams(user_id):
  '''Get default teams'''
  db = get_db()
  org_id = get_org_id(user_id)
  teams = db.execute(
    'SELECT *'
    ' FROM org_teams'
    ' WHERE org_id = ?',
    (org_id,)
  ).fetchall()
  return teams

## get default webhook
def get_def_webhooks(user_id):
  '''Get default teams'''
  db = get_db()
  org_id = get_org_id(user_id)
  raw_teams = db.execute(
    'SELECT *'
    ' FROM org_webhooks'
    ' WHERE org_id = ?',
    (org_id,)
  ).fetchall()
  teams = [team['webhook_url'] for team in raw_teams]
  return teams

# get all repos that misses branch
def get_lacking_repo(branch):
  repos_name = [repo['name'] for repo in list_all_repos()]
  lacking_repos = list_lacking_branch_repos(repos_name, branch)
  print(lacking_repos)
  session['lacking_repos'] = lacking_repos
  session['branch'] = branch
  
# get all teams in org
def get_all_teams():
  '''Listing all available teams in organization'''
  raw_org_teams = list_teams("[[org]]")
  org_teams = [
    {
      'name': team['name'],
      'slug': team['slug'],
      'parent': "" if team['parent'] is None else team['parent']['name'],
      'permission': team['permission']
    }
    for team in raw_org_teams
  ]
  return org_teams

# get all teams in a repo
def get_teams(repo_name):  
  '''Listing all available teams in a repo'''
  repo_teams = list_teams(repo_name)
  return repo_teams

# get all members in organization
def get_all_members():
  '''Listing all members in organization'''
  raw_org_members = list_members("[[org]]")
  org_members = [
    {
      'id': member['id'],
      'name': member['name']
    }
    for member in raw_org_members
  ]
  return org_members

# get all invitations to join org
def get_all_invitations():
  '''Listing all invitations'''
  invitations = list_invitations("[[org]]")
  return invitations

# get all members in a repo
def get_members(repo_name):  
  '''Listing all members in a repo'''
  repo_members = list_members(repo_name)
  print(repo_members)
  return repo_members

## get user info 
def get_user(user_id):  
  '''Listing all info about a user of this tool'''
  db = get_db()
  user = db.execute(
    'SELECT *'
    ' FROM user'
    ' WHERE id = ?',
    (user_id,)
  ).fetchone()
  return user

## get all repo
def get_all_repos():
  '''List all repos in organization'''
  repos = list_all_repos()
  return repos