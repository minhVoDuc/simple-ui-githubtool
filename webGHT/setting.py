from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from webGHT.auth import login_required
from webGHT.db import get_db
from webGHT.get_data import get_user
bp = Blueprint('setting', __name__)

# User Profile
## display user profile
@bp.route('/setting/profile')
@login_required
def get_profile():
  error = None
  if 'user_id' not in session:
    error = '[ERR] You are not login yet!'
  
  if error is not None:
    flash(error)
  else:
    user = get_user(session['user_id'])
    print(user['id'])
    return render_template('setting/profile.html', user=user)
 
## update user permission (only dev)
@bp.route('/setting/profile/change_permission', methods=('POST',))
@login_required
def change_permision():
  exist_perm = ['superadmin', 'projectadmin', 'member']
  error = None
  db = get_db()
  
  permission = request.form['permission']
  user_id = session['user_id']
  if permission is None or permission == "":
    error = '[ERR] Please provide a permission'
  
  if error is not None:
    flash(error)
  else:
    if permission not in exist_perm:
      permission = 'member'
    db.execute(
      'UPDATE user'
      ' SET permission = ?'
      ' WHERE id = ?',
      (permission, user_id)
    )
    db.commit()
    session['user_permission'] = permission
  return redirect(url_for('setting.get_profile', user_id=session['user_id']))