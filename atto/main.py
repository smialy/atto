import logging

from atto_api.web import IWebApplication

from . import settings as atto_settings
from .cdi import create_framework
from .conf import Settings

FORMAT = '[%(levelname)s] %(name)s (%(filename)s) %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logger = logging.getLogger(__name__)


async def create_app(loop, settings):
    settings = Settings(settings)
    settings.extend(atto_settings)

    cdi = create_framework(settings.INSTALLED_BUNDLES, settings)

    await cdi.start()
    app = _find_web_app(cdi)
    app.on_cleanup.append(lambda _: cdi.stop())
    return app


def _find_web_app(cdi):
    ref = cdi.get_service_reference(IWebApplication)
    if not ref:
        raise TypeError('Not registered service: "IWebApplication"')
    return cdi.get_service(cdi, ref)
