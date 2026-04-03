from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.RunBlockReasons.model import RunBlockReasons


class BulkUpdateRunBlockReasons(APIView):
    def patch(self, request):
        updates = request.data  # expects list of {id, is_active, reason}

        if not isinstance(updates, list) or not updates:
            return Response(
                {'error': 'Provide a non-empty list of objects with id and fields to update.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_ids = []
        errors = []

        for item in updates:
            record_id = item.get('id')
            if not record_id:
                errors.append({'error': 'id is required', 'item': item})
                continue

            fields = {k: v for k, v in item.items() if k != 'id' and k in ('is_active', 'reason')}
            if not fields:
                errors.append({'error': 'No valid fields to update', 'id': record_id})
                continue

            updated = RunBlockReasons.objects.filter(pk=record_id).update(**fields)
            if updated:
                updated_ids.append(record_id)
            else:
                errors.append({'error': 'Record not found', 'id': record_id})

        return Response({'updated': updated_ids, 'errors': errors}, status=status.HTTP_200_OK)
