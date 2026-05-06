from django.db import models


class WifiUser(models.Model):
    line_user_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    # 🔥 เพิ่ม field สำหรับ CRM
    email = models.EmailField(blank=True, null=True)

    # 🔥 tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} ({self.line_user_id})"


class WifiAccessLog(models.Model):
    line_user_id = models.CharField(max_length=100)
    action = models.CharField(max_length=50, default="visit")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line_user_id} - {self.action}"
