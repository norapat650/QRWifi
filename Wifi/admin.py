from django.contrib import admin
from .models import WifiUser, WifiAccessLog

admin.site.register(WifiUser)
admin.site.register(WifiAccessLog)
