import os
from datetime import datetime

import requests
import typer

# Set terminal width environment variables at the very beginning
os.environ["COLUMNS"] = "100"  # This affects Click/Typer formatting
app = typer.Typer()


def get_contributors(owner: str, repo: str):
    contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(contributors_url)

    if response.status_code != 200:
        print(f"Failed to fetch contributors: {response.status_code}")
        return []

    contributors = response.json()
    sorted_contributors = sorted(contributors, key=lambda x: x['contributions'], reverse=True)
    return sorted_contributors


def get_last_contribution_date(owner: str, repo: str, username: str):
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


def mark_users(user: str, owner: str):
    match user:
        case _ if '[bot]' in user:
            return f"_{user.replace('[bot]', '')}_"
        case _ if user == owner:
            return f"**{user}**"
        case _:
            return user


def generate_markdown_table(owner: str, repo: str, contributors: str, top_n: int = 10_000, ):
    table = "| Username | Commits | Last<br>Contribution|\n"
    table += "|----------|---------------:|:------------------------:|\n"

    for contributor in contributors[:top_n]:
        username = contributor['login']
        contributions = contributor['contributions']
        last_contribution = get_last_contribution_date(owner, repo, username)
        table += f"| {mark_users(username, owner)} | {contributions} | {last_contribution} |\n"

    return table


@app.command()
def contributors(
        owner: str = typer.Option("hucker", help="Owner of the GitHub repository."),
        repo: str = typer.Option("ten8t", help="Repository name."),
        top: int = typer.Option(10_000, help="Number of top contributors to display (default is all)."),

):
    """
    Fetch contributors for OWNER/REPO and display a markdown table
    sorted by number of contributions.
    """
    contributors = get_contributors(owner, repo)
    if contributors:
        markdown_table = generate_markdown_table(owner, repo, contributors, top)
        typer.echo(markdown_table)
    else:
        typer.echo("No contributors found.", err=True)


if __name__ == "__main__":
    app()
