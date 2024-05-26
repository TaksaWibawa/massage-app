from django.urls import path
from . import views

urlpatterns = [
  # Auth
  path('login', views.LoginPage, name='login'),

  # Dashboard
  path('', views.LandingPage, name='landing_page'),
  path('chart', views.ChartPage, name='chart'),
  path('recap', views.RecapPage, name='recap'),
  path('report', views.ReportPage, name='report'),
  path('assignment/create' , views.NewAssignmentPage, name='new_assignment'),
  path('assignment/edit/<str:id>', views.EditAssignmentPage, name='edit_assignment'),
  path('assignment/delete/<str:id>', views.DeleteAssignmentPage, name='delete_assignment'),

  # Employee
  path('employee-list', views.EmployeeListPage, name='employee_list'),
  path('employee/create', views.EmployeeNewPage, name='employee_new'),
  path('employee/edit/<str:id>', views.EmployeeEditPage, name='employee_edit'),
  path('employee/delete/<str:id>', views.EmployeeDeletePage, name='employee_delete'),

  # Service
  path('service-list', views.ServiceListPage, name='service_list'),
  path('service/create', views.ServiceNewPage, name='service_new'),
  path('service/edit/<str:id>', views.ServiceEditPage, name='service_edit'),
  path('service/delete/<str:id>', views.ServiceDeletePage, name='service_delete'),
]