from datetime import datetime
from decimal import Decimal
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from massage.context_processors import chart_context
from massage.decorator import auth_required, role_required
from massage.forms import EmployeeFilterForm, MonthFilterForm
from massage.models import Assignment, Employee, Receipt, EmployeePayment
from massage.services.recap import generate_recap_pdf
from massage.utils import get_global_setting

@auth_required
def LandingPage(request):
    return render(request, 'dashboard/landing_page.html')


@role_required(allowed_roles=['supervisor'])
def ChartPage(request):
    context = chart_context(request)

    filter_form = EmployeeFilterForm(request.GET or None, initial={'date': timezone.localtime().date()})
    
    employee = None
    selected_date = timezone.localtime().date()
    tasks = Assignment.objects.all().order_by('start_date')
    
    if filter_form.is_valid():
        selected_date = filter_form.cleaned_data.get('date')

    if selected_date:
        tasks = tasks.filter(start_date__date=selected_date)

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get('employee')

        if employee:
            tasks = tasks.filter(employee=employee)

    tasks_with_positions = []
    for task in tasks:
        start = timezone.localtime(task.start_date).time()
        end = timezone.localtime(task.end_date).time()
        start_row = (start.hour * 60 + start.minute - 18 * 60) + 1
        end_row = (end.hour * 60 + end.minute - 18 * 60) + 1
        tasks_with_positions.append({
            'task': task,
            'start_time': start.strftime('%I:%M %p'),
            'end_time': end.strftime('%I:%M %p'),
            'start_row': start_row,
            'end_row': end_row,
        })

    context['tasks_with_positions'] = tasks_with_positions
    
    for i, time_slot in enumerate(context['TIME_SLOTS']):
        time = datetime.strptime(time_slot, '%I:%M %p')
        row = ((time.hour * 60 + time.minute - 18 * 60) / 240) * 100
        context['TIME_SLOTS'][i] = (time_slot, row)
    
    context['filter_form'] = filter_form

    n = 3
    context['date_range'] = list(range(-n, n+1))
    context['now'] = selected_date

    return render(request, 'dashboard/chart.html', context)

@role_required(allowed_roles=['accountant'])
def ReportPage(request):
    filter_form = MonthFilterForm(request.GET or None, initial={'month': datetime.now().month})
    current_year = datetime.now().year
    month = datetime.now().month
    supervisor_fee = get_global_setting('supervisor fee')

    if filter_form.is_valid():
        month = filter_form.cleaned_data.get('month')

    revenue_per_day = Receipt.objects.filter(assignment__start_date__year=current_year, assignment__start_date__month=month).annotate(date=TruncDay('assignment__start_date')).values('date').annotate(revenue=Sum('total')).order_by('date')

    employee_fee_per_day = EmployeePayment.objects.filter(receipt__assignment__start_date__year=current_year, receipt__assignment__start_date__month=month).annotate(date=TruncDay('receipt__assignment__start_date')).values('date', 'is_paid', 'total_fee').order_by('date')

    report = []
    for revenue in revenue_per_day:
        costs = [cost for cost in employee_fee_per_day if cost['date'] == revenue['date']]
        supervisor_fee_amount = revenue['revenue'] * Decimal(supervisor_fee) / 100
        employee_fee = sum(cost['total_fee'] for cost in costs if cost['is_paid'])
        is_unpaid = any(cost['is_paid'] == False for cost in costs)

        report.append({
            'date': revenue['date'].strftime('%d/%m/%Y'),
            'revenue': revenue['revenue'],
            'supervisor_fee': supervisor_fee_amount,
            'employee_fee': 'unpaid' if is_unpaid else employee_fee,
            'nett_revenue': 'unpaid' if is_unpaid else revenue['revenue'] - employee_fee - supervisor_fee_amount,
        })

    return render(request, 'dashboard/report.html', {'report': report, 'filter_form': filter_form})

@role_required(allowed_roles=['accountant', 'employee'])
def RecapPage(request):
    is_employee = request.user.groups.filter(name__iexact='employee').exists()
    filter_form = EmployeeFilterForm(request.GET or None, request=request, initial={'date': timezone.localtime().date()})
    selected_date = filter_form.cleaned_data.get('date') if filter_form.is_valid() else timezone.localtime().date()
    employee = filter_form.cleaned_data.get('employee') if filter_form.is_valid() and not is_employee else None

    if selected_date is None:
        selected_date = timezone.localtime().date()

    if is_employee:
        employee = Employee.objects.get(user=request.user)

    employee_payments = EmployeePayment.objects.filter(
        receipt__assignment__start_date__date__lte=selected_date,
        is_paid=False
    ).order_by('receipt__assignment__employee')

    if employee:
        employee_payments = employee_payments.filter(receipt__assignment__employee=employee)

    if request.method == 'POST' and not is_employee:
        return HttpResponseRedirect(reverse('recap_confirm') + '?date=' + str(selected_date) + '&employee=' + (str(employee.id) if employee else ''))

    total_payment = employee_payments.aggregate(total=Sum('total_fee'))['total'] or 0

    context = {
        'date': selected_date,
        'employee_id': employee.id if employee else None,
        'employee_payments': employee_payments,
        'employees': Employee.objects.filter(role__name__iexact='employee'),
        'filter_form': filter_form,
        'is_employee': is_employee,
        'total_payment': total_payment,
    }

    return render(request, 'dashboard/recap.html', context)

@role_required(allowed_roles=['accountant', 'employee'])
def RecapHistoryPage(request):
    is_employee = request.user.groups.filter(name__iexact='employee').exists()
    filter_form = EmployeeFilterForm(request.GET or None, request=request, initial={'date': timezone.localtime().date()})
    selected_date = filter_form.cleaned_data.get('date') if filter_form.is_valid() else timezone.localtime().date()
    employee = filter_form.cleaned_data.get('employee') if filter_form.is_valid() and not is_employee else None

    if selected_date is None:
        selected_date = timezone.localtime().date()

    if is_employee:
        employee = Employee.objects.get(user=request.user)

    employee_payments = EmployeePayment.objects.filter(
        receipt__assignment__start_date__date__lte=selected_date,
        is_paid=True
    ).order_by('receipt__assignment__employee')

    if employee:
        employee_payments = employee_payments.filter(receipt__assignment__employee=employee)

    if request.method == 'POST':
        response = generate_recap_pdf(selected_date, employee_payments)

        if response.status_code == 200:
            messages.success(request, 'Recap created')
        else:
            messages.error(request, 'Failed to download recap')
        
        return response

    total_payment = employee_payments.aggregate(total=Sum('total_fee'))['total'] or 0

    context = {
        'date': selected_date,
        'employee_id': employee.id if employee else None,
        'employee_payments': employee_payments,
        'employees': Employee.objects.filter(role__name__iexact='employee'),
        'filter_form': filter_form,
        'is_employee': is_employee,
        'total_payment': total_payment,
    }

    return render(request, 'dashboard/recap_history.html', context)

@role_required(allowed_roles=['accountant'])
def RecapConfirmPage(request):
    date = request.GET.get('date')
    employee = request.GET.get('employee')
    employee_payments = EmployeePayment.objects.filter(
        receipt__assignment__start_date__date__lte=date,
        is_paid=False
    ).order_by('receipt__assignment__employee')

    if request.method == 'POST':
        employee_payments.update(is_paid=True)
        employee_payments = EmployeePayment.objects.filter(
                receipt__assignment__start_date__date__lte=date,
                is_paid=True
            ).order_by('receipt__assignment__employee')
        
        response = generate_recap_pdf(date, employee_payments)

        if response.status_code == 200:
            messages.success(request, 'Recap created')
        else:
            messages.error(request, 'Failed to download recap')
        
        return response
    
    context = {
        'date': date,
        'employee': employee,
    }

    return render(request, 'dashboard/recap_confirm.html', context)