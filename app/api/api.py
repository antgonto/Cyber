from ninja import NinjaAPI, Swagger

api = NinjaAPI(
    title="Cyber API",
    version="1.0.0",
    auth=None,
    docs=Swagger(
        settings={
            "tryItOutEnabled": True,
            "displayRequestDuration": True,
        }
    ),
)

api.add_router("/users", "app.api.users.router.router", tags=["users"])