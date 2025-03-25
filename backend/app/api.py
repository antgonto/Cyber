from ninja import NinjaAPI
from ninja.openapi import Swagger

api = NinjaAPI(
    title="Cyber API",
    version="1.0.0",
    docs=Swagger(
        settings={
            "tryItOutEnabled": True,
            "displayRequestDuration": True,
        }
    ),
)

api.add_router("/users/", user_router)