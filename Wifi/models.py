from django.db import models


class WifiUser(models.Model):
    line_user_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.first_name


class WifiAccessLog(models.Model):
    line_user_id = models.CharField(max_length=100)
    action = models.CharField(max_length=50, default="visit")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line_user_id} - {self.action}"
