# QRWifi

ระบบ Login WiFi ผ่าน LINE (LIFF) + Django

---

## 🔥 Features

- Login ผ่าน LINE LIFF
- ตรวจสอบ user จาก lineUserId
- สมัคร user ใหม่
- จำ user เดิม (ไม่ต้องสมัครซ้ำ)
- บันทึก Access Log (IP / User Agent / Action)
- Redirect ไปหน้า WiFi Login

---

## 🛠 Tech Stack

- Python
- Django
- SQLite (default)
- LINE LIFF

---

## 📦 Installation (Windows)

### 1. Clone project

```bash
git clone https://github.com/norapat650/QRWifi.git
cd QRWifi
```

---

### 2. สร้าง Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Migrate Database

```bash
python manage.py migrate
```

---

### 5. สร้าง Admin

```bash
python manage.py createsuperuser
```

---

### 6. Run Server

```bash
python manage.py runserver
```

เปิด:

```
http://127.0.0.1:8000/
```

---

## 🔐 Admin

```
http://127.0.0.1:8000/admin/
```

---

## 🔁 Flow

```
Scan QR
→ เปิด LIFF
→ ได้ lineUserId
→ check-user
→ register / welcome
→ redirect WiFi
```
# QRWifi

Enterprise-ready WiFi Login System using LINE LIFF + Django

---

## 📌 Overview

QRWifi is a web-based WiFi authentication system that allows users to connect to WiFi by logging in via LINE (LIFF).  
The system identifies users using `lineUserId`, supports new user registration, and tracks all access activity.

---

## 🚀 Key Features

- LINE LIFF Authentication
- Automatic user recognition (no repeated registration)
- New user registration (name + phone)
- Access logging (IP Address, User Agent, Action)
- WiFi redirect integration (Captive Portal ready)
- Admin dashboard via Django Admin

---

## 🧱 Tech Stack

- Python 3.x
- Django 4.x
- SQLite (default, replaceable with PostgreSQL)
- LINE LIFF SDK

---

## 📦 Installation Guide (Windows)

### 1. Clone Repository

```bash
git clone https://github.com/norapat650/QRWifi.git
cd QRWifi
```

---

### 2. Setup Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Apply Database Migration

```bash
python manage.py migrate
```

---

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

---

### 6. Run Development Server

```bash
python manage.py runserver
```

Access system:

```
http://127.0.0.1:8000/
```

---

## 🔐 Admin Panel

```
http://127.0.0.1:8000/admin/
```

Use the superuser credentials created earlier.

---

## 🔄 System Flow

```
User scans QR Code
→ Opens LIFF
→ Retrieves lineUserId
→ Backend API (/check-user)
    ├── Existing User → /welcome
    └── New User → /register
→ Register (if needed)
→ Save to database
→ Redirect to WiFi login page
```

---

## 🗄 Database Structure

### WifiUser
- line_user_id (unique)
- first_name
- phone
- created_at
- updated_at

### WifiAccessLog
- line_user_id
- action
- ip_address
- user_agent
- created_at

---

## 🧪 Testing

Example API:

```
http://127.0.0.1:8000/check-user/?lineUserId=test001
```

Expected response:

```json
{
  "success": true,
  "is_registered": false
}
```

---

## ⚠️ Important Notes

- Internet connection is required for LINE LIFF
- Use ngrok for local testing with LIFF
- Ensure `line_user_id` is unique
- Replace WiFi redirect URL with actual router endpoint

---

## 📈 Future Improvements

- Dashboard analytics (user count, visits)
- Export user data (CSV)
- LINE OA broadcast integration
- Multi-location support
- Production deployment (Gunicorn + Nginx)

---

## 👨‍💻 Author

QRWifi Project  
Developed for real-world WiFi + LINE integration use case