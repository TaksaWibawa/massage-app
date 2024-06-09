from massage.utils import generate_pdf
from django.http import HttpResponse, JsonResponse
from datetime import datetime

def generate_recap_pdf(date, employee_payments):
    try:
        if isinstance(date, datetime):
            date = datetime.strptime(date, '%Y-%m-%d')
            
        data = {
            'date': date,
            'employee_payments': employee_payments,
        }

        pdf_bytes = generate_pdf('downloads/download_recap.html', data)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=Recap_{date.strftime("%d-%m-%Y")}.pdf'

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)