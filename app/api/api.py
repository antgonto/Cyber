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
    urls_namespace="api",
)

api.add_router("/users/", "app.api.users.router.router", tags=["users"])
api.add_router("/assets/", "app.api.assets.router.router", tags=["assets"])
api.add_router("/vulnerabilities/", "app.api.vulnerabilities.router.router", tags=["vulnerabilities"])
api.add_router("/alerts/", "app.api.alerts.router.router", tags=["alerts"])
api.add_router("/incidents/", "app.api.incidents.router.router", tags=["incidents"])
api.add_router("/threat_intelligence/", "app.api.threat_intelligence.router.router", tags=["threat_intelligence"])