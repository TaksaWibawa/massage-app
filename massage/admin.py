from django.contrib import admin
from .models import Role, Employee

class AuditableAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']
    readonly_fields = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']

class EmployeeAdmin(AuditableAdmin):
    list_display = ['name', 'phone', 'address', 'age', 'role'] + AuditableAdmin.list_display

admin.site.register(Role)
admin.site.register(Employee, EmployeeAdmin)