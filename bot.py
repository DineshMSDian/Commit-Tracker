import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load env variables
load_dotenv()

GITHUB_TOKEN=os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_todays_commits(repo_name):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    since = today.isoformat()

    url = f'https://api.github.com/repos/{repo_name}/commits?since={since}'
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return []
    
    commits = response.json()
    if not isinstance(commits, list):
        return []
    
    result  = []

    for c in commits:
        commit_info = {
            'repo': repo_name,
            'message': c['commit']['author']['date']
        }

        result.append(commit_info)

    return result

def get_all_repos():
    url = "https://api.github.com/user/repos?per_page=100&type=owner"
    response = requests.get(url, headers=HEADERS)
    repos = response.json()

    repo_names = []

    for repo in repos:
        repo_names.append(repo["full_name"])

    return repo_names

def fetch_all_commits():
    repos = get_all_repos()
    all_commits = []
    for repo in repos:
        commits = get_todays_commits(repo)
        all_commits.extend(commits)
    return all_commits


if __name__ == "__main__":
    commits = fetch_all_commits()
    if commits:
        for c in commits:
            print(f"[{c['repo']}] {c['message']} @ {c['time']}")
    else:
        print("No commits today.")