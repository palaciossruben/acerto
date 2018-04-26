from decouple import config


def add_cloud_front_to_context(request):
    context_data = dict()
    context_data['cloud_front_url'] = config('cloud_front_url')
    return context_data
