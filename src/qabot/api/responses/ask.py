ask_responses = {
    200: {
        "description": "Success - the question was answered successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": "chatcmpl-f51b2cd2-bef7-417e-964e-a08f0b513c22",
                    "object": "chat.completion",
                    "created": 1730241104,
                    "model": "openai/gpt-oss-20b",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Fast language models have gained significant attention..."
                            },
                            "logprobs": None,
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "queue_time": 0.037493756,
                        "prompt_tokens": 18,
                        "prompt_time": 0.000680594,
                        "completion_tokens": 556,
                        "completion_time": 0.463333333,
                        "total_tokens": 574,
                        "total_time": 0.464013927
                    },
                    "system_fingerprint": "fp_179b0f92c9",
                    "x_groq": { "id": "req_01jbd6g2qdfw2adyrt2az8hz4w" }
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
