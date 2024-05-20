from django.urls import path
from . import views

urlpatterns = [
  # Dashboard
  path('', views.LandingPage, name='landing_page'),
  path('chart', views.ChartPage, name='chart'),
  path('recap', views.RecapPage, name='recap'),
  path('report', views.ReportPage, name='report'),
  path('new-assignment', views.NewAssignmentPage, name='new_assignment'),

  # Employee
  path('employee-list', views.EmployeeListPage, name='employee_list'),
  path('new-employee', views.EmployeeNewPage, name='employee_new'),

  # Service
  path('service-list', views.ServiceListPage, name='service_list'),
  path('new-service', views.ServiceNewPage, name='service_new'),
]