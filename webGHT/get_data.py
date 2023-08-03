from webGHT.db import get_db

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