from rest_framework.viewsets import ModelViewSet
from api.ExecutionReports.model import ExecutionReports
from api.ExecutionReports.serializer import ExecutionReportsSerializer


class ExecutionReportsViewset(ModelViewSet):
    serializer_class = ExecutionReportsSerializer

    def get_queryset(self):
        user = self.request.user
        qs = ExecutionReports.objects.select_related(
            'execution__bot', 'execution__executed_by', 'execution__request'
        )
        if user.is_superuser:
            return qs.all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return qs.filter(execution__executed_by_id__in=client_ids)
        return qs.filter(execution__executed_by=user)
