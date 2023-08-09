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
  ).fetchone()['org_name']
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
  ).fetchone()['token']      
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
  ).fetchone()['id']
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
  print(org_teams)
  return org_teams

# get all teams in a repo
def get_teams(repo_name):
  repo_teams = list_teams(repo_name)
  print(repo_teams)
  return repo_teams