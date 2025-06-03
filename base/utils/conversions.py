from rest_framework.serializers import ValidationError


class NumberConverter:
    
    """
    A class to handle conversions between different number types.
    """
    def __init__(self):
        pass

    def convert_to_float(value):
        """
        Convert a value to float, if possible.
        :param value: The value to convert.
        :return: The converted float value or None if conversion is not possible.
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid value for float conversion: {value}")
        

    def convert_to_int(value):
        """
        Convert a value to int, if possible.
        :param value: The value to convert.
        :return: The converted int value or None if conversion is not possible.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid value for int conversion: {value}")
        
