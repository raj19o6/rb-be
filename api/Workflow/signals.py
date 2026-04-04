# import os
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# JENKINS_URL = os.environ.get('JENKINS_URL', '')
# JENKINS_USER = os.environ.get('JENKINS_USER', '')
# JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN', '')
# JENKINS_JOB = os.environ.get('JENKINS_JOB', 'rb-bot')
# API_BASE_URL = os.environ.get('API_BASE_URL', '')


# @receiver(post_save, sender='api.Workflow')
# def trigger_jenkins_on_queued(sender, instance, created, **kwargs):
#     if instance.status != 'queued':
#         return

#     from api.run_job import trigger_jenkins_job
#     from api.Workflow.model import WorkflowReport

#     job_url = f"{JENKINS_URL}/job/{JENKINS_JOB}"
#     params = {
#         'WORKFLOW_ID': str(instance.id),
#         'WORKFLOW_JSON_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/download/",
#         'CALLBACK_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/report/",
#     }
#     auth = (JENKINS_USER, JENKINS_TOKEN) if JENKINS_USER and JENKINS_TOKEN else None

#     result = trigger_jenkins_job(job_url, params=params, auth=auth)

#     report, _ = WorkflowReport.objects.get_or_create(workflow=instance)
#     report.status = 'queued' if result['success'] else 'failed'
#     report.save(update_fields=['status'])



# import os
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# JENKINS_URL = os.environ.get('JENKINS_URL', 'https://jenkins.btacode.com')
# JENKINS_USER = os.environ.get('JENKINS_USER', '')
# JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN', '')
# JENKINS_JOB = os.environ.get('JENKINS_JOB', 'rb-bot-runner')  # Changed from 'rb-bot'
# API_BASE_URL = os.environ.get('API_BASE_URL', 'http://172.17.84.253:8000')
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # Added


# @receiver(post_save, sender='api.Workflow')
# def trigger_jenkins_on_queued(sender, instance, created, **kwargs):
#     if instance.status != 'queued':
#         return

#     from api.run_job import trigger_jenkins_job
#     from api.Workflow.model import WorkflowReport

#     # Fixed job URL - removed /view/rb-bot/ part
#     job_url = f"{JENKINS_URL}/job/{JENKINS_JOB}/buildWithParameters"

#     params = {
#         'WORKFLOW_ID': str(instance.id),
#         'WORKFLOW_JSON_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/download/",
#         'CALLBACK_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/report/",
#         'OPENAI_API_KEY': OPENAI_API_KEY,  # Added
#     }

#     auth = (JENKINS_USER, JENKINS_TOKEN) if JENKINS_USER and JENKINS_TOKEN else None

#     print(f":rocket: Triggering Jenkins job: {job_url}")
#     print(f":package: Parameters: {params}")

#     result = trigger_jenkins_job(job_url, params=params, auth=auth)

#     print(f":white_check_mark: Jenkins result: {result}")

#     report, _ = WorkflowReport.objects.get_or_create(workflow=instance)
#     report.status = 'queued' if result['success'] else 'failed'
#     report.jenkins_build_url = result.get('build_url', '')  # Added to track build
#     report.save(update_fields=['status', 'jenkins_build_url'])


import os
from django.db.models.signals import post_save
from django.dispatch import receiver

JENKINS_URL = os.environ.get('JENKINS_URL', 'https://jenkins.btacode.com')
JENKINS_USER = os.environ.get('JENKINS_USER', '')
JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN', '')
JENKINS_JOB = os.environ.get('JENKINS_JOB', 'rb-bot-runner')
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://8nh48kbv-8000.inc1.devtunnels.ms')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')


@receiver(post_save, sender='api.Workflow')
def trigger_jenkins_on_queued(sender, instance, created, **kwargs):
    if instance.status != 'queued':
        return

    from api.run_job import trigger_jenkins_job
    from api.Workflow.model import WorkflowReport

    # Job URL without /buildWithParameters (your function adds it)
    job_url = f"{JENKINS_URL}/job/{JENKINS_JOB}"

    params = {
        'WORKFLOW_ID': str(instance.id),
        'WORKFLOW_JSON_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/download/",
        'CALLBACK_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/report/",
        'OPENAI_API_KEY': OPENAI_API_KEY,
    }

    auth = (JENKINS_USER, JENKINS_TOKEN) if JENKINS_USER and JENKINS_TOKEN else None

    print(f":rocket: Triggering Jenkins job: {job_url}")
    print(f":package: Parameters: {params}")
    print(f":closed_lock_with_key: Auth user: {JENKINS_USER if JENKINS_USER else 'None'}")

    result = trigger_jenkins_job(job_url, params=params, auth=auth)

    print(f":white_check_mark: Jenkins result: {result}")

    report, _ = WorkflowReport.objects.get_or_create(workflow=instance)

    if result['success']:
        report.status = 'queued'
        print(f":white_check_mark: Workflow {instance.id} queued successfully")
    else:
        report.status = 'failed'
        print(f":x: Workflow {instance.id} failed: {result.get('error')}")

    report.save(update_fields=['status'])