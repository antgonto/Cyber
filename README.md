### A Django project for cyber security

#### 1. Create a Django project.

#### 2. Install Django Ninja.

```
pip3 install django-ninja
```

#### 3. Add `ninja` to `INSTALLED_APPS` in `settings.py`.

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


