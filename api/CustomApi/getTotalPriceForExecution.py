from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from api.ExecutionReports.model import ExecutionReports


class GetTotalPriceForExecution(APIView):
    def get(self, request, user_id=None):
        qs = ExecutionReports.objects.all()

        if user_id:
            qs = qs.filter(execution__executed_by_id=user_id)

        total = qs.aggregate(total_price=Sum('total_price'))['total_price'] or 0

        return Response({
            'user_id': user_id,
            'total_price': total,
        })
