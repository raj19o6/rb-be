import re
from rest_framework.permissions import BasePermission

METHOD_PERMISSION_MAP = {
    'POST': 'add_',
    'GET': 'view_',
    'DELETE': 'delete_',
    'PUT': 'change_',
    'PATCH': 'change_',
}

ALLOWED_GROUPS = {
    'admin', 'sales', 'creator', 'editor', 'manager',
    'leader', 'employee', 'client', 'backoffice', 'support',
    'CompanyUser'
}

# These endpoints are controlled by their own view-level logic
BYPASS_ENDPOINTS = {
    'assignpermission', 'revokepermission', 'mypermissions',
    'myteam', 'assignments', 'issuperuser', 'changemypassword',
    'passwordreset', 'createuser'
}


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        path = request.path
        match = re.search(r'api/v1/([^/]+)', path)
        if not match:
            return True

        resource = match.group(1).lower()

        # Bypass custom endpoints — they handle their own permissions
        if resource in BYPASS_ENDPOINTS:
            return True

        method = request.method.upper()
        prefix = METHOD_PERMISSION_MAP.get(method, 'view_')
        codename = f"{prefix}{resource}"

        # Check if user has explicit permission assigned
        has_explicit = (
            request.user.has_perm(f"auth.{codename}") or
            request.user.has_perm(f"api.{codename}")
        )
        if has_explicit:
            return True

        # Fall back to group membership check
        user_groups = set(request.user.groups.values_list('name', flat=True))
        return bool(user_groups & ALLOWED_GROUPS)
