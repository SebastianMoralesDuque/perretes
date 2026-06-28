import os


def umami_context(request):
    """Context processor to inject Umami analytics configuration into templates."""
    return {
        'UMAMI_WEBSITE_ID': os.environ.get('UMAMI_WEBSITE_ID', 'c093fdc7-f86d-4ac9-b58e-01f49857d35f'),
        'UMAMI_SCRIPT_URL': os.environ.get('UMAMI_SCRIPT_URL', 'https://analytics.sebastianmorales.sbs/script.js'),
    }
