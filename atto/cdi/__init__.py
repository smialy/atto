from .framework import Framework

def create_framework(bundles, settings):
    cdi = Framework(settings)
    for bundle_name in bundles:
        cdi.install_bundle(bundle_name)
    return cdi

