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

from api.CustomRole.view import CustomRoleViewset

from api.Requests.view import RequestsViewset
from api.RequestsHistory.view import RequestsHistoryViewset
from api.RequestFiles.view import RequestFilesViewset
from api.Bot.view import BotViewset
from api.BotAllotments.view import BotAllotmentsViewset
from api.BotMaintainance.view import BotMaintainanceViewset
from api.BotPrereq.view import BotPrereqViewset
from api.BotFunctions.view import BotFunctionsViewset
from api.Billing.view import BillingViewset
from api.Executions.view import ExecutionsViewset
from api.ExecutionReports.view import ExecutionReportsViewset
from api.DocCategory.view import DocCategoryViewset
from api.DocFields.view import DocFieldsViewset
from api.FieldKeyMap.view import FieldKeyMapViewset
from api.Regex.view import RegexViewset
from api.ResponsePrereq.view import ResponsePrereqViewset
from api.Credentials.view import CredentialsViewset
from api.Payment.view import PaymentViewset
from api.RunBlockReasons.view import RunBlockReasonsViewset
from api.Budget.view import BudgetViewset
from api.Bugs.view import BugsViewset
from api.Notification.view import NotificationViewset
from api.APITestLogs.view import APITestLogsViewset

from api.CustomApi.getBotAllotmentsByUser import GetBotAllotmentsByUser
from api.CustomApi.getRequestsHistoryByUser import GetRequestsHistoryByUser
from api.CustomApi.getResponsePrereqByUser import GetResponsePrereqByUser
from api.CustomApi.getRequestWithCredentials import GetRequestWithCredentials
from api.CustomApi.getTotalPriceForExecution import GetTotalPriceForExecution
from api.CustomApi.runJenkinsJob import RunJenkinsJob
from api.CustomApi.bulkUpdateRunBlockReasons import BulkUpdateRunBlockReasons
from api.CustomApi.getBudget import GetBudget
from api.CustomApi.manageMaintenanceReason import ManageMaintenanceReason
from api.CustomApi.getRegexList import GetRegexList
from api.CustomApi.getDocCategoriesWithDetails import GetDocCategoriesWithDetails
from api.CustomApi.getDashboard import GetDashboard

router = DefaultRouter()
router.register('user', UserViewset, basename='user')
router.register('role', RoleViewset, basename='role')
router.register('permission', PermissionViewset, basename='permission')
router.register('userprofile', UserProfileViewset, basename='userprofile')
router.register('assignments', AssignmentListView, basename='assignments')
router.register('customrole', CustomRoleViewset, basename='customrole')
router.register('requests', RequestsViewset, basename='requests')
router.register('requestshistory', RequestsHistoryViewset, basename='requestshistory')
router.register('requestfiles', RequestFilesViewset, basename='requestfiles')
router.register('bot', BotViewset, basename='bot')
router.register('botallotments', BotAllotmentsViewset, basename='botallotments')
router.register('botmaintainance', BotMaintainanceViewset, basename='botmaintainance')
router.register('botprereq', BotPrereqViewset, basename='botprereq')
router.register('botfunctions', BotFunctionsViewset, basename='botfunctions')
router.register('billing', BillingViewset, basename='billing')
router.register('executions', ExecutionsViewset, basename='executions')
router.register('executionreports', ExecutionReportsViewset, basename='executionreports')
router.register('doccategory', DocCategoryViewset, basename='doccategory')
router.register('docfields', DocFieldsViewset, basename='docfields')
router.register('fieldkeymap', FieldKeyMapViewset, basename='fieldkeymap')
router.register('regex', RegexViewset, basename='regex')
router.register('responseprereq', ResponsePrereqViewset, basename='responseprereq')
router.register('credentials', CredentialsViewset, basename='credentials')
router.register('payment', PaymentViewset, basename='payment')
router.register('runblockreasons', RunBlockReasonsViewset, basename='runblockreasons')
router.register('budget', BudgetViewset, basename='budget')
router.register('bugs', BugsViewset, basename='bugs')
router.register('notification', NotificationViewset, basename='notification')
router.register('apitestlogs', APITestLogsViewset, basename='apitestlogs')

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

    # Custom API endpoints
    path('getBotAllotmentsByUser/<str:user_id>/', GetBotAllotmentsByUser.as_view()),
    path('getRequestsHistoryByUser/<str:user_id>/', GetRequestsHistoryByUser.as_view()),
    path('getResponsePrereqByUser/<str:user_id>/', GetResponsePrereqByUser.as_view()),
    path('getRequestWithCredentials/', GetRequestWithCredentials.as_view()),
    path('getTotalPriceForExecution/', GetTotalPriceForExecution.as_view()),
    path('getTotalPriceForExecution/<str:user_id>/', GetTotalPriceForExecution.as_view()),
    path('runJenkinsJob/', RunJenkinsJob.as_view()),
    path('bulkUpdateRunBlockReasons/', BulkUpdateRunBlockReasons.as_view()),
    path('getBudget/', GetBudget.as_view()),
    path('underMaintenance/', ManageMaintenanceReason.as_view()),
    path('getRegexList/', GetRegexList.as_view()),
    path('getDocCategoriesWithDetails/', GetDocCategoriesWithDetails.as_view()),
    path('getDashboard/', GetDashboard.as_view()),
]
