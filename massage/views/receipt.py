from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from massage.decorator import supervisor_required
from massage.forms import AdditionalServicesFormset
from massage.models import Assignment, Service, Receipt, ReceiptService, EmployeePayment
from massage.utils import get_global_setting, generate_pdf
import json

@supervisor_required(allowed_roles=['supervisor'])
def ReceiptPage(request, id):
    fee_percentage = get_global_setting('Service Fee')
    assignment = get_object_or_404(Assignment, id=id)

    current_date = timezone.localtime().strftime('%d%m%Y')
    last_receipt = Receipt.objects.filter(id__startswith='EMS-' + current_date).last()

    existing_receipt = Receipt.objects.filter(assignment=assignment).first()
    if existing_receipt:
        invoice_number = existing_receipt.id
    else:
        if last_receipt is not None:
            last_sequence = int(last_receipt.id.split('-')[2])
            new_sequence = str(last_sequence + 1).zfill(4)
        else:
            new_sequence = '0001'

        invoice_number = 'EMS-' + current_date + '-' + new_sequence

    request.session['invoice_number'] = invoice_number

    if request.method == 'POST':
        formset = AdditionalServicesFormset(request.POST, prefix='additional_services')

        if formset.is_valid():
            additional_services = []
            for form in formset:
                additional_service = form.cleaned_data.get('additional_service')
                if additional_service:
                    additional_services.append(additional_service)

            base_price = assignment.service.price
            additional_services_price = sum(service.price for service in additional_services)
            total_price = base_price + additional_services_price
            
            request.session['total_price'] = total_price
            request.session['additional_services'] = [str(service.id) for service in additional_services]
            request.session['fee_percentage'] = fee_percentage

            try:
                pdf_bytes = generate_pdf(request, invoice_number, request.user, assignment)

                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename=Invoice_{invoice_number}.pdf'
                
                return response
            except Exception as e:
                messages.error(request, e)
                return JsonResponse({'error': str(e)}, status=500)

        else:
            messages.error(request, 'Invalid form data')
    else:
        formset = AdditionalServicesFormset(prefix='additional_services')

    services = Service.objects.all()
    services_prices = {str(service.id): float(service.price) for service in services}
    services_prices_json = json.dumps(services_prices, cls=DjangoJSONEncoder)

    context = {
        'assignment': assignment,
        'invoice_number': invoice_number,
        'formset': formset,
        'services_prices': services_prices_json,
        'receipt': existing_receipt or None
    }

    return render(request, 'dashboard/receipt.html', context)

@supervisor_required(allowed_roles=['supervisor'])
def finalize_receipt(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    invoice_number = request.session.get('invoice_number')
    total_price = request.session.get('total_price')
    additional_services_ids = request.session.get('additional_services', [])
    fee_percentage = request.session.get('fee_percentage')

    if not all([invoice_number, total_price, fee_percentage]):
        messages.error(request, 'Invalid session data')
        return JsonResponse({'error': 'Invalid session data'}, status=400)

    additional_services = Service.objects.filter(id__in=additional_services_ids)
    receipt = Receipt.objects.filter(id=invoice_number).first()

    if receipt is None:
        receipt = Receipt.objects.create(
            id=invoice_number,
            cashier=request.user,
            assignment=assignment,
            total=total_price
        )

        ReceiptService.objects.create(receipt=receipt, service=assignment.service)

        for service in additional_services:
            ReceiptService.objects.create(receipt=receipt, service=service)

        EmployeePayment.objects.create(
            receipt=receipt,
            fee_percentage=fee_percentage,
            total_fee=total_price * fee_percentage / 100,
            is_paid=False
        )

        if 'invoice_number' in request.session:
            del request.session['invoice_number']
            del request.session['total_price']
            del request.session['additional_services']
            del request.session['fee_percentage']

    if not assignment.is_done:
        assignment.is_done = True
        assignment.save()
        message = 'Payment Completed'
    else:
        message = 'Receipt printed'

    messages.success(request, message)
    return JsonResponse({'message': 'Receipt finalized and assignment marked as done.'})