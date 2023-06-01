from django.contrib import admin

from .models import Profile


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    fields = 'user', 'phone', 'avatar'


admin.site.register(Profile, ProfileAdmin)
