from urllib.parse import urlencode

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def admin_login_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        return HttpResponseForbidden("管理サイトへのアクセス権がありません")

    next_url = request.GET.get("next") or reverse("admin:index")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("admin:index")

    try:
        base = reverse("openid_connect_login")
    except Exception:
        base = "/accounts/openid_connect/login/"

    qs = urlencode({"process": "login", "app": "keycloak", "next": next_url})
    return redirect(f"{base}?{qs}")
