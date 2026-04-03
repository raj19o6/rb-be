from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.User.model
        import api.UserProfile.model
        import api.HierarchyPermission.model
        import api.CustomRole.model

        # Requests group
        import api.Requests.model
        import api.RequestsHistory.model
        import api.RequestFiles.model

        # Bot group
        import api.Bot.model
        import api.BotAllotments.model
        import api.BotMaintainance.model
        import api.BotPrereq.model
        import api.BotFunctions.model

        # Billing / Executions group
        import api.Billing.model
        import api.Executions.model
        import api.ExecutionReports.model

        # Doc group
        import api.DocCategory.model
        import api.DocFields.model
        import api.FieldKeyMap.model

        # Misc
        import api.Regex.model
        import api.ResponsePrereq.model
        import api.Credentials.model
        import api.Payment.model

        # Block / Budget / Bugs
        import api.RunBlockReasons.model
        import api.Budget.model
        import api.Budget.history_model
        import api.Bugs.model
        import api.Bugs.history_model

        # Notifications / Logs
        import api.Notification.model
        import api.APITestLogs.model

        # Signals
        import api.Budget.signals
        import api.Payment.signals
        import api.Executions.signals
