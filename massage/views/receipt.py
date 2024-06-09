from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from massage.decorator import supervisor_required
from massage.forms import AdditionalServicesFormset
from massage.models import Assignment, Service, Receipt, ReceiptService
from massage.services.receipt import generate_invoice_number, create_receipt, generate_pdf_response
from massage.utils import get_global_setting
import json


@supervisor_required(allowed_roles=['supervisor'])
def ReceiptPage(request, id):
    assignment = get_object_or_404(Assignment, id=id)

    current_date = timezone.localtime().strftime('%d%m%Y')
    last_receipt = Receipt.objects.filter(
        id__startswith='EMS-' + current_date).last()

    try:
        existing_receipt = Receipt.objects.get(assignment=assignment)
    except Receipt.DoesNotExist:
        existing_receipt = None

    invoice_number = existing_receipt.id if existing_receipt else generate_invoice_number(
        current_date, last_receipt)

    request.session['invoice_number'] = invoice_number
    if request.method == 'POST':
        formset = AdditionalServicesFormset(
            request.POST, prefix='additional_services')

        if formset.is_valid():
            additional_services = []
            if existing_receipt:
                receipt_services = ReceiptService.objects.filter(
                    receipt=existing_receipt, is_additional=True)
                additional_services = [rs.service for rs in receipt_services]
            else:
                for form in formset:
                    additional_service = form.cleaned_data.get(
                        'additional_service')
                    if additional_service:
                        additional_services.append(additional_service)

            base_price = assignment.service.price
            additional_services_price = sum(
                service.price for service in additional_services)
            total_price = base_price + additional_services_price

            request.session['total_price'] = float(total_price)
            request.session['additional_services'] = [
                str(service.id) for service in additional_services]

            try:
                additional_services_data = [{'name': service.name, 'price': service.price} for service in additional_services]

                return generate_pdf_response(
                    request, invoice_number, assignment, additional_services_data, total_price)
            except Exception as e:
                messages.error(request, e)
                return JsonResponse({'error': str(e)}, status=500)

        else:
            messages.error(request, 'Invalid form data')
    else:
        formset = AdditionalServicesFormset(prefix='additional_services')

    services = Service.objects.all()
    services_prices = {str(service.id): float(service.price)
                       for service in services}
    services_prices_json = json.dumps(services_prices, cls=DjangoJSONEncoder)

    context = {
        'services_prices': services_prices_json,
        'receipt': existing_receipt,
        'invoice_number': invoice_number,
        'formset': formset,
        'assignment': assignment,
        'additional_services': existing_receipt.receiptservice_set.filter(is_additional=True) if existing_receipt else ''
    }

    return render(request, 'dashboard/receipt.html', context)


@supervisor_required(allowed_roles=['supervisor'])
def finalize_receipt(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    fee_percentage = get_global_setting('Service Fee')

    invoice_number = request.session.get('invoice_number')
    total_price = request.session.get('total_price')
    additional_services_ids = request.session.get('additional_services')

    if not all([invoice_number, total_price, fee_percentage]):
        messages.error(request, 'Invalid data')
        return JsonResponse({'error': 'Invalid data'}, status=400)

    receipt = Receipt.objects.filter(id=invoice_number).first()

    if receipt is None:
        receipt = create_receipt(invoice_number, request.user, assignment,
                                 total_price, additional_services_ids, fee_percentage)

    if not assignment.is_done:
        assignment.is_done = True
        assignment.save()
        message = 'Payment Completed'
    else:
        message = 'Receipt printed'

    
    del request.session['invoice_number']
    del request.session['total_price']
    del request.session['additional_services']

    messages.success(request, message)
    return JsonResponse({'message': 'Receipt finalized and assignment marked as done.'})
