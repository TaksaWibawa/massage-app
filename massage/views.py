from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Employee
from .forms import LoginForm, EmployeeForm
from .decorator import supervisor_required, auth_required, protected

# Auth
@protected
def LoginPage(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Dashboard
@auth_required
def LandingPage(request):
    return render(request, 'dashboard/landing_page.html')

@supervisor_required(allowed_roles=['supervisor'])
def ChartPage(request):
    return render(request, 'dashboard/chart.html')

@auth_required
def RecapPage(request):
    return render(request, 'dashboard/recap.html')

@supervisor_required(allowed_roles=['supervisor'])
def ReportPage(request):
    return render(request, 'dashboard/report.html')

@supervisor_required(allowed_roles=['supervisor'])
def NewAssignmentPage(request):
    return render(request, 'dashboard/new_assignment.html')

# Employees
@supervisor_required(allowed_roles=['supervisor'])
def EmployeeListPage(request):
    employees = employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

@supervisor_required(allowed_roles=['supervisor'])
def EmployeeNewPage(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_new.html', {'form': form})

# Services
@supervisor_required(allowed_roles=['supervisor'])
def ServiceListPage(request):
    return render(request, 'services/service_list.html')

@supervisor_required(allowed_roles=['supervisor'])
def ServiceNewPage(request):
    return render(request, 'services/service_new.html')