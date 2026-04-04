from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from api.Requests.model import Requests
from api.Requests.serializer import RequestsSerializer
from api.RequestsHistory.model import RequestsHistory


class RequestsViewset(ModelViewSet):
    serializer_class = RequestsSerializer

    def _is_manager(self, user):
        return 'manager' in [g.lower() for g in user.groups.values_list('name', flat=True)]

    def _is_client(self, user):
        return 'client' in [g.lower() for g in user.groups.values_list('name', flat=True)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Requests.objects.select_related('requested_by', 'assigned_to', 'bot').all()
        if self._is_manager(user):
            # Manager sees all requests from clients under them
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return Requests.objects.select_related('requested_by', 'assigned_to', 'bot').filter(
                requested_by_id__in=client_ids
            )
        # Client sees only their own requests
        return Requests.objects.select_related('requested_by', 'assigned_to', 'bot').filter(
            requested_by=user
        )

    def perform_create(self, serializer):
        user = self.request.user
        # Only clients can create requests
        if user.is_superuser or self._is_manager(user):
            raise PermissionDenied('Only clients can submit bot requests.')
        serializer.save(requested_by=user)

    def perform_update(self, serializer):
        user = self.request.user
        # Clients cannot update status — only manager/superuser can
        if self._is_client(user):
            raise PermissionDenied('Clients cannot update requests.')
        serializer.save()

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or self._is_manager(user)):
            raise PermissionDenied('Only managers or superusers can approve requests.')

        req = self.get_object()
        if req.status != 'pending':
            return Response({'error': f'Cannot approve a request with status: {req.status}'}, status=400)
        if not req.bot:
            return Response({'error': 'Request has no bot attached.'}, status=400)

        # Auto-create BotAllotment
        from api.BotAllotments.model import BotAllotments
        allotment, created = BotAllotments.objects.get_or_create(
            bot=req.bot,
            user=req.requested_by,
            defaults={'allotted_by': user}
        )

        # Auto-create unpaid Billing
        from api.Billing.model import Billing
        from django.utils import timezone
        billing, _ = Billing.objects.get_or_create(
            user=req.requested_by,
            bot=req.bot,
            status='unpaid',
            defaults={
                'amount': 0,
                'price_per_action': 0.10,
                'billing_date': timezone.now().date(),
            }
        )

        # Update request
        previous_status = req.status
        req.status = 'approved'
        req.assigned_to = user
        req.save(update_fields=['status', 'assigned_to'])

        RequestsHistory.objects.create(
            request=req,
            changed_by=user,
            previous_status=previous_status,
            new_status='approved',
            note='Request approved. Bot allotted and billing created.',
        )

        return Response({
            'message': 'Request approved.',
            'request_id': str(req.id),
            'allotment_id': str(allotment.id),
            'allotment_created': created,
            'billing_id': str(billing.id),
            'next_step': 'Set billing amount via PATCH /api/v1/billing/{billing_id}/'
        })

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or self._is_manager(user)):
            raise PermissionDenied('Only managers or superusers can reject requests.')

        req = self.get_object()
        if req.status != 'pending':
            return Response({'error': f'Cannot reject a request with status: {req.status}'}, status=400)

        reason = request.data.get('reason', '')
        previous_status = req.status
        req.status = 'rejected'
        req.rejection_reason = reason
        req.assigned_to = user
        req.save(update_fields=['status', 'rejection_reason', 'assigned_to'])

        RequestsHistory.objects.create(
            request=req,
            changed_by=user,
            previous_status=previous_status,
            new_status='rejected',
            note=reason,
        )

        return Response({
            'message': 'Request rejected.',
            'request_id': str(req.id),
            'reason': reason,
        })
