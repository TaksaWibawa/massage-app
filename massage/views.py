from django.shortcuts import render

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
    return render(request, 'dashboard/employee_list.html')

def EmployeeNewPage(request):
    return render(request, 'dashboard/employee_new.html')

# Services
def ServiceListPage(request):
    return render(request, 'dashboard/service_list.html')

def ServiceNewPage(request):
    return render(request, 'dashboard/service_new.html')