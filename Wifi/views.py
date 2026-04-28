from django.shortcuts import render
from django.http import JsonResponse
from .models import WifiUser


def landing_page(request):
    return render(request, "wifi/landing.html")


def check_user(request):
    line_user_id = request.GET.get("lineUserId")

    if not line_user_id:
        return JsonResponse({
            "success": False,
            "message": "Missing lineUserId"
        })

    user = WifiUser.objects.filter(line_user_id=line_user_id).first()

    if user:
        return JsonResponse({
            "success": True,
            "is_registered": True,
            "redirect_url": "/welcome/"
        })

    return JsonResponse({
        "success": True,
        "is_registered": False,
        "redirect_url": f"/register/?lineUserId={line_user_id}"
    })


def register_page(request):
    if request.method == "POST":
        line_user_id = request.POST.get("line_user_id")
        first_name = request.POST.get("first_name")
        phone = request.POST.get("phone")

        if not line_user_id or not first_name or not phone:
            return render(request, "wifi/register.html", {
                "line_user_id": line_user_id,
                "error": "กรุณากรอกข้อมูลให้ครบ"
            })

        WifiUser.objects.create(
            line_user_id=line_user_id,
            first_name=first_name,
            phone=phone
        )

        return render(request, "wifi/welcome.html")

    line_user_id = request.GET.get("lineUserId")

    return render(request, "wifi/register.html", {
        "line_user_id": line_user_id
    })


def welcome_page(request):
    return render(request, "wifi/welcome.html")