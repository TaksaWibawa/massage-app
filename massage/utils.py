from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf as generate_pdf_xhtml2pdf
from .models import GlobalSettings, ReceiptService, Service, Receipt


def get_global_setting(name):
    setting = GlobalSettings.objects.filter(name__iexact=name).first()
    if setting:
        if setting.type == 'number':
            value = int(setting.value)
        elif setting.type == 'percentage':
            value = float(setting.value)
        else:
            value = setting.value
        return value
    return None

def render_to_pdf(template_src, context_dict={}, response=None):
    pdf_content = generate_pdf_xhtml2pdf(template_name=template_src, context=context_dict, file_object=response)
    if pdf_content:
        return pdf_content
    else:
        print("PDF generation error")
        return None


def generate_pdf(request, invoice_number, user, assignment):
    additional_services_qs = ReceiptService.objects.filter(receipt=invoice_number)
    total_price_qs = Receipt.objects.filter(id=invoice_number)

    if additional_services_qs.exists():
        additional_services = []
        for service in additional_services_qs[1:]:
            additional_services.append({
                'name': service.service.name,
                'price': service.service.price,
            })
    else:
        additional_services = request.session.get('additional_services', [])
        additional_services = Service.objects.filter(id__in=additional_services).values('name', 'price')

    if total_price_qs.exists():
        total_price = total_price_qs[0].total
    else:
        total_price = request.session.get('total_price', 0)

    data = {
        'invoice_number': invoice_number,
        'cashier': user,
        'assignment': assignment,
        'additional_services': additional_services,
        'total': total_price,
    }

    try:
        response = HttpResponse(content_type='application/pdf')
        pdf_bytes = render_to_pdf('dashboard/download_receipt.html', data, response)
        if pdf_bytes:
            return pdf_bytes
        else:
            raise Exception('Failed to generate PDF')
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
