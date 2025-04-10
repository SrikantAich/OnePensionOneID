from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Pensioner, Pension, PensionTransaction, LifeCertificate, Grievance
from .models import Announcement
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# Register custom User model with our custom admin
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Pensioner)
admin.site.register(Pension)
admin.site.register(PensionTransaction)
admin.site.register(LifeCertificate)
admin.site.register(Grievance)
admin.site.register(Announcement)