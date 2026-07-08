from openai import OpenAI
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

def generate_summary(commits):
    if not commits:
        return "No commits today. Rest day or planning day!"

    commit_lines = ""
    for c in commits:
        commit_lines = commit_lines + "- [" + c["repo"] + "] " + c["message"] + "\n"

    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPEN_ROUTER_BASE_URL')
    )

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": "You are a developer journal bot. Given today's GitHub commits, write a short WhatsApp-friendly daily summary in 4-6 lines. Be conversational, not robotic. Mention what was built and why it matters.\n\nCommits:\n" + commit_lines + "\nWrite the summary now:"
            }
        ]
    )

    return response.choices[0].message.content

def send_whatsapp(summary):
    instance_id = os.getenv('ULTRAMSG_INSTANCE')
    token = os.getenv('ULTRAMSG_TOKEN')
    number = os.getenv('WHATSAPP_NUMBER')

    url = f'https://api.ultramsg.com/{instance_id}/messages/chat'
    payload = {
        "token": token,
        "to": number,
        "body": summary
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print("WhatsApp message sent successfully!")
    else:
        print("Failed to send. Status: " + str(response.status_code))
        print(response.text)

if __name__ == "__main__":
    commits = fetch_all_commits()
    summary = generate_summary(commits)
    print(summary)
    send_whatsapp(summary)