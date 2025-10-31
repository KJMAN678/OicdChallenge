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

    provider_cls = providers.registry.get_class("openid_connect")
    if provider_cls is None:
        return HttpResponseForbidden("OpenID Connect provider is not configured")

    provider = provider_cls(request)
    login_url = provider.get_login_url(
        request, process="login", next=next_url, **{"openid_connect": "keycloak"}
    )
    return redirect(login_url)
