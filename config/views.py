from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount import providers


def admin_login_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        return HttpResponseForbidden("管理サイトへのアクセス権がありません")

    next_url = request.GET.get("next", reverse("admin:index"))

    oidc_provider = next(
        (p for p in providers.registry.get_list() if p.id == "openid_connect"), None
    )
    if not oidc_provider:
        return HttpResponseForbidden("OpenID Connect provider is not available")

    login_url = oidc_provider.get_login_url(
        request, process="login", next=next_url, app="keycloak"
    )
    return redirect(login_url)
