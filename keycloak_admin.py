"""
KeyCloak Admin API integration using python-keycloak library.
This module provides functions for managing KeyCloak resources alongside django-allauth.
"""

from typing import Dict, List, Optional
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from django.conf import settings


class KeyCloakAdminClient:
    """KeyCloak Admin API client for managing users, realms, and clients."""

    def __init__(self):
        """Initialize KeyCloak admin client with environment configuration."""
        self.server_url = getattr(
            settings, "KEYCLOAK_SERVER_URL", "http://localhost:8080"
        )
        self.realm_name = getattr(settings, "KEYCLOAK_REALM", "myrealm")
        self.admin_username = getattr(settings, "KEYCLOAK_ADMIN_USERNAME", "admin")
        self.admin_password = getattr(settings, "KEYCLOAK_ADMIN_PASSWORD", "admin")

        self.keycloak_admin = None
        self._connect()

    def _connect(self):
        """Establish connection to KeyCloak admin API."""
        try:
            keycloak_connection = KeycloakOpenIDConnection(
                server_url=self.server_url,
                username=self.admin_username,
                password=self.admin_password,
                realm_name="master",
                verify=False,
            )

            self.keycloak_admin = KeycloakAdmin(
                connection=keycloak_connection, realm_name=self.realm_name
            )
        except Exception as e:
            print(f"Failed to connect to KeyCloak: {e}")
            self.keycloak_admin = None

    def is_connected(self) -> bool:
        """Check if KeyCloak admin client is connected."""
        return self.keycloak_admin is not None

    def create_user(
        self,
        email: str,
        username: str,
        first_name: str = "",
        last_name: str = "",
        password: str = None,
        email_verified: bool = True,
    ) -> Optional[str]:
        """Create a new user in KeyCloak."""
        if not self.is_connected():
            return None

        try:
            user_data = {
                "email": email,
                "username": username,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": email_verified,
            }

            user_id = self.keycloak_admin.create_user(user_data)

            if password:
                self.set_user_password(user_id, password)

            return user_id
        except Exception as e:
            print(f"Failed to create user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        if not self.is_connected():
            return None

        try:
            users = self.keycloak_admin.get_users({"email": email})
            return users[0] if users else None
        except Exception as e:
            print(f"Failed to get user by email: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        if not self.is_connected():
            return None

        try:
            users = self.keycloak_admin.get_users({"username": username})
            return users[0] if users else None
        except Exception as e:
            print(f"Failed to get user by username: {e}")
            return None

    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Update user information."""
        if not self.is_connected():
            return False

        try:
            self.keycloak_admin.update_user(user_id, user_data)
            return True
        except Exception as e:
            print(f"Failed to update user: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """Delete user from KeyCloak."""
        if not self.is_connected():
            return False

        try:
            self.keycloak_admin.delete_user(user_id)
            return True
        except Exception as e:
            print(f"Failed to delete user: {e}")
            return False

    def set_user_password(
        self, user_id: str, password: str, temporary: bool = False
    ) -> bool:
        """Set user password."""
        if not self.is_connected():
            return False

        try:
            self.keycloak_admin.set_user_password(user_id, password, temporary)
            return True
        except Exception as e:
            print(f"Failed to set user password: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Get all users in the realm."""
        if not self.is_connected():
            return []

        try:
            return self.keycloak_admin.get_users()
        except Exception as e:
            print(f"Failed to get users: {e}")
            return []

    def get_realm_info(self) -> Optional[Dict]:
        """Get realm information."""
        if not self.is_connected():
            return None

        try:
            return self.keycloak_admin.get_realm(self.realm_name)
        except Exception as e:
            print(f"Failed to get realm info: {e}")
            return None

    def update_realm_settings(self, settings_data: Dict) -> bool:
        """Update realm settings."""
        if not self.is_connected():
            return False

        try:
            self.keycloak_admin.update_realm(self.realm_name, settings_data)
            return True
        except Exception as e:
            print(f"Failed to update realm settings: {e}")
            return False

    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """Get client by client ID."""
        if not self.is_connected():
            return None

        try:
            clients = self.keycloak_admin.get_clients()
            for client in clients:
                if client.get("clientId") == client_id:
                    return client
            return None
        except Exception as e:
            print(f"Failed to get client: {e}")
            return None

    def create_client(self, client_data: Dict) -> Optional[str]:
        """Create a new client."""
        if not self.is_connected():
            return None

        try:
            return self.keycloak_admin.create_client(client_data)
        except Exception as e:
            print(f"Failed to create client: {e}")
            return None

    def update_client(self, client_id: str, client_data: Dict) -> bool:
        """Update client configuration."""
        if not self.is_connected():
            return False

        try:
            self.keycloak_admin.update_client(client_id, client_data)
            return True
        except Exception as e:
            print(f"Failed to update client: {e}")
            return False

    def create_realm_role(self, role_name: str, description: str = "") -> bool:
        """Create a realm role."""
        if not self.is_connected():
            return False

        try:
            role_data = {"name": role_name, "description": description}
            self.keycloak_admin.create_realm_role(role_data)
            return True
        except Exception as e:
            print(f"Failed to create realm role: {e}")
            return False

    def assign_realm_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign realm role to user."""
        if not self.is_connected():
            return False

        try:
            role = self.keycloak_admin.get_realm_role(role_name)
            self.keycloak_admin.assign_realm_roles(user_id, [role])
            return True
        except Exception as e:
            print(f"Failed to assign realm role to user: {e}")
            return False

    def get_user_realm_roles(self, user_id: str) -> List[Dict]:
        """Get user's realm roles."""
        if not self.is_connected():
            return []

        try:
            return self.keycloak_admin.get_realm_roles_of_user(user_id)
        except Exception as e:
            print(f"Failed to get user realm roles: {e}")
            return []

    def create_google_identity_provider(
        self, google_client_id: str, google_client_secret: str
    ) -> bool:
        """Create Google identity provider configuration."""
        if not self.is_connected():
            return False

        try:
            idp_data = {
                "alias": "google",
                "displayName": "Google",
                "providerId": "google",
                "enabled": True,
                "config": {
                    "clientId": google_client_id,
                    "clientSecret": google_client_secret,
                    "defaultScope": "openid profile email",
                    "trustEmail": "true",
                    "storeToken": "true",
                    "addReadTokenRoleOnCreate": "true",
                },
            }

            self.keycloak_admin.create_idp(idp_data)
            return True
        except Exception as e:
            print(f"Failed to create Google identity provider: {e}")
            return False

    def get_identity_providers(self) -> List[Dict]:
        """Get all identity providers."""
        if not self.is_connected():
            return []

        try:
            return self.keycloak_admin.get_idps()
        except Exception as e:
            print(f"Failed to get identity providers: {e}")
            return []


keycloak_admin = KeyCloakAdminClient()


def sync_django_user_to_keycloak(django_user):
    """Sync Django user to KeyCloak."""
    if not keycloak_admin.is_connected():
        return False

    existing_user = keycloak_admin.get_user_by_email(django_user.email)
    if existing_user:
        user_data = {
            "firstName": django_user.first_name,
            "lastName": django_user.last_name,
            "email": django_user.email,
            "username": django_user.username,
        }
        return keycloak_admin.update_user(existing_user["id"], user_data)
    else:
        return (
            keycloak_admin.create_user(
                email=django_user.email,
                username=django_user.username,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
            )
            is not None
        )


def get_keycloak_user_info(django_user):
    """Get KeyCloak user information for Django user."""
    if not keycloak_admin.is_connected():
        return None

    return keycloak_admin.get_user_by_email(django_user.email)
