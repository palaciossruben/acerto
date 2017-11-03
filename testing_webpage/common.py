def get_ziggeo_api_key():
    """
    Has a remove '/n' becuase in Linux, production was not working because of this.
    Returns: String with key
    """
    return open('./ziggeo_api_key.txt').read().replace('\n', '')
