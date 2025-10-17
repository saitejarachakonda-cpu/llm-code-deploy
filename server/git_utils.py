# server/git_utils.py
import os
import shutil
import subprocess
import tempfile
from github import Github


def create_and_push_repo(local_dir: str, task_name: str, github_token: str, org: str | None = None):
    # Create repo using PyGithub
    gh = Github(github_token)
    user = gh.get_user()
    owner = org or user.login

    repo_name = f"{task_name}-{os.urandom(4).hex()}"

    if org:
        org_obj = gh.get_organization(org)
        repo = org_obj.create_repo(name=repo_name, private=False, auto_init=False)
    else:
        repo = user.create_repo(name=repo_name, private=False, auto_init=False)

    repo_url = repo.clone_url

    # initialize git in local_dir and push
    cwd = os.getcwd()
    try:
        # git init
        subprocess.check_call(["git", "init"], cwd=local_dir)
        subprocess.check_call(["git", "checkout", "-b", "main"], cwd=local_dir)
        subprocess.check_call(["git", "add", "."], cwd=local_dir)
        subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=local_dir)
        # set remote with token in URL (use https)
        remote_url = repo.clone_url.replace('https://', f'https://{github_token}@')
        subprocess.check_call(["git", "remote", "add", "origin", remote_url], cwd=local_dir)
        subprocess.check_call(["git", "push", "-u", "origin", "main"], cwd=local_dir)

        # enable GitHub Pages: publish from main branch / root
        repo.edit(has_pages=True)
        # GitHub's pages_url may take a moment to show; we build expected pages URL
        pages_url = f"https://{owner}.github.io/{repo_name}/"

        # get latest commit sha
        commit_sha = repo.get_commits()[0].sha

        return {"repo_url": repo.html_url, "commit_sha": commit_sha, "pages_url": pages_url}
    finally:
        os.chdir(cwd)
Sai Teja Rachakonda
