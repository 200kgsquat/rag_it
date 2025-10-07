health_responses = {
    200: {
        "description": "Success - the service is healthy",
        "content": {"application/json": {"example": {"status": "ok"}}},
    },
    500: {
        "description": "Internal Server Error - the service is not healthy",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Service is unavailable",
                }
            }
        },
    },
}
