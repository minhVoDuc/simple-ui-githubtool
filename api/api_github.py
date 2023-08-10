import requests
import json

org_name = None
headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}
team_permission = ['pull', 'triage', 'push', 'maintain', 'admin']
repo_visibility = ['private', 'public']

# 1. Repo
def list_all_repos():
    url = f'https://api.github.com/orgs/{org_name}/repos'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    return list([
            {
                'id': repo['id'],
                'name': repo['name'],
                'owner': repo['owner']['login']
            }
            for repo in r.json()
        ])

def create_repo(new_repo):
    url = f'https://api.github.com/orgs/{org_name}/repos'
    if (repo_visibility.count(new_repo['visibility']) == 0):
        new_repo['visibility'] = 'private'
    payload = {
        "name": new_repo['name'],
        "visibility": new_repo['visibility'],
        "auto_init": new_repo['auto_init']
    }
    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code

def delete_repo(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}'
    r = requests.delete(url=url, headers=headers)
    return r.status_code # 204: successful

# 2. Branch
def list_all_branches(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/branches'
    r = requests.get(url=url, headers=headers)
    return list([repo['name'] for repo in r.json()])

def find_revision(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/git/refs/heads'
    r = requests.get(url=url, headers=headers)
    if ('message' in r.json()):
        return "REPO_EMPTY"        
    else:
        data = r.json()[0]
        return data['object']['sha']
    
def create_dummy_file(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/contents/dummy'
    payload = {
        'branch': 'main',
        'message': 'Create a dummy file for the sake of creating a branch',
        'content': 'ZHVtbXk='
    }
    r = requests.put(url=url, headers=headers, data=json.dumps(payload))
    return r.json()['commit']['tree']['sha']

def create_init_commit(repo_name, tree_sha):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/git/commits'
    payload = {
        'message': 'Initial commit',
        'tree': tree_sha
    }
    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    # print(r.json())
    return r.json()['sha']

def create_init_branch(repo_name, commit_sha):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/git/refs/heads/main'
    payload = {
        'sha': commit_sha,
        'force': True
    }
    r = requests.patch(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code

def create_branch(repo_name, branch_name, revision_id):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/git/refs'
    payload = {
        'ref': f'refs/heads/{branch_name}',
        'sha': f'{revision_id}'
    }
    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code

def get_branch(repo_name, branch_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/branches/{branch_name}'
    r = requests.get(url=url, headers=headers)
    return r.status_code # 404: not found

def delete_branch(repo_name, branch_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/git/refs/heads/{branch_name}'
    r = requests.delete(url=url, headers=headers)
    return r.status_code # 204: successful

# 3. Branch Protection Rules
def get_p_rule(repo_name, branch_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}]/branches/{branch_name}/protection'
    r = requests.get(url=url, headers=headers)
    return r.status_code # 404: not found

def apply_p_rule(repo_name, branch_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/branches/{branch_name}/protection'
    payload = {
        "required_status_checks": None,
        "enforce_admins": None,
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "require_code_owner_reviews": False
        },
        "restrictions": None
    }
    r = requests.put(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code

def delete_p_rule(repo_name, branch_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}]/branches/{branch_name}/protection'
    r = requests.delete(url=url, headers=headers)
    return r.status_code # 204: successful

# 4. Teams
def list_org_teams():
    url = f'https://api.github.com/orgs/{org_name}/teams'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    return list([
        {
            'name': team['name'],
            'slug': team['slug'],
            'parent': team['parent'],
            'permission': team['permission']
        }
        for team in r.json()
    ])

def list_org_members():
    url = f'https://api.github.com/orgs/{org_name}/members'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    return list([
        {
            'id': member['id'],
            'name': member['login'],
        }
        for member in r.json()
    ])
    
def list_org_invitations():
    url = f'https://api.github.com/orgs/{org_name}/invitations'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    print(r.json())
    return list([
        {
            'id': invitation['id'],
            'email': invitation['email'],
        }
        for invitation in r.json()
    ])

def list_repo_teams(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/teams'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    return list([
        {
            'slug': team['slug'],
            'permission': team['permission']
        }
        for team in r.json()
    ])

def list_repo_members(repo_name):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/collaborators'
    r = requests.get(url=url, headers=headers)
    if 'message' in r.json() and r.json()['message'] == 'Not Found':
        return list()
    return list([
        {
            'name': member['login'],
            'role': member['role_name']
        }
        for member in r.json()
    ])

def add_team_to_repo(repo_name, team):
    url = f'https://api.github.com/orgs/{org_name}/teams/{team["slug"]}/repos/{org_name}/{repo_name}'
    if (team_permission.count(team['permission']) == 0):
        team['permission'] = 'pull'
    payload = {
        "permission": team["permission"]
    }
    r = requests.put(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code # 204: successful

def invite_mem_to_org(email):
    url = f'https://api.github.com/orgs/{org_name}/invitations'
    payload = {
        'email': email
    }
    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code # 201: created

def clear_invitation(invitation_id):
    url = f'https://api.github.com/orgs/{org_name}/invitations/{invitation_id}'
    r = requests.delete(url=url, headers=headers)
    return r.status_code # 204

# 5. Webhooks
def create_webhook(repo_name, webhook_url):
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/hooks'
    payload = {
        "name":"web",
        "active": True,
        "events": ["push"],
        "config":{
            "url": webhook_url,
            "insecure_ssl":"0"}
    }
    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    return r.status_code