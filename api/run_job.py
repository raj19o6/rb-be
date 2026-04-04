import os
import requests
import urllib3

VERIFY_SSL = os.environ.get('VERIFY_SSL', 'false').lower() == 'true'

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_session():
    """
    Return a requests.Session with SSL verification configured via VERIFY_SSL env var.
    - VERIFY_SSL=true  → verifies using certifi CA bundle (production)
    - VERIFY_SSL=false → disables SSL verification (dev/staging)
    """
    session = requests.Session()
    if VERIFY_SSL:
        import certifi
        session.verify = certifi.where()
    else:
        session.verify = False
    return session


def trigger_jenkins_job(job_url, params=None, auth=None):
    """
    Trigger a Jenkins job via POST.

    Args:
        job_url (str): Base URL of the Jenkins job.
        params (dict): Optional build parameters for parameterized jobs.
        auth (tuple): Optional (username, token) for Jenkins auth.

    Returns:
        dict: {'success': bool, 'status_code': int, 'error': str|None}
    """
    session = get_session()
    url = f"{job_url.rstrip('/')}/buildWithParameters" if params else f"{job_url.rstrip('/')}/build"

    try:
        response = session.post(url, params=params or {}, auth=auth, allow_redirects=False)
        return {
            'success': response.status_code in (200, 201, 302),
            'status_code': response.status_code,
            'error': None,
        }
    except requests.exceptions.SSLError as e:
        return {'success': False, 'status_code': None, 'error': f'SSL error: {e}'}
    except requests.exceptions.ConnectionError as e:
        return {'success': False, 'status_code': None, 'error': f'Connection error: {e}'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'status_code': None, 'error': str(e)}
