from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from .models import WifiUser, WifiAccessLog
import requests
import binascii
import logging
import librouteros
from django.urls import path

# ปิด librouteros ไว้ชั่วคราวเนื่องจากไม่มีอุปกรณ์จริงในระบบทดสอบ
# from librouteros import connect

COMMUNE_PORTAL_URL = "https://commune.shellutapao.com"
COMMUNE_API_URL = "https://commune.shellutapao.com/api/customer-sync"
logger = logging.getLogger(__name__)

def liff_login_page(request):
    """หน้าแรกที่ลูกค้าสแกน QR เข้ามา (แสดงหน้าจอ LINE LIFF)"""
    return render(request, 'liff_index.html')

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def submit_to_mikrotik(request):
    user_ip = request.META.get('REMOTE_ADDR')
    line_id = request.POST.get('line_id')
    return render(request, 'success.html')

def create_access_log(request, line_user_id, action):
    WifiAccessLog.objects.create(
        line_user_id=line_user_id or "unknown",
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )

def bypass_mikrotik_login(client_ip):
    """จำลองการล็อกอินสำเร็จโดยไม่ต้องเชื่อมต่อ Router จริง"""
    logger.info(f"[Bypass] Simulated MikroTik active activation for IP: {client_ip}")
    return True

def login_to_mikrotik(request):
    """จำลองระบบล็อกอินเข้าสู่ MikroTik"""
    client_ip = request.META.get('REMOTE_ADDR')
    logger.info(f"[Bypass] Simulated connection to MikroTik from IP: {client_ip}")
    return render(request, 'success.html', {'message': 'เชื่อมต่อสำเร็จ! (ระบบจำลองการทำงาน)'})

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
    """จำลองการอนุมัติสิทธิ์การเข้าใช้เน็ตใน Log"""
    create_access_log(request, line_user_id, "mikrotik_allow_simulated")
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
    """
    หน้าแสดงโปรโมชั่นหลัก: ทำการ Bypass คำสั่ง API ของ MikroTik เพื่อให้ระบบทำงานต่อได้ทันที
    """
    line_user_id = request.GET.get("lineUserId")
    campaign = request.GET.get("campaign", "wifi")

    create_access_log(request, line_user_id, f"view_promo_{campaign}")
    allow_mikrotik_wifi(request, line_user_id)
    create_access_log(request, line_user_id, "render_welcome_page_bypass")

    return render(request, "wifi/welcome.html", {"line_user_id": line_user_id})

def log_connect(request):
    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "connect_wifi_clicked")
    allow_mikrotik_wifi(request, line_user_id)

    return JsonResponse({
        "success": True,
        "message": "connect logged (Simulated)",
        "mikrotik": "bypass_mode",
        "redirect_url": "https://www.google.com",
    })

def wifi_demo(request):
    line_user_id = request.GET.get("lineUserId")
    create_access_log(request, line_user_id, "wifi_demo_enter")

    return JsonResponse({
        "success": True,
        "message": f"WiFi Ready for {line_user_id} (Demo Mode)"
    })

def activate_wifi(request):
    # ข้อมูลสำหรับเชื่อมต่อ Router ของคุณ
    router_ip = '192.168.30.1' 
    username = 'admin'
    password = 'your_password' # ใส่รหัสผ่าน Router ของคุณ
    
    client_ip = request.META.get('REMOTE_ADDR')
    
    try:
        # เชื่อมต่อกับ MikroTik
        api = librouteros.connect(router_ip, username, password)
        
        # คำสั่งสร้าง Hotspot IP Binding เพื่ออนุญาตให้เข้าเน็ตได้โดยไม่ต้อง Login ซ้ำ
        api(cmd='/ip/hotspot/ip-binding/add', address=client_ip, type='bypassed')
        
        return JsonResponse({'status': 'success', 'message': 'คุณสามารถใช้งาน Internet ได้แล้ว'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})