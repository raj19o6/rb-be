from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.Bot.model import Bot
from api.Bot.serializer import BotSerializer


class BotViewset(ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Bot.objects.select_related('created_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return Bot.objects.select_related('created_by').all()
        # Client sees only allotted bots
        return Bot.objects.select_related('created_by').filter(
            allotments__user=user
        ).distinct()

    @action(detail=True, methods=['get'], url_path='prerequisites')
    def prerequisites(self, request, pk=None):
        """Client fetches what fields are required before submitting a request for this bot"""
        from api.BotPrereq.model import BotPrereq
        from api.BotPrereq.serializer import BotPrereqSerializer
        from django.shortcuts import get_object_or_404
        # Use base Bot queryset — not role-filtered — so clients can view prereqs before being allotted
        bot = get_object_or_404(Bot, pk=pk)
        prereqs = BotPrereq.objects.filter(bot=bot)
        serializer = BotPrereqSerializer(prereqs, many=True)
        return Response({
            'bot_id': str(bot.id),
            'bot_name': bot.name,
            'prerequisites': serializer.data,
            'credential_fields': {
                'username': 'Login username (leave empty for public websites)',
                'password': 'Login password (leave empty for public websites)',
                'extra_data': {
                    'target_url': 'URL of the website/webapp to scan (required)',
                    'target_type': 'webapp or website',
                    'login_url': 'Login page URL if different from target_url (optional)',
                    'otp_required': 'true or false (optional)',
                    'notes': 'Any additional notes (optional)',
                }
            }
        })

    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        """All active bots — clients use this to browse and request bots"""
        bots = Bot.objects.filter(status='active').select_related('created_by')
        serializer = self.get_serializer(bots, many=True)
        return Response(serializer.data)

    def http_method_not_allowed(self, request, *args, **kwargs):
        user = request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups and request.method not in ('GET', 'HEAD', 'OPTIONS'):
            from rest_framework.response import Response
            return Response({'error': 'Clients have read-only access to bots.'}, status=403)
        return super().http_method_not_allowed(request, *args, **kwargs)
