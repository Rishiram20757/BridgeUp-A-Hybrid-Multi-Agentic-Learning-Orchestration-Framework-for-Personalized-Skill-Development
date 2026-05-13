class APIError(Exception):
    pass


class APIRateLimitError(APIError):
    pass


class APIResponseFormatError(APIError):
    pass