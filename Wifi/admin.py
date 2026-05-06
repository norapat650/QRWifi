from django.contrib import admin
from .models import WifiUser, WifiAccessLog


@admin.register(WifiUser)
class WifiUserAdmin(admin.ModelAdmin):
    list_display = ("line_user_id", "first_name", "phone", "created_at")
    search_fields = ("line_user_id", "first_name", "phone")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_filter = ("created_at",)


@admin.register(WifiAccessLog)
class WifiAccessLogAdmin(admin.ModelAdmin):
    list_display = ("line_user_id", "action", "ip_address", "created_at")
    search_fields = ("line_user_id", "action", "ip_address", "user_agent")
    list_filter = ("action", "created_at")