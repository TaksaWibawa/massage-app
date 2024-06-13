from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from massage.forms import ServiceForm, ServiceStatusFilterForm
from massage.models import Service
from massage.decorator import role_required

@role_required(allowed_roles=['supervisor'])
def ServiceListPage(request):
    form = ServiceStatusFilterForm(request.GET or None, initial={'status': None})
    services = Service.objects.all()
    service_id = request.POST.get('service_id')

    if 'status' in request.GET and request.GET['status'] != '':
        services = services.filter(is_active=request.GET['status'] == 'True').order_by('-is_active')

    if request.POST and service_id:
        service = get_object_or_404(Service, id=service_id)
        if 'is_active' in request.POST and request.POST['is_active'] != '':
            service.is_active = request.POST['is_active'] == 'True'
            service.save()

    return render(request, 'services/service_list.html', {'services': services, 'form': form})


@role_required(allowed_roles=['supervisor'])
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


@role_required(allowed_roles=['supervisor'])
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