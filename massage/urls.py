from django.urls import path
from .views import auth, dashboard, employee, assignment, service, receipt

urlpatterns = [
  # Auth
  path('login', auth.LoginPage, name='login'),
  path('logout', auth.Logout, name='logout'),

  # Dashboard
  path('', dashboard.LandingPage, name='landing_page'),
  path('chart', dashboard.ChartPage, name='chart'),
  path('report', dashboard.ReportPage, name='report'),

  # Assignment
  path('assignment/create' , assignment.NewAssignmentPage, name='new_assignment'),
  path('assignment/edit/<str:id>', assignment.EditAssignmentPage, name='edit_assignment'),
  path('assignment/delete/<str:id>', assignment.DeleteAssignmentPage, name='delete_assignment'),
  path('assignment/available-chairs', assignment.get_available_chairs, name='get_available_chairs'),

  # Employee
  path('employee-list', employee.EmployeeListPage, name='employee_list'),
  path('employee/create', employee.EmployeeNewPage, name='employee_new'),
  path('employee/edit/<str:id>', employee.EmployeeEditPage, name='employee_edit'),
  path('employee/edit/change-password/<str:id>', employee.EmployeeChangePasswordPage, name='employee_change_password'),

  # Service
  path('service-list', service.ServiceListPage, name='service_list'),
  path('service/create', service.ServiceNewPage, name='service_new'),
  path('service/edit/<str:id>', service.ServiceEditPage, name='service_edit'),

  # Receipt
  path('assignment/pay/<str:id>', receipt.ReceiptPage, name='receipt'),
  path('assignment/pay/<str:id>/download', receipt.finalize_receipt, name='download_receipt'),

  # Recap
  path('recap', dashboard.RecapPage, name='recap'),
  path('recap/history', dashboard.RecapHistoryPage, name='recap_history'),
  path('recap/confirm', dashboard.RecapConfirmPage, name='recap_confirm'),
]