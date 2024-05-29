from datetime import datetime
import json

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .context_processors import chart_context
from .decorator import auth_required, protected, supervisor_required
from .forms import (AdditionalServicesFormset, AssignmentForm, EmployeeForm,
                    LoginForm, ServiceForm, CreateUserForm, ChangePasswordForm)
from .models import (Assignment, Employee, Receipt, ReceiptService, Service)
from .utils import get_global_setting

# Auth
@protected
def LoginPage(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, 'Login successful.')
            return redirect('/')
        
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Dashboard
@auth_required
def LandingPage(request):
    return render(request, 'dashboard/landing_page.html')


@supervisor_required(allowed_roles=['supervisor'])
def ChartPage(request):
    context = chart_context(request)
    tasks = Assignment.objects.filter(
        start_date__date=timezone.localtime().date(), is_done=False)

    tasks_with_positions = []

    for task in tasks:
        start = timezone.localtime(task.start_date).time()
        end = timezone.localtime(task.end_date).time()
        start_row = (start.hour * 60 + start.minute - 18 * 60) + 1
        end_row = (end.hour * 60 + end.minute - 18 * 60) + 1
        tasks_with_positions.append({
            'task': task,
            'start_time': start.strftime('%H:%M'),
            'end_time': end.strftime('%H:%M'),
            'start_row': start_row,
            'end_row': end_row,
        })

    context['tasks_with_positions'] = tasks_with_positions

    for i, time_slot in enumerate(context['TIME_SLOTS']):
        time = datetime.strptime(time_slot, '%H:%M')
        row = ((time.hour * 60 + time.minute - 18 * 60) / 240) * 100
        context['TIME_SLOTS'][i] = (time_slot, row)

    return render(request, 'dashboard/chart.html', context)


@supervisor_required(allowed_roles=['supervisor'])
def EditAssignmentPage(request, id):
    assignment = Assignment.objects.get(id=id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment has been updated successfully.')
            return redirect('chart')
        
        else:
            messages.error(request, 'Failed to update assignment.')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'dashboard/assignment_edit.html', {'form': form})


@supervisor_required(allowed_roles=['supervisor'])
def DeleteAssignmentPage(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment has been deleted successfully.')
        return redirect('chart')

    return render(request, 'dashboard/assignment_delete.html', {'assignment': assignment})


@supervisor_required(allowed_roles=['supervisor'])
def ReceiptPage(request, id):
    ppn = get_global_setting('ppn')
    assignment = get_object_or_404(Assignment, id=id)

    if assignment.is_done:
        return redirect('chart')

    current_date = timezone.localtime().strftime('%d%m%Y')
    last_receipt = Receipt.objects.filter(
        id__startswith='EMS-' + current_date).last()
    if last_receipt is not None:
        last_sequence = int(last_receipt.id.split('-')[2])
        new_sequence = str(last_sequence + 1).zfill(4)
    else:
        new_sequence = '0001'

    invoice_number = 'EMS-' + current_date + '-' + new_sequence

    if request.method == 'POST' and assignment.is_done == False:
        formset = AdditionalServicesFormset(
            request.POST, prefix='additional_services')

        if formset.is_valid():
            additional_services = []
            for form in formset:
                additional_service = form.cleaned_data.get(
                    'additional_service')
                if additional_service:
                    additional_services.append(additional_service)

            base_price = assignment.service.price
            additional_services_price = sum(
                service.price for service in additional_services)

            total_price = base_price + additional_services_price

            receipt = Receipt.objects.create(
                id=invoice_number,
                assignment=assignment,
                total=total_price,
            )

            assignment.is_done = True
            assignment.save()

            ReceiptService.objects.create(
                receipt=receipt, service=assignment.service)
            for service in additional_services:
                ReceiptService.objects.create(receipt=receipt, service=service)

            messages.success(request, 'Receipt has been created successfully.')
            return redirect('chart')

        else:
            messages.error(request, 'Failed to create receipt.')

    else:
        formset = AdditionalServicesFormset(prefix='additional_services')

    services = Service.objects.all()
    services_prices = {str(service.id): float(service.price) for service in services}
    services_prices_json = json.dumps(services_prices)

    return render(request, 'dashboard/receipt.html', {'assignment': assignment, 'invoice_number': invoice_number, 'formset': formset, 'services_prices': services_prices_json})


@auth_required
def RecapPage(request):
    return render(request, 'dashboard/recap.html')


@supervisor_required(allowed_roles=['supervisor'])
def NewAssignmentPage(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment has been created successfully.')
            return redirect('chart')
        else:
            messages.error(request, 'Failed to create assignment.')
    else:
        form = AssignmentForm()
    return render(request, 'dashboard/assignment_new.html', {'form': form})

# Employees
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
            employee_form.save(user=user)
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
    user = employee.user
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

# Services
@supervisor_required(allowed_roles=['supervisor'])
def ServiceListPage(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})


@supervisor_required(allowed_roles=['supervisor'])
def ServiceNewPage(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been created successfully.')
            return redirect('service_list')
        
        else:
            messages.error(request, 'Failed to create service.')
    else:
        form = ServiceForm()
    return render(request, 'services/service_new.html', {'form': form})


@supervisor_required(allowed_roles=['supervisor'])
def ServiceEditPage(request, id):
    service = Service.objects.get(id=id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been updated successfully.')
            return redirect('service_list')
        
        else:
            messages.error(request, 'Failed to update service.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_edit.html', {'form': form})

@supervisor_required(allowed_roles=['supervisor'])
def ServiceDeletePage(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service has been deleted successfully.')
        return redirect('service_list')
    return render(request, 'services/service_delete.html', {'service': service})
