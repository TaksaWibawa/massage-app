from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib import admin
from .models import Role, Employee, Service, Assignment, Receipt, ReceiptService, GlobalSettings
from .forms import UserAdminForm

class AuditableAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']
    readonly_fields = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # editing an existing object
            return [(None, {'fields': [field for field in fieldsets[0][1]['fields'] if field not in self.readonly_fields]})]
        return fieldsets

class UserAdmin(DefaultUserAdmin):
    add_form = UserAdminForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'get_role', 'is_staff', 'is_superuser', 'get_created_at',
                    'get_created_by', 'get_last_updated_at', 'get_last_updated_by')

    def get_created_at(self, obj):
        return obj.employee.created_at
    get_created_at.short_description = 'Created At'

    def get_created_by(self, obj):
        return obj.employee.created_by
    get_created_by.short_description = 'Created By'

    def get_last_updated_at(self, obj):
        return obj.employee.last_updated_at
    get_last_updated_at.short_description = 'Last Updated At'

    def get_last_updated_by(self, obj):
        return obj.employee.last_updated_by
    get_last_updated_by.short_description = 'Last Updated By'

    def get_role(self, obj):
        return obj.employee.role
    get_role.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        role = form.cleaned_data.get('role')
        obj.is_staff = role.id == 1 or role.name == 'supervisor'
        obj.save()
        Employee.objects.get_or_create(user=obj, defaults={'role': role})

class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'display_value')

    def display_value(self, obj):
        if obj.type == 'percentage':
            return f'{obj.value}%'
        return obj.value

    display_value.short_description = 'Value'

class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

class EmployeeAdmin(AuditableAdmin):
    list_display = ['name', 'phone', 'address',
                    'age', 'role'] + AuditableAdmin.list_display

class ServiceAdmin(AuditableAdmin):
    list_display = ['name', 'price', 'duration'] + AuditableAdmin.list_display

class AssignmentAdmin(AuditableAdmin):
    list_display = ['customer', 'service', 'chair', 'employee', 'start_date', 'end_date'] + AuditableAdmin.list_display

class ReceiptServiceInline(admin.TabularInline):
    model = ReceiptService
    extra = 1

class ReceiptAdmin(AuditableAdmin):
    inlines = [ReceiptServiceInline]
    list_display = ['id', 'assignment', 'total'] + AuditableAdmin.list_display

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Receipt, ReceiptAdmin)