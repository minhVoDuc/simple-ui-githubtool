from api import api_github

webhook_urls = list()
default_teams = list()
default_branches = ['main', 'production']

# relevant function
def list_all_repos():
    repos = api_github.list_all_repos()
    return repos

## check empty
def is_empty_token():
    return 'Authorization' not in api_github.headers \
        or api_github.headers['Authorization'] == ""
        
def is_empty_org_name():
    return api_github.org_name is None \
        or api_github.org_name == ""
        
def is_empty_default_team():
    return len(default_teams) == 0
    
def is_empty_webhook():
    return len(webhook_urls) == 0    

## set global variable
def set_token(token):    
    api_github.headers['Authorization'] = f'Bearer {token}'    

def set_org_name(org_name):    
    api_github.org_name = org_name
    
def set_default_team(teams):
    default_teams = []
    for team in teams:
        default_teams.append(
            {
                'slug': team['team_name'],
                'permission': 'pull'
            }
        )

def set_default_webhook(urls):
    webhook_urls = urls
    print("updating", webhook_urls)

# 1. Repo
def create_a_repo(new_repo):
    repo_name = new_repo['name']
    msg = f'--> Repo {repo_name}'
    status_code = api_github.create_repo(new_repo)
    if (status_code == 201):
        msg += ' created successfully!'
    else:
        msg += ' created failed!'
    return msg

# 2. Branch
def list_lacking_branch_repos(repos_name, branch):
    lacking_repos = list()
    for repo_name in repos_name:
        status_code = api_github.get_branch(repo_name, branch)
        if (status_code == 404):
            lacking_repos.append(repo_name)
    return lacking_repos

def create_branch(repo_name, branch):    
    revision_id = api_github.find_revision(repo_name)
    if (revision_id == "REPO_EMPTY"):
        print(f"Warning: Repo {repo_name} is empty. Creating branch `main`...")
        tree_sha = api_github.create_dummy_file(repo_name)
        commit_sha = api_github.create_init_commit(repo_name, tree_sha)
        status_code = api_github.create_init_branch(repo_name, commit_sha)
        if (status_code == 200):
            print(f"   |-- Branch `{branch}` created!")
            revision_id = api_github.find_revision(repo_name)
        else:
            return f"   |-- Error: Branch `{branch}` cannot created!"
    if (branch != 'main'):
        status_code = api_github.create_branch(repo_name, branch, revision_id) 
        if (status_code == 201):
            return f"   |-- Branch `{branch}` created!"
        else:
            return f"   |-- Error: Branch `{branch}` cannot created!"  

# 3. Collaborator
def list_teams(repo_name):
    if (repo_name == "[[org]]"):
        return api_github.list_org_teams()
    return api_github.list_repo_teams(repo_name)

def list_members(repo_name):
    if (repo_name == "[[org]]"):
        return api_github.list_org_members()
    return api_github.list_repo_members(repo_name)

def list_invitations(repo_name):
    if (repo_name == "[[org]]"):
        return api_github.list_org_invitations()
    return True

def set_teams():
    teams_num = int(input('> How many teams will be added: '))
    teams = list()
    for _ in range(teams_num):
        team = dict()
        team['slug'] = input('Enter team name: ')
        team['permission'] = input('Enter team\'s permission [`pull`, `triage`, `push`, `maintain` or `admin`]: ')
        teams.append(team)
    return teams

def add_teams(repo_name, teams):
    for team in teams:
        status_code = api_github.add_team_to_repo(repo_name, team)
        if status_code != 204:
            return "Error"
    return None
        
def remove_teams(repo_name, teams):
    for team_name in teams:
        status_code = api_github.delete_team_from_repo(repo_name, team_name)
        if status_code != 204:
            return "Error"
    return None

def invite_members(emails):
    for email in emails:
        api_github.invite_mem_to_org(email)
        
def cancel_invitations(invitation_id):
    status_code = api_github.clear_invitation(invitation_id)
    return status_code

# 4. Modify protection branch rule
def list_lacking_rule_repos(repos_name):
    lacking_repos = list()
    for repo_name in repos_name:
        branches = list()
        for branch in default_branches:
            if (api_github.get_branch(repo_name, branch) != 404):
                branches.append(branch)
        lacking_branches = list()
        for branch in branches:
            status_code = api_github.get_p_rule(repo_name, branch)
            if (status_code == 404): 
                lacking_branches.append(branch)
        if (len(lacking_branches) > 0):
            lacking_repos.append(
                {
                    "name": repo_name,
                    "branches": lacking_branches
                }
            )
    return lacking_repos

def apply_branch_rule(repo_name, branches):
    # repo_name = repo['name']
    # branches = repo['branches']
    # branches = ['main', 'production']
    for branch in branches:
        status_code = api_github.apply_p_rule(repo_name, branch)
        print(status_code)
        if status_code != 200:
            return f"[ERR] Cannot apply branch protection rule to {repo_name}!"
    return None

def delete_branch_rule(repo_name, branches):
    for branch in branches:
        status_code = api_github.delete_p_rule(repo_name, branch)
        print(status_code)
        if status_code != 204:
            return f"[ERR] Cannot apply branch protection rule to {repo_name}!"
    return None

# 5. Create webhooks for repo
def create_repo_webhook(repo_name, url):
    status_code = api_github.create_webhook(repo_name, url)
    if status_code != 201:
        return "ERROR"    
    return None