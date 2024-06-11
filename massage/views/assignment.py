from datetime import datetime, timedelta
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from massage.decorator import supervisor_required, fetch_required
from massage.forms import AssignmentForm
from massage.models import Assignment, Service
from massage.utils import get_global_setting

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
    return render(request, 'assignments/assignment_edit.html', {'form': form})

@supervisor_required(allowed_roles=['supervisor'])
def DeleteAssignmentPage(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment has been deleted successfully.')
        return redirect('chart')

    return render(request, 'assignments/assignment_delete.html', {'assignment': assignment})

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
    return render(request, 'assignments/assignment_new.html', {'form': form})

@fetch_required(allowed_methods=['GET'])
def get_available_chairs(request):
    start_date = request.GET.get('start_date')
    start_time = request.GET.get('start_time')
    service_id = request.GET.get('service_id')
    
    if request.GET.get('assignment_id'):
        assignment_id = request.GET.get('assignment_id')
    else:
        assignment_id = None

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if start_time:
        start_time = datetime.strptime(start_time, "%H:%M").time()

    service = get_object_or_404(Service, id=service_id) if service_id else None

    duration = service.duration if service else None

    if start_date and start_time and duration:
        start_datetime = datetime.combine(start_date, start_time)
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = start_datetime + timedelta(minutes=duration)
    else:
        start_datetime = end_datetime = None

    max_chairs = get_global_setting('max chairs')

    filter_args = {}
    if start_datetime and end_datetime:
        filter_args['start_date__lt'] = end_datetime
        filter_args['end_date__gt'] = start_datetime

    if assignment_id:
        assigned_chairs = Assignment.objects.filter(**filter_args).exclude(id=assignment_id).values_list('chair', flat=True)
    else:
        assigned_chairs = Assignment.objects.filter(**filter_args).values_list('chair', flat=True)

    available_chairs = [(i, str(i)) for i in range(1, max_chairs+1) if i not in assigned_chairs]

    return JsonResponse({'available_chairs': available_chairs})