from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount.providers import registry


def admin_login_redirect(request):
    # すでにログイン済みの場合
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        return HttpResponseForbidden("管理サイトへのアクセス権がありません")

    # 次のURLを取得（デフォルトは管理画面トップ）
    next_url = request.GET.get("next", reverse("admin:index"))

    provider = registry.by_id("openid_connect", request=request)
    login_url = provider.get_login_url(
        request, process="login", next=next_url, **{"openid_connect": "keycloak"}
    )
    return redirect(login_url)
