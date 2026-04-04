import os
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='api.Workflow')
def trigger_jenkins_on_queued(sender, instance, created, **kwargs):
    if instance.status != 'queued':
        return

    from api.run_job import trigger_jenkins_job
    from api.Workflow.model import WorkflowReport

    JENKINS_URL = os.environ.get('JENKINS_URL', 'https://jenkins.btacode.com')
    JENKINS_USER = os.environ.get('JENKINS_USER', '')
    JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN', '')
    JENKINS_JOB = os.environ.get('JENKINS_JOB', 'rb-bot-runner')
    API_BASE_URL = os.environ.get('API_BASE_URL', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    job_url = f"{JENKINS_URL}/job/{JENKINS_JOB}"

    params = {
        'WORKFLOW_ID': str(instance.id),
        'WORKFLOW_JSON_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/download/",
        'CALLBACK_URL': f"{API_BASE_URL}/api/v1/workflows/{instance.id}/report/",
        'OPENAI_API_KEY': OPENAI_API_KEY,
    }

    auth = (JENKINS_USER, JENKINS_TOKEN) if JENKINS_USER and JENKINS_TOKEN else None

    print(f"🚀 Triggering Jenkins job: {job_url}")
    print(f"📦 Parameters: { {k: v for k, v in params.items() if k != 'OPENAI_API_KEY'} }")
    print(f"🔑 Auth user: {JENKINS_USER if JENKINS_USER else 'None'}")

    result = trigger_jenkins_job(job_url, params=params, auth=auth)

    print(f"✅ Jenkins result: {result}")

    report, _ = WorkflowReport.objects.get_or_create(workflow=instance)

    if result['success']:
        report.status = 'queued'
        print(f"✅ Workflow {instance.id} queued successfully")
    else:
        report.status = 'failed'
        print(f"❌ Workflow {instance.id} failed: {result.get('error')}")

    report.save(update_fields=['status'])
