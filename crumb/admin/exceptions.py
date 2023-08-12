class InputValidationError(ValueError):
    """Невалидные данные в инпутере"""
    def __init__(self, msg: str, key: str = None, **kwargs):
        self.msg = msg
        self.code = key
