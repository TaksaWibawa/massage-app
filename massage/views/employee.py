from massage.models import Employee
from massage.forms import CreateUserForm, EmployeeForm, ChangePasswordForm, EmployeeStatusFilterForm
from massage.decorator import role_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib import messages

@role_required(allowed_roles=['supervisor'])
def EmployeeListPage(request):
    form = EmployeeStatusFilterForm(request.GET)
    employees = Employee.objects.filter(role__name__iexact='employee').order_by('-is_active')
    employee_id = request.POST.get('employee_id')

    if 'status' in request.GET and request.GET['status'] != '':
        employees = employees.filter(is_active=request.GET['status'] == 'True')

    if request.POST and employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
        if 'is_active' in request.POST and request.POST['is_active'] != '':
            employee.is_active = request.POST['is_active'] == 'True'
            employee.save()

    return render(request, 'employees/employee_list.html', {'employees': employees, 'form': form})


@role_required(allowed_roles=['supervisor'])
def EmployeeNewPage(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        employee_form = EmployeeForm(request.POST, request.FILES)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()

            group, _created = Group.objects.get_or_create(name='Employee')
            group.user_set.add(user)

            messages.success(request, 'Employee has been created successfully.')
            return redirect('employee_list')
        else:
            messages.error(request, 'Failed to create employee.')
    else:
        user_form = CreateUserForm()
        employee_form = EmployeeForm()
    return render(request, 'employees/employee_new.html', {'user_form': user_form, 'employee_form': employee_form, 'is_edit_page': False})

@role_required(allowed_roles=['supervisor'])
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

@role_required(allowed_roles=['supervisor'])
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
