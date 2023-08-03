from api import api_github

webhook_urls = None
default_teams = None
default_branches = ['main', 'production']

# setting global variable
def list_all_repos():
    return api_github.list_all_repos()
    
def set_token(token):    
    api_github.headers['Authorization'] = f'Bearer {token}'    

def set_org_name(org_name):    
    api_github.org_name = org_name

# 1. create repo with config
def create_a_repo(new_repo):
    repo_name = new_repo['name']
    msg = f'--> Repo {repo_name}'
    status_code = api_github.create_repo(new_repo)
    if (status_code == 201):
        msg += ' created successfully!'
    else:
        msg += ' created failed!'

    # add_teams(repo_name, default_teams)
    # create_webhooks(repo_name)
    
    return msg

# 2. Create branch `production`
def list_lacking_branch_repos(repos_name):
    lacking_repos = list()
    for repo_name in repos_name:
        status_code = api_github.get_branch(repo_name, 'production')
        if (status_code == 404):
            lacking_repos.append(repo_name)
    return lacking_repos

def create_branch(repo_name):    
    revision_id = api_github.find_revision(repo_name)
    if (revision_id == "REPO_EMPTY"):
        print(f"Warning: Repo {repo_name} is empty. Creating branch `main`...")
        tree_sha = api_github.create_dummy_file(repo_name)
        commit_sha = api_github.create_init_commit(repo_name, tree_sha)
        status_code = api_github.create_init_branch(repo_name, commit_sha)
        if (status_code == 200):
            print("   |-- Branch `main` created!")
            revision_id = api_github.find_revision(repo_name)
        else:
            return "   |-- Error: Branch `main` cannot created!"
    status_code = api_github.create_branch(repo_name, 'production', revision_id) 
    if (status_code == 201):
        return "   |-- Branch `production` created!"
    else:
        return "   |-- Error: Branch `production` cannot created!"  

# 3. Add teams
def list_teams(repo_name):
    if (repo_name == "[[org]]"):
        return list([
            team['slug']
            for team in api_github.list_org_teams()
        ])
    else:
        return api_github.list_repo_teams(repo_name)

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
        msg = f'   |-- Add team {team["slug"]} as {team["permission"]}'
        status_code = api_github.add_team_to_repo(repo_name, team)
        if (status_code == 204):
            msg += ' successful!'
        else:
            msg += ' failed!'
        print(msg)

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

def apply_branch_rule(repo):
    # repo_name = repo['name']
    # branches = repo['branches']
    branches = ['main', 'production']
    for branch in branches:
        msg = f'   |--`{branch}`: updated '
        status_code = api_github.apply_p_rule(repo, branch)
        if (status_code == 200):
            msg += 'successfully!'
        else:
            msg += 'failed!'
        print(msg)

# 5. Create webhooks for repo
def create_webhooks(repo_name):
    for url in webhook_urls:
        msg = f'   |--`{url}`: created '
        status_code = api_github.create_webhook(repo_name, url)
        if (status_code == 201):
            msg += 'successfully!'
        else:
            msg += 'failed!'
        print(msg)