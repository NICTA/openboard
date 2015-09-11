import re
from django.core.exceptions import ValidationError

html_colour_pattern = re.compile("^([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
def validate_html_colour(value):
    if not html_colour_pattern.match(value):
        raise ValidationError("%s is not a valid html colour representation" % value)

