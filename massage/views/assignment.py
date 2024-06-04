from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from massage.forms import AssignmentForm
from massage.models import Assignment
from massage.decorator import supervisor_required

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
