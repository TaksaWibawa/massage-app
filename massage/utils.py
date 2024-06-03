from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from .models import GlobalSettings, ReceiptService, Service


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


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return result.getvalue()
    else:
        print(f"PDF generation error: {pdf.err}")
        return None


def generate_pdf(request, invoice_number, user, assignment, total_price):
    additional_services_qs = ReceiptService.objects.filter(receipt=invoice_number)

    if additional_services_qs.exists():
        additional_services = []
        for service in additional_services_qs[1:]:
            additional_services.append({
                'name': service.service.name,
                'price': service.service.price,
            })
    else:
        additional_services = request.session.get('additional_services', [])
        if additional_services:
            additional_services = Service.objects.filter(id__in=additional_services).values('name', 'price')
        else:
            raise Exception('No additional services found')

    data = {
        'invoice_number': invoice_number,
        'cashier': user,
        'assignment': assignment,
        'additional_services': additional_services,
        'total': total_price,
    }

    pdf_bytes = render_to_pdf('dashboard/download_receipt.html', data)
    if pdf_bytes:
        return pdf_bytes
    else:
        raise Exception('Failed to generate PDF')
