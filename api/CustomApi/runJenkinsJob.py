from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.run_job import trigger_jenkins_job


class RunJenkinsJob(APIView):
    def post(self, request):
        job_url = request.data.get('job_url')
        params = request.data.get('params', {}) or None
        jenkins_user = request.data.get('jenkins_user')
        jenkins_token = request.data.get('jenkins_token')

        if not job_url:
            return Response({'error': 'job_url is required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth = (jenkins_user, jenkins_token) if jenkins_user and jenkins_token else None
        result = trigger_jenkins_job(job_url, params=params, auth=auth)

        if result['error']:
            return Response({'error': result['error']}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'status_code': result['status_code'],
            'message': 'Job triggered successfully.' if result['success'] else 'Unexpected response.',
        }, status=status.HTTP_200_OK)
