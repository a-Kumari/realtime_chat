from django import template

register = template.Library()

@register.filter
def file_type(file_url):
    """
    Determines the file type based on its extension.
    """
    file_url = file_url.lower()
    if file_url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return 'image'
    elif file_url.endswith(('.mp4', '.webm', '.ogg')):
        return 'video'
    else:
        return 'document'

@register.filter
def get_item(dictionary, key):
    """Fetch an item from a dictionary by key, handling non-dictionary input."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None