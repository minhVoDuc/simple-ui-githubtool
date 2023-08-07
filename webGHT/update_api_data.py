from flask import session
from webGHT.db import get_db
from webGHT.get_data import *
from api import github_action

def auto_update():
  if 'user_id' in session:
    if github_action.is_empty_token():
      update_data('token')
    if github_action.is_empty_org_name():
      update_data('org_name')
    if github_action.is_empty_default_team():
      update_data('default_team')
    if github_action.is_empty_webhook():
      update_data('webhook')

def update_data(part='all'):
  if part=='all' or part=='org_name':
    github_action.set_org_name(get_org_name(session['user_id']))
  if part=='all' or part=='token':
    github_action.set_token(get_token_id(session['user_id']))
  if part=='all' or part=='default_team':
    github_action.set_default_team(get_def_teams(session['user_id']))
  if part=='all' or part=='webhook':
    github_action.set_default_webhook(get_def_webhooks(session['user_id']))

  