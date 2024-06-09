from django.http import HttpResponse
from massage.models import Receipt, ReceiptService, EmployeePayment, Service
from massage.utils import generate_pdf

def generate_invoice_number(current_date, last_receipt):
    if last_receipt is not None:
        last_sequence = int(last_receipt.id.split('-')[2])
        new_sequence = str(last_sequence + 1).zfill(4)
    else:
        new_sequence = '0001'

    return 'EMS-' + current_date + '-' + new_sequence

def create_receipt(invoice_number, user, assignment, total_price, additional_services_ids, fee_percentage):
    receipt = Receipt.objects.create(
        id=invoice_number,
        cashier=user,
        assignment=assignment,
        total=total_price
    )

    ReceiptService.objects.create(receipt=receipt, service=assignment.service, is_additional=False)

    for service_id in additional_services_ids:
        service = Service.objects.get(id=service_id)
        ReceiptService.objects.create(receipt=receipt, service=service, is_additional=True)

    EmployeePayment.objects.create(
        receipt=receipt,
        fee_percentage=fee_percentage,
        total_fee=total_price * fee_percentage / 100,
        is_paid=False
    )

    return receipt

def generate_pdf_response(request, invoice_number, assignment, additional_services_data, total_price):
    data = {
        'invoice_number': invoice_number,
        'cashier': request.user,
        'assignment': assignment,
        'additional_services': additional_services_data,
        'total': total_price,
    }

    print(data)
    pdf_bytes = generate_pdf('downloads/download_receipt.html', data)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Invoice_{invoice_number}.pdf'
    return response