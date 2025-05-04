from ninja import NinjaAPI, Swagger
import importlib.util

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

# Only add routers if they haven't been added already
routers = [
    ("/users/", "app.api.users.router.router", ["users"]),
    ("/assets/", "app.api.assets.router.router", ["assets"]),
    ("/vulnerabilities/", "app.api.vulnerabilities.router.router", ["vulnerabilities"]),
    ("/alerts/", "app.api.alerts.router.router", ["alerts"]),
    ("/incidents/", "app.api.incidents.router.router", ["incidents"]),
    ("/threat_intelligence/", "app.api.threat_intelligence.router.router", ["threat_intelligence"]),
    ("/settings/", "app.api.settings.router.router", ["settings"]),
    ("/dashboard/", "app.api.dashboard.router.router", ["dashboard"]),
    ("/risk/", "app.api.risk.router.router", ["risk"]),
]

# Track which routers have been added
added_routers = set()

for path, module_path, tags in routers:
    # Check if router already added
    if path not in added_routers:
        try:
            api.add_router(path, module_path, tags=tags)
            added_routers.add(path)
        except Exception as e:
            # Skip if already attached
            if "has already been attached" not in str(e):
                # Re-raise if it's a different error
                raise