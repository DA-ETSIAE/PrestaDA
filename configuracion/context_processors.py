from django.core.cache import cache

from configuracion.models import Configuration
from prestamos import settings
from utils.environment import get_env_bool


def config_processor(request):
    config_cache = cache.get('configs_cache')
    if config_cache is None:
        config_cache = {config.node: config.value for config in Configuration.objects.all()}
        cache.set('configs_cache', config_cache, 5*60)
    return {
        'site_config': config_cache
    }

def local_dev_processor(request):
    return {
        'local_dev' : get_env_bool('PRESTAMOS_LOCALMODE')
    }