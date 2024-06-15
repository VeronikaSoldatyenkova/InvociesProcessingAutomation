# automation_app/admin.py

from django.contrib import admin
from .models import User, Automation, AutomationType, UserAutomation

admin.site.register(User)
admin.site.register(Automation)
admin.site.register(AutomationType)
admin.site.register(UserAutomation)
from django.contrib import admin

# Register your models here.
