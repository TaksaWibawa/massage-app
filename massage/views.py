from django.shortcuts import render, redirect
from .models import Employee
from .forms import EmployeeForm

# Dashboard
def LandingPage(request):
    return render(request, 'dashboard/landing_page.html')

def ChartPage(request):
    return render(request, 'dashboard/chart.html')

def RecapPage(request):
    return render(request, 'dashboard/recap.html')

def ReportPage(request):
    return render(request, 'dashboard/report.html')

def NewAssignmentPage(request):
    return render(request, 'dashboard/new_assignment.html')

# Employees
def EmployeeListPage(request):
    employees = employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

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
def ServiceListPage(request):
    return render(request, 'services/service_list.html')

def ServiceNewPage(request):
    return render(request, 'services/service_new.html')