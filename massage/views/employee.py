from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from massage.forms import CreateUserForm, EmployeeForm, ChangePasswordForm
from massage.models import Employee
from massage.decorator import supervisor_required

@supervisor_required(allowed_roles=['supervisor'])
def EmployeeListPage(request):
    employees = Employee.objects.filter(role__name__iexact='employee')
    return render(request, 'employees/employee_list.html', {'employees': employees})


@supervisor_required(allowed_roles=['supervisor'])
def EmployeeNewPage(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        employee_form = EmployeeForm(request.POST, request.FILES)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            messages.success(request, 'Employee has been created successfully.')
            return redirect('employee_list')
        else:
            messages.error(request, 'Failed to create employee.')
    else:
        user_form = CreateUserForm()
        employee_form = EmployeeForm()
    return render(request, 'employees/employee_new.html', {'user_form': user_form, 'employee_form': employee_form, 'is_edit_page': False})

@supervisor_required(allowed_roles=['supervisor'])
def EmployeeEditPage(request, id):
    employee = Employee.objects.get(id=id)
    if request.method == 'POST':
        employee_form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if employee_form.is_valid():
            employee_form.save()
            messages.success(request, 'Employee has been updated successfully.')
            return redirect('employee_list')
        else:
            messages.error(request, 'Failed to update employee.')
    else:
        employee_form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_edit.html', {'employee_form': employee_form, 'is_edit_page': True, 'employee_id': employee.id})

@supervisor_required(allowed_roles=['supervisor'])
def EmployeeChangePasswordPage(request, id):
    employee = get_object_or_404(Employee, id=id)
    user = employee.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password has been updated successfully.')
            return redirect('employee_edit', id=id)
        else:
            messages.error(request, 'Failed to update password.')
    else:
        form = ChangePasswordForm(user=user)
    return render(request, 'employees/employee_change_password.html', {'password_form': form})


@supervisor_required(allowed_roles=['supervisor'])
def EmployeeDeletePage(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_delete.html', {'employee': employee})
