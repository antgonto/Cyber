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
api.add_router("/assets", "app.api.assets.router.router", tags=["assets"])
api.add_router("/vulnerabilities", "app.api.vulnerabilities.router.router", tags=["vulnerabilities"])