from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from massage.forms import ServiceForm
from massage.models import Service
from massage.decorator import supervisor_required

@supervisor_required(allowed_roles=['supervisor'])
def ServiceListPage(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})


@supervisor_required(allowed_roles=['supervisor'])
def ServiceNewPage(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been created successfully.')
            return redirect('service_list')
        
        else:
            messages.error(request, 'Failed to create service.')
    else:
        form = ServiceForm()
    return render(request, 'services/service_new.html', {'form': form})


@supervisor_required(allowed_roles=['supervisor'])
def ServiceEditPage(request, id):
    service = Service.objects.get(id=id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been updated successfully.')
            return redirect('service_list')
        
        else:
            messages.error(request, 'Failed to update service.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_edit.html', {'form': form})

@supervisor_required(allowed_roles=['supervisor'])
def ServiceDeletePage(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service has been deleted successfully.')
        return redirect('service_list')
    return render(request, 'services/service_delete.html', {'service': service})