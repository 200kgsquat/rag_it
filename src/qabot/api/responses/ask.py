ask_responses = {
    200: {
        "description": "Success - the question was answered successfully",
        "content": {
            "application/json": {
                "example": {
                    "answer": "RAG stands for Retrieval-Augmented Generation...",
                    "sources": [
                        {"title": "Doc 1", "path": "/docs/1", "updated_at": "2025-10-08T12:00:00Z"},
                        {"title": "Doc 2", "path": "/docs/2", "updated_at": "2025-10-08T12:00:00Z"}
                    ],
                    "timings": {"retrieve_ms": 10, "llm_ms": 100, "total_ms": 110}
                }
            }
        },
    },
    400: {
        "description": "Bad Request - invalid input",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Question cannot be empty",
                }
            }
        },
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "question"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                }
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Internal server error during question answering",
                }
            }
        },
    },
}
