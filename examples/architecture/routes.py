from .handlers import ReportHandler, Request


def dispatch(method: str, path: str, request: Request, handler: ReportHandler) -> dict:
    if method == "GET" and path == "/reports/subtotal":
        return handler.handle(request)
    return {"status": 404, "error": "route_not_found"}
