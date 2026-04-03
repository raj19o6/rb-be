import os
import requests
import urllib3
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

VERIFY_SSL = os.environ.get('VERIFY_SSL', 'false').lower() == 'true'

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_jenkins_session():
    session = requests.Session()
    if VERIFY_SSL:
        import certifi
        session.verify = certifi.where()
    else:
        session.verify = False
    return session


class RunJenkinsJob(APIView):
    def post(self, request):
        job_url = request.data.get('job_url')
        params = request.data.get('params', {})
        jenkins_user = request.data.get('jenkins_user')
        jenkins_token = request.data.get('jenkins_token')

        if not job_url:
            return Response({'error': 'job_url is required.'}, status=status.HTTP_400_BAD_REQUEST)

        session = get_jenkins_session()

        auth = (jenkins_user, jenkins_token) if jenkins_user and jenkins_token else None

        try:
            if params:
                response = session.post(
                    f"{job_url.rstrip('/')}/buildWithParameters",
                    params=params,
                    auth=auth,
                )
            else:
                response = session.post(
                    f"{job_url.rstrip('/')}/build",
                    auth=auth,
                )

            return Response({
                'status_code': response.status_code,
                'message': 'Job triggered successfully.' if response.status_code in (200, 201) else 'Unexpected response.',
            }, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
