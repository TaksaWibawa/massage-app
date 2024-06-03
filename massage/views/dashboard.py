from datetime import datetime
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.shortcuts import render
from django.utils import timezone
from massage.decorator import auth_required, supervisor_required
from massage.forms import EmployeeFilterForm, MonthFilterForm
from massage.models import Assignment, Employee, Receipt, EmployeePayment
from massage.context_processors import chart_context

@auth_required
def LandingPage(request):
    return render(request, 'dashboard/landing_page.html')


@supervisor_required(allowed_roles=['supervisor'])
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
    
    context['filter_form'] = filter_form

    return render(request, 'dashboard/chart.html', context)

@supervisor_required(allowed_roles=['supervisor'])
def ReportPage(request):
    filter_form = MonthFilterForm(request.GET or None, initial={'month': datetime.now().month})
    current_year = datetime.now().year
    month = datetime.now().month

    if filter_form.is_valid():
        month = filter_form.cleaned_data.get('month')

    revenue_per_day = Receipt.objects.filter(created_at__year=current_year, created_at__month=month).annotate(date=TruncDay('created_at')).values('date').annotate(revenue=Sum('total')).order_by('date')

    cost_per_day = EmployeePayment.objects.filter(receipt__created_at__year=current_year, receipt__created_at__month=month).annotate(date=TruncDay('receipt__created_at')).values('date', 'is_paid', 'total_fee').order_by('date')

    report = []
    for revenue in revenue_per_day:
        costs = [cost for cost in cost_per_day if cost['date'] == revenue['date']]
        total_cost = sum(cost['total_fee'] for cost in costs if cost['is_paid'])
        is_unpaid = any(cost['is_paid'] == False for cost in costs)

        report.append({
            'date': revenue['date'].strftime('%d/%m/%Y'),
            'revenue': revenue['revenue'],
            'cost': 'unpaid' if is_unpaid else total_cost,
            'nett_revenue': 'unpaid' if is_unpaid else revenue['revenue'] - total_cost
        })

    return render(request, 'dashboard/report.html', {'report': report, 'filter_form': filter_form})

@auth_required
def RecapPage(request):
    filter_form = EmployeeFilterForm(request.GET or None, initial={'date': timezone.localtime().date()})
    selected_date = timezone.localtime().date()
    employee = None

    if filter_form.is_valid():
        selected_date = filter_form.cleaned_data.get('date')

    employees = Employee.objects.filter(role__name__iexact='employee')
    employee_payments = EmployeePayment.objects.all().order_by('receipt__assignment__employee')

    if selected_date:
        employee_payments = employee_payments.filter(receipt__assignment__start_date__date=selected_date)

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get('employee')

        if employee:
            employee_payments = employee_payments.filter(receipt__assignment__employee=employee)

    if request.method == 'POST':
        selected_payments = request.POST.getlist('payment_id')
        pay_all = 'pay_all' in request.POST
    
        if not selected_payments and not pay_all:
            messages.error(request, 'Please select at least one payment to pay off.')
        else:
            if selected_payments:
                EmployeePayment.objects.filter(id__in=selected_payments).update(is_paid=True)
                messages.success(request, f'{len(selected_payments)} payments have been paid off.')
            if pay_all:
                EmployeePayment.objects.filter(is_paid=False).update(is_paid=True)
                messages.success(request, 'All payments have been paid off.')
    
    total_payment = employee_payments.aggregate(total=Sum('total_fee'))['total'] or 0

    context = {
        'filter_form': filter_form,
        'date': selected_date,
        'employee_id': employee.id if employee else None,
        'employee_payments': employee_payments,
        'employees': employees,
        'total_payment': total_payment,
    }

    return render(request, 'dashboard/recap.html', context)