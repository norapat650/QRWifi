from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from .models import WifiUser, WifiAccessLog

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def create_access_log(request, line_user_id, action):
    WifiAccessLog.objects.create(
        line_user_id=line_user_id or "unknown",
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )


def get_promo_redirect_url(line_user_id):
    safe_line_user_id = line_user_id or "unknown"
    return f"/promo/?lineUserId={safe_line_user_id}&campaign=wifi"


def landing_page(request):
    create_access_log(request, "unknown", "visit_landing")
    return render(request, "wifi/landing.html")


def check_user(request):
    line_user_id = request.GET.get("lineUserId")

    if not line_user_id:
        create_access_log(request, "unknown", "missing_line_user_id")
        return JsonResponse({
            "success": False,
            "message": "Missing lineUserId"
        })

    user = WifiUser.objects.filter(line_user_id=line_user_id).first()
    create_access_log(request, line_user_id, "check_user")

    if user:
        return JsonResponse({
            "success": True,
            "is_registered": True,
            "redirect_url": f"/welcome/?lineUserId={line_user_id}"
        })

    return JsonResponse({
        "success": True,
        "is_registered": False,
        "redirect_url": f"/register/?lineUserId={line_user_id}"
    })


def register_page(request):
    if request.method == "POST":
        line_user_id = (request.POST.get("line_user_id") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()

        if not line_user_id or not first_name or not phone:
            create_access_log(request, line_user_id, "register_failed")
            return render(request, "wifi/register.html", {
                "line_user_id": line_user_id,
                "error": "กรุณากรอกข้อมูลให้ครบ"
            })

        try:
            user, created = WifiUser.objects.get_or_create(
                line_user_id=line_user_id,
                defaults={
                    "first_name": first_name,
                    "phone": phone,
                }
            )
        except IntegrityError:
            user = WifiUser.objects.get(line_user_id=line_user_id)
            created = False

        create_access_log(
            request,
            line_user_id,
            "register_success" if created else "register_existing"
        )

        return redirect(get_promo_redirect_url(line_user_id))

    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "view_register")

    return render(request, "wifi/register.html", {
        "line_user_id": line_user_id
    })


def welcome_page(request):
    line_user_id = request.GET.get("lineUserId") or "unknown"
    create_access_log(request, line_user_id, "view_welcome")
    return redirect(get_promo_redirect_url(line_user_id))

def promo_page(request):
    line_user_id = request.GET.get("lineUserId")
    campaign = request.GET.get("campaign", "default")

    create_access_log(request, line_user_id, f"view_promo_{campaign}")

    return render(request, "wifi/promo.html", {
        "line_user_id": line_user_id,
        "campaign": campaign
    })

def promo_page(request):
    line_user_id = request.GET.get("lineUserId")
    campaign = request.GET.get("campaign", "default")

    create_access_log(request, line_user_id, f"view_promo_{campaign}")

    return render(request, "wifi/promo.html", {
        "line_user_id": line_user_id,
        "campaign": campaign
    })