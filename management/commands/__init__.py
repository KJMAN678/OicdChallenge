from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]</old_str>
<new_str>from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]</new_str>
</str_replace>

<str_replace path="/home/ubuntu/repos/OicdChallenge/docker-compose.yml">
<old_str>services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}

volumes:
  postgres_data:</old_str>
<new_str>services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  keycloak-db:
    image: postgres:13
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: keycloak
    volumes:
      - keycloak_db_data:/var/lib/postgresql/data

  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      KEYCLOAK_ADMIN: ${KEYCLOAK_ADMIN_USERNAME:-admin}
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD:-admin}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://keycloak-db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak
      KC_HOSTNAME_STRICT: false
      KC_HOSTNAME_STRICT_HTTPS: false
      KC_HTTP_ENABLED: true
    ports:
      - "8080:8080"
    command: start-dev
    depends_on:
      - keycloak-db

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
      - keycloak
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}
      KEYCLOAK_SERVER_URL: ${KEYCLOAK_SERVER_URL:-http://keycloak:8080}
      KEYCLOAK_REALM: ${KEYCLOAK_REALM:-myrealm}
      KEYCLOAK_CLIENT_ID: ${KEYCLOAK_CLIENT_ID:-django-client}
      KEYCLOAK_CLIENT_SECRET: ${KEYCLOAK_CLIENT_SECRET}
      KEYCLOAK_ADMIN_USERNAME: ${KEYCLOAK_ADMIN_USERNAME:-admin}
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD:-admin}
      AWS_OIDC_ISSUER_URL: ${AWS_OIDC_ISSUER_URL}
      AWS_OIDC_CLIENT_ID: ${AWS_OIDC_CLIENT_ID}
      AWS_OIDC_CLIENT_SECRET: ${AWS_OIDC_CLIENT_SECRET}

volumes:
  postgres_data:
  keycloak_db_data:</new_str>
</str_replace>

<create_file path="/home/ubuntu/repos/OicdChallenge/management/commands/setup_keycloak.py">
"""
Django management command to set up KeyCloak realm, client, and Google Identity Provider.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
from keycloak_admin import keycloak_admin


class Command(BaseCommand):
    help = 'Set up KeyCloak realm, client, and Google Identity Provider'

    def add_arguments(self, parser):
        parser.add_argument(
            '--google-client-id',
            type=str,
            help='Google OAuth2 Client ID for Identity Provider setup',
        )
        parser.add_argument(
            '--google-client-secret',
            type=str,
            help='Google OAuth2 Client Secret for Identity Provider setup',
        )
        parser.add_argument(
            '--skip-google',
            action='store_true',
            help='Skip Google Identity Provider setup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting KeyCloak setup...'))
        
        max_retries = 30
        for i in range(max_retries):
            if keycloak_admin.is_connected():
                break
            time.sleep(2)
            self.stdout.write(f'Retry {i+1}/{max_retries}...')
        
        if not keycloak_admin.is_connected():
            self.stdout.write(
                self.style.ERROR('Failed to connect to KeyCloak. Please check your configuration.')
            )
            return
        
        self.stdout.write(self.style.SUCCESS('Connected to KeyCloak successfully!'))
        
        realm_info = keycloak_admin.get_realm_info()
        if realm_info:
            self.stdout.write(f'Realm "{settings.KEYCLOAK_REALM}" already exists.')
        else:
            self.stdout.write(f'Creating realm "{settings.KEYCLOAK_REALM}"...')
            self.stdout.write(
                self.style.WARNING(
                    'Realm creation requires manual setup in KeyCloak admin console.'
                )
            )
        
        self.setup_django_client()
        
        if not options['skip_google']:
            google_client_id = options.get('google_client_id') or os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
            google_client_secret = options.get('google_client_secret') or os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
            
            if google_client_id and google_client_secret:
                self.setup_google_identity_provider(google_client_id, google_client_secret)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Google OAuth2 credentials not provided. Skipping Google Identity Provider setup.'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('KeyCloak setup completed!'))
        self.print_next_steps()

    def setup_django_client(self):
        self.stdout.write('Setting up Django OIDC client...')
        
        client_id = settings.KEYCLOAK_CLIENT_ID
        existing_client = keycloak_admin.get_client_by_id(client_id)
        
        if existing_client:
            self.stdout.write(f'Client "{client_id}" already exists.')
            return
        
        client_data = {
            "clientId": client_id,
            "name": "Django OIDC Client",
            "description": "Django application OIDC client",
            "enabled": True,
            "clientAuthenticatorType": "client-secret",
            "secret": settings.KEYCLOAK_CLIENT_SECRET,
            "redirectUris": [
                "http://localhost:8000/accounts/openid_connect/keycloak/login/callback/",
                "http://127.0.0.1:8000/accounts/openid_connect/keycloak/login/callback/",
            ],
            "webOrigins": [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ],
            "protocol": "openid-connect",
            "publicClient": False,
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": False,
            "authorizationServicesEnabled": False,
        }
        
        try:
            client_uuid = keycloak_admin.create_client(client_data)
            if client_uuid:
                self.stdout.write(
                    self.style.SUCCESS(f'Django OIDC client "{client_id}" created successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create Django OIDC client "{client_id}".')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating Django OIDC client: {e}')
            )

    def setup_google_identity_provider(self, google_client_id, google_client_secret):
        self.stdout.write('Setting up Google Identity Provider...')
        
        existing_idps = keycloak_admin.get_identity_providers()
        google_idp_exists = any(idp.get('alias') == 'google' for idp in existing_idps)
        
        if google_idp_exists:
            self.stdout.write('Google Identity Provider already exists.')
            return
        
        success = keycloak_admin.create_google_identity_provider(
            google_client_id, google_client_secret
        )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('Google Identity Provider created successfully!')
            )
            self.stdout.write(
                'Note: You may need to configure additional mappers in the KeyCloak admin console.'
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to create Google Identity Provider.')
            )

    def print_next_steps(self):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('NEXT STEPS:'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n1. KeyCloak Admin Console:')
        self.stdout.write(f'   URL: {settings.KEYCLOAK_SERVER_URL}/admin/')
        self.stdout.write(f'   Username: {settings.KEYCLOAK_ADMIN_USERNAME}')
        self.stdout.write(f'   Password: {settings.KEYCLOAK_ADMIN_PASSWORD}')
        
        self.stdout.write('\n2. Create Realm (if not exists):')
        self.stdout.write(f'   - Create realm: "{settings.KEYCLOAK_REALM}"')
        self.stdout.write('   - Enable user registration if needed')
        
        self.stdout.write('\n3. Google OAuth2 Setup:')
        self.stdout.write('   - Go to Google Cloud Console')
        self.stdout.write('   - Create OAuth 2.0 Client ID')
        self.stdout.write('   - Add authorized redirect URI:')
        self.stdout.write(f'     {settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/broker/google/endpoint')
        
        self.stdout.write('\n4. AWS OIDC Setup (Optional):')
        self.stdout.write('   - Configure AWS IAM Identity Center')
        self.stdout.write('   - Set environment variables:')
        self.stdout.write('     - AWS_OIDC_ISSUER_URL')
        self.stdout.write('     - AWS_OIDC_CLIENT_ID')
        self.stdout.write('     - AWS_OIDC_CLIENT_SECRET')
        
        self.stdout.write('\n5. Test Authentication:')
        self.stdout.write('   - Start Django server: python manage.py runserver')
        self.stdout.write('   - Visit: http://localhost:8000')
        self.stdout.write('   - Test login with configured providers')
        
        self.stdout.write('\n' + '='*60)
