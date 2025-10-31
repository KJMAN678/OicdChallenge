from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


def admin_login_redirect(request):
    # すでにログイン済みの場合
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        return HttpResponseForbidden("管理サイトへのアクセス権がありません")

    # 次のURLを取得（デフォルトは管理画面トップ）
    next_url = request.GET.get("next", reverse("admin:index"))

    # KeyCloakのOIDCログインにリダイレクト
    return redirect(
        f"/accounts/openid_connect/login/?process=login&openid_connect=keycloak&next={next_url}"
    )
