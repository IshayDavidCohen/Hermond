class VendorError(Exception):
    status_code: int = 500

    def __init__(self, detail: str = "Internal server error"):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(VendorError):
    status_code = 404

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail)


class ValidationError(VendorError):
    status_code = 400

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(detail)


class ForbiddenError(VendorError):
    status_code = 403

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)


class ConflictError(VendorError):
    status_code = 409

    def __init__(self, detail: str = "Conflict"):
        super().__init__(detail)
