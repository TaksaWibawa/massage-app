from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf as generate_pdf_xhtml2pdf
from datetime import datetime
from .models import GlobalSettings


def get_global_setting(name):
    setting = GlobalSettings.objects.filter(name__iexact=name).first()
    if setting:
        if setting.type == 'number':
            value = int(setting.value)
        elif setting.type == 'percentage':
            value = float(setting.value)
        elif setting.type == 'time':
            value = datetime.strptime(setting.value, '%H:%M')
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


def generate_pdf(template_src, context_dict={}):
    try:
        response = HttpResponse(content_type='application/pdf')
        pdf_bytes = render_to_pdf(template_src, context_dict, response)
        if pdf_bytes:
            return pdf_bytes
        else:
            raise Exception('Failed to generate PDF')
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
