import os
import subprocess


GIT_REPO_URL = os.environ.get('GIT_REPO_URL', '')
GIT_USERNAME = os.environ.get('GIT_USERNAME', '')
GIT_PASSWORD = os.environ.get('GIT_PASSWORD', '')
GIT_BASE_BRANCH = os.environ.get('GIT_BASE_BRANCH', 'main')


def _build_authenticated_url(repo_url):
    """Inject username:password into the repo URL for HTTPS auth."""
    if GIT_USERNAME and GIT_PASSWORD and repo_url.startswith('https://'):
        repo_url = repo_url.replace('https://', f'https://{GIT_USERNAME}:{GIT_PASSWORD}@')
    return repo_url


def _run(cmd, cwd=None):
    """Run a shell command, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def clone_repo(destination):
    """Clone GIT_REPO_URL into destination folder."""
    url = _build_authenticated_url(GIT_REPO_URL)
    stdout, stderr, code = _run(['git', 'clone', url, destination])
    return {'success': code == 0, 'stdout': stdout, 'stderr': stderr}


def pull_latest(repo_path, branch=None):
    """Pull latest changes on the given branch (defaults to GIT_BASE_BRANCH)."""
    branch = branch or GIT_BASE_BRANCH
    _run(['git', 'checkout', branch], cwd=repo_path)
    stdout, stderr, code = _run(['git', 'pull', 'origin', branch], cwd=repo_path)
    return {'success': code == 0, 'stdout': stdout, 'stderr': stderr}


def get_current_branch(repo_path):
    """Return the currently checked-out branch name."""
    stdout, stderr, code = _run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_path)
    return {'success': code == 0, 'branch': stdout, 'stderr': stderr}


def get_latest_commit(repo_path):
    """Return the latest commit hash and message."""
    stdout, stderr, code = _run(
        ['git', 'log', '-1', '--pretty=format:%H|%s|%an|%ad', '--date=iso'],
        cwd=repo_path,
    )
    if code == 0 and stdout:
        parts = stdout.split('|', 3)
        return {
            'success': True,
            'hash': parts[0] if len(parts) > 0 else '',
            'message': parts[1] if len(parts) > 1 else '',
            'author': parts[2] if len(parts) > 2 else '',
            'date': parts[3] if len(parts) > 3 else '',
        }
    return {'success': False, 'stderr': stderr}


def list_branches(repo_path):
    """Return list of all remote branches."""
    stdout, stderr, code = _run(['git', 'branch', '-r'], cwd=repo_path)
    branches = [b.strip() for b in stdout.splitlines() if b.strip()] if code == 0 else []
    return {'success': code == 0, 'branches': branches, 'stderr': stderr}


def checkout_branch(repo_path, branch):
    """Checkout an existing branch."""
    stdout, stderr, code = _run(['git', 'checkout', branch], cwd=repo_path)
    return {'success': code == 0, 'stdout': stdout, 'stderr': stderr}


def create_branch(repo_path, branch_name, from_branch=None):
    """Create and checkout a new branch from from_branch (defaults to GIT_BASE_BRANCH)."""
    from_branch = from_branch or GIT_BASE_BRANCH
    _run(['git', 'checkout', from_branch], cwd=repo_path)
    stdout, stderr, code = _run(['git', 'checkout', '-b', branch_name], cwd=repo_path)
    return {'success': code == 0, 'stdout': stdout, 'stderr': stderr}


def commit_and_push(repo_path, message, branch=None):
    """Stage all changes, commit with message, and push to remote."""
    branch = branch or GIT_BASE_BRANCH
    _run(['git', 'add', '.'], cwd=repo_path)
    stdout, stderr, code = _run(['git', 'commit', '-m', message], cwd=repo_path)
    if code != 0:
        return {'success': False, 'stdout': stdout, 'stderr': stderr}
    stdout, stderr, code = _run(['git', 'push', 'origin', branch], cwd=repo_path)
    return {'success': code == 0, 'stdout': stdout, 'stderr': stderr}
