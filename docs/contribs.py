from datetime import datetime

import requests


def get_contributors(owner, repo):
    contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(contributors_url)

    if response.status_code != 200:
        print(f"Failed to fetch contributors: {response.status_code}")
        return []

    contributors = response.json()
    sorted_contributors = sorted(contributors, key=lambda x: x['contributions'], reverse=True)
    return sorted_contributors


def get_last_contribution_date(owner, repo, username):
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {'author': username, 'per_page': 1}
    response = requests.get(commits_url, params=params)

    if response.status_code != 200:
        return 'N/A'

    commits = response.json()
    if commits:
        last_date = commits[0]['commit']['author']['date']
        # Convert to readable format
        date = datetime.strptime(last_date, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%Y-%m-%d")
    else:
        return 'N/A'


def generate_markdown_table(owner, repo, contributors):
    table = "| Username | Contributions | Last<br>Contribution|\n"
    table += "|----------|---------------|------------------------|\n"

    for contributor in contributors:
        username = contributor['login']
        contributions = contributor['contributions']
        last_contribution = get_last_contribution_date(owner, repo, username)
        table += f"| {username} | {contributions} | {last_contribution} |\n"

    return table


def main():
    owner = 'hucker'  # Replace with correct owner name
    repo = 'ten8t'  # Replace with correct repository name

    contributors = get_contributors(owner, repo)
    if contributors:
        markdown_table = generate_markdown_table(owner, repo, contributors)
        print(markdown_table)
    else:
        print("No contributors found.")


if __name__ == "__main__":
    main()
