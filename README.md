### A Django project for cyber security

#### 1. Create a Django project.

#### 2. Install Django Ninja.

```
pip3 install django-ninja
```

#### 3. Add `ninja` to `INSTALLED_APPS` in `settings.py`.

INSTALLED_APPS = [
    # ... other apps
    'corsheaders',
    # ... other apps
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top of middleware list
    # ... other middleware
]

CORS_ALLOW_ALL_HEADERS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Make sure Django knows where to find static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Make sure Django serves static files in development
if DEBUG:
    INSTALLED_APPS += ['django.contrib.staticfiles']

pip install django-cors-headers

python manage.py collectstatic --noinput

Adding the django-cors-headers package
Configuring proper CORS settings in the Django settings.py
Ensuring static files are properly served for Django Ninja's docs UI

#### 4. Add `ninja` to `urls.py`.

#### 5. Create a new file `api.py` in the app folder.

#### 6. Create .env file with environment variables.

#### 7. Create class Settings in the environment.py file with the environment variables.

#### 8. Change the `DATABASE` and `CACHES` sections in the `settings.py` file to use the environment variables.

#### 9. Install and start Docker.

#### 10. Create Dockerfile.

#### 11. Create docker-compose.yml.

#### 12. Create .gitignore file.

#### 13. Add pyproject.toml to the project root folder to using Ruff, black, isort and mypy.

#### 14. Add .pre-commit-config.yaml to the project.

#### 15. Install pre-commit.

```
pip3 install pre-commit
```
#### 16. Create sonar-project.properties.

#### 17. Create a SonarQube account in sonarcloud.io.

#### 18. Create a new project in SonarQube, and get the project and organization keys.

#### 19. Install the SonarQube plugin in Pycharm and configure it after generating a token.


#### 20. Add a GitHub action - .github/workflows/code-quality.yml.

#### 21. Create a Django app.

```
python manage.py startapp app

```

#### 22. Create the class `APIConfig` in the `apps.py` file.

#### 23. Add the app to INSTALLED_APPS in your settings.py.

```python
INSTALLED_APPS = [
    "ninja",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "app.apps.APIConfig",
]
```

#### 24. Create your models.

#### 25. Run 

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 26. Create your schemas.

#### 27. Create your routers.

#### 28. Create the frontend folder.

#### 29. Add the package.json file to the frontend folder.

#### 30. Add src/services/api.js to the frontend folder.


project_root/
│
├── app/                      # Django app
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py            # NinjaAPI setup
│   │   ├── apps.py           # APIConfig class
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── router.py     # User routes
│   │   │   ├── models.py     # User models
│   │   │   └── schemas.py    # User schemas
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── apps.py
│
├── frontend/                  # React frontend
│   ├── node_modules/          # Created after npm install
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/
│   │   │   └── api.js         # API service for backend communication
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json          # Your current file
│   └── package-lock.json
│
├── manage.py                  # Django management script
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── pyproject.toml             # Python project configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── sonar-project.properties   # SonarQube configuration
└── README.md                  # Project documentation
