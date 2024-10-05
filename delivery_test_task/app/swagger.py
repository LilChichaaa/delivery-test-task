usd = {
    200: {
        "description": "id посылки",
        "content": {
            "application/json": {
                "example": {
                    "task_id": "219e4a25-d9e6-4cc1-acc7-2b7e9c5accf4"
                }
            }
        }
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/dollar-exchange-rate"
                }
            }
        }
    }
}

registration = {
    200: {
        "description": "id посылки",
        "content": {
            "application/json": {
                "example": {
                    "task_id": "1jhk12312kj3h12kjh312kjh31j2kh31k3"
                }
            }
        }
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/parcel-registration"
                }
            }
        }
    },
    422: {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {
                            "error": "Validation Error",
                            "message": "Input should be greater than 0",
                            "field": "body.weight"
                        }
                    ],
                    "message": "Unprocessable Entity",
                    "endpoint": "http://127.0.0.1:8000/parcel-registration"
                }
            }
        }
    },
    400: {
        "description": "Ошибка запроса",
        "content": {
            "application/json": {
                "example": {
                    "error": "HTTP Error",
                    "message": "Parcel creation failed due to integrity error.",
                    "endpoint": "http://127.0.0.1:8000/parcel-registration"
                }
            }
        }
    }
}

parcel_types = {
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/parcel-types"
                }
            }
        }
    },

    200: {
        "description": "Список типов посылок",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 1,
                        "name": "Other"
                    },
                    {
                        "id": 2,
                        "name": "Electronics"
                    },
                    {
                        "id": 3,
                        "name": "Clothing"
                    }
                ]
            }
        }
    }

}

parcels = {
    200: {
        "description": "Список типов посылок",
        "content": {
            "application/json": {
                "example": {
                    "parcels": [
                        {
                            "id": 2,
                            "name": "pivo",
                            "weight": 3.5,
                            "value": 2500.0,
                            "parcel_type": "Documents",
                            "delivery_cost": "Не рассчитано"
                        },
                        {
                            "id": 3,
                            "name": "abc",
                            "weight": 3.3,
                            "value": 2600.0,
                            "parcel_type": "Clothing",
                            "delivery_cost": "Не рассчитано"
                        }
                    ],
                    "total": 12
                }
            }
        }
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/parcels"
                }
            }
        }
    },
    400: {
        "description": "Ошибка запроса",
        "content": {
            "application/json": {
                "example": {
                    "error": "HTTP Error",
                    "message": "Page and page_size must be positive integers.",
                    "endpoint": "http://127.0.0.1:8000/parcels?page=-10"
                }
            }
        }
    },
    422: {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {
                            "error": "Validation Error",
                            "message": "Input should be a valid integer, unable to parse string as an integer",
                            "field": "query.parcel_type_id"
                        }
                    ],
                    "message": "Unprocessable Entity",
                    "endpoint": "http://127.0.0.1:8000/parcels?parcel_type_id=f"
                }
            }
        }
    }

}

parcels_num = {
    200: {
        "description": "Данные посылки",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "name": "Laptop",
                    "weight": 2.5,
                    "value": 1500.0,
                    "parcel_type": "Electronics",
                    "delivery_cost": "Не рассчитано"
                }
            }
        }
    },
    404: {
        "description": "Посылка не найдена",
        "content": {
            "application/json": {
                "example": {
                    "error": "HTTP Error",
                    "message": "Parcel not found",
                    "endpoint": "http://127.0.0.1:8000/parcels/100"
                }
            }
        }
    },
    422: {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {
                            "error": "Validation Error",
                            "message": "Input should be a valid integer, unable to parse string as an integer",
                            "field": "path.parcel_id"
                        }
                    ],
                    "message": "Unprocessable Entity",
                    "endpoint": "http://127.0.0.1:8000/parcels/в"
                }
            }
        }
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/parcels/1"
                }
            }
        }
    }
}

parcel_asign_company = {
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server",
                    "endpoint": "http://127.0.0.1:8000/parcels/1/assign-company"
                }
            }
        }
    },
    200: {
        "description": "Компания привязана",
        "content": {
            "application/json": {
                "example": {
                    "message": "Company assigned successfully"
                }
            }
        }
    },
    400: {
        "description": "Ошибка запроса",
        "content": {
            "application/json": {
                "example": {
                    "error": "HTTP Error",
                    "message": "Parcel already assigned to a transport company",
                    "endpoint": "http://127.0.0.1:8000/parcels/8/assign-company?company_id=1"
                }
            }
        }
    },
    422: {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {
                            "error": "Validation Error",
                            "message": "Input should be a valid integer, unable to parse string as an integer",
                            "field": "path.parcel_id"
                        }
                    ],
                    "message": "Unprocessable Entity",
                    "endpoint": "http://127.0.0.1:8000/d/assign-company?company_id=1"
                }
            }
        }
    }
}
