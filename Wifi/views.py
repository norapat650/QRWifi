from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from .models import WifiUser, WifiAccessLog
import requests


COMMUNE_PORTAL_URL = "https://commune.shellutapao.com"
COMMUNE_API_URL = "https://commune.shellutapao.com/api/customer-sync"


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


def sync_to_commune(user):
    """
    ส่งข้อมูลลูกค้าจาก QRWifi ไป Commune demo ก่อน
    ถ้า API demo ยังไม่พร้อม ระบบ QRWifi จะไม่พัง แค่ log error ใน console
    """
    try:
        payload = {
            "line_user_id": user.line_user_id,
            "name": user.first_name,
            "phone": user.phone,
            "email": user.email,
            "source": "qrwifi",
        }

        response = requests.post(COMMUNE_API_URL, json=payload, timeout=3)
        print("Commune sync response:", response.status_code, response.text)

    except Exception as e:
        print("Commune sync error:", e)


def allow_mikrotik_wifi(request, line_user_id):
    """
    เก็บไว้สำหรับ Phase ถัดไป: MikroTik API / IP Binding
    ตอนนี้ยังไม่ใช้ POST /login เพราะ MikroTik Hotspot ต้องผูก session กับ client browser
    """
    create_access_log(request, line_user_id, "mikrotik_allow_pending")
    return True


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

    if user and user.first_name and user.phone:
        user.save(update_fields=["last_login"])
        sync_to_commune(user)
        return JsonResponse({
            "success": True,
            "is_registered": True,
            "redirect_url": f"/promo/?lineUserId={line_user_id}"
        })

    # ถ้าไม่มี user หรือมี line_user_id แล้วแต่ข้อมูลยังไม่ครบ ให้กลับไปกรอกฟอร์มสมัคร Commune ก่อน
    create_access_log(request, line_user_id, "needs_register_info")
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
        email = (request.POST.get("email") or "").strip()

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
                    "email": email,
                }
            )
        except IntegrityError:
            user = WifiUser.objects.get(line_user_id=line_user_id)
            created = False

        if not created:
            user.first_name = first_name
            user.phone = phone
            user.email = email
            user.save(update_fields=["first_name", "phone", "email", "last_login"])

        create_access_log(
            request,
            line_user_id,
            "register_success" if created else "register_existing"
        )

        sync_to_commune(user)

        return redirect(get_promo_redirect_url(line_user_id))

    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "view_register")

    existing_user = WifiUser.objects.filter(line_user_id=line_user_id).first()

    return render(request, "wifi/register.html", {
        "line_user_id": line_user_id,
        "existing_user": existing_user,
    })


def welcome_page(request):
    line_user_id = request.GET.get("lineUserId") or "unknown"
    create_access_log(request, line_user_id, "view_welcome")
    return redirect(get_promo_redirect_url(line_user_id))


def promo_page(request):
    line_user_id = request.GET.get("lineUserId")
    campaign = request.GET.get("campaign", "wifi")

    create_access_log(request, line_user_id, f"view_promo_{campaign}")

    # เก็บไว้เผื่อ Phase ถัดไป: allow ผ่าน MikroTik API / IP Binding
    allow_mikrotik_wifi(request, line_user_id)

    # วิธีปัจจุบัน: ให้ client browser เข้า MikroTik login เอง เพื่อผูก session/cookie กับมือถือเครื่องนั้น
    # ถ้า login สำเร็จ MikroTik จะปล่อย internet ตาม policy เดิม แล้ว user จะเห็น/ไปต่อได้จาก hotspot flow
    mikrotik_login_url = "http://192.168.30.1/login"

    create_access_log(request, line_user_id, "render_mikrotik_autologin")

    return redirect(
    f"{COMMUNE_PORTAL_URL}"
    f"?lineUserId={line_user_id}"
    f"&source=qrwifi"
    f"&campaign={campaign}"
)


def log_connect(request):
    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "connect_wifi_clicked")
    allow_mikrotik_wifi(request, line_user_id)

    return JsonResponse({
        "success": True,
        "message": "connect logged",
        "mikrotik": "redirect_login_mode"
    })

def wifi_demo(request):
    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "wifi_demo_enter")

    return JsonResponse({
        "success": True,
        "message": f"WiFi Ready for {line_user_id}"
    })