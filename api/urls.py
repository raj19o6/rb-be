from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.User.view import UserViewset
from api.Role.view import RoleViewset
from api.Permission.view import PermissionViewset
from api.UserProfile.view import UserProfileViewset
from api.ChangeMyPassword.view import ChangeMyPasswordView
from api.ForgetPassword.view import PasswordResetRequestView
from api.IsSuperUser.view import CheckUserType
from api.CreateUser.views import CreateUserAPI
from api.HierarchyPermission.view import (
    AssignPermissionView, RevokePermissionView,
    MyPermissionsView, MyTeamView, AssignmentListView
)

router = DefaultRouter()
router.register('user', UserViewset, basename='user')
router.register('role', RoleViewset, basename='role')
router.register('permission', PermissionViewset, basename='permission')
router.register('userprofile', UserProfileViewset, basename='userprofile')
router.register('assignments', AssignmentListView, basename='assignments')

schema_view = get_schema_view(
    openapi.Info(title='API', default_version='v1'),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('changeMyPassword/', ChangeMyPasswordView.as_view()),
    path('passwordReset/', PasswordResetRequestView.as_view()),
    path('isSuperUser/', CheckUserType.as_view()),
    path('createUser/', CreateUserAPI.as_view()),
    path('assignPermission/', AssignPermissionView.as_view()),
    path('revokePermission/', RevokePermissionView.as_view()),
    path('myPermissions/', MyPermissionsView.as_view()),
    path('myTeam/', MyTeamView.as_view()),
]
