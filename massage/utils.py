from django.core.cache import cache
from .models import GlobalSettings

def get_global_setting(name):
    value = cache.get(name)
    if value is None:
        setting = GlobalSettings.objects.filter(name__iexact=name).first()
        if setting:
            if setting.type == 'number':
                value = int(setting.value)
            elif setting.type == 'percentage':
                value = float(setting.value)
            else:
                value = setting.value
    return value