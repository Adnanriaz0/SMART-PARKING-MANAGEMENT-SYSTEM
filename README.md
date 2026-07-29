# 🚗 Smart Parking Management System

An IoT-based Smart Parking Management System developed using **Flask, Python, MySQL, ESP32, ESP32-CAM, RFID RC522, and Servo Motor**. The system provides real-time parking slot reservation, RFID-based vehicle authentication, license plate verification, automated gate control, payment verification, and centralized parking management through a responsive web application.

---

## 📌 Features

- 👤 User Registration & Login
- 🚘 Vehicle Registration
- 📍 Parking Location Management
- 🅿️ Real-Time Parking Slot Reservation
- 💳 Parking Package Management
- 📤 Payment Proof Upload
- ✅ Payment Verification by Admin
- 🔐 RFID-Based Vehicle Authentication
- 📷 License Plate Verification using ESP32-CAM
- 🚪 Automated Gate Control using Servo Motor
- 📊 Admin Dashboard
- 📈 Real-Time Parking Monitoring
- 🔒 Secure REST API Communication
- 🔑 Device Token Authentication

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 Templates

### Backend
- Python
- Flask
- REST APIs

### Database
- MySQL

### IoT Hardware
- ESP32
- ESP32-CAM
- RFID RC522
- SG90 Servo Motor

### Development Tools
- Visual Studio Code
- Arduino IDE
- Git
- GitHub

---

## 🏗️ System Architecture

```
Vehicle Owner
      │
      ▼
Web Application (HTML, Bootstrap, JS)
      │
      ▼
Flask Backend (REST APIs)
      │
      ├────────────► MySQL Database
      │
      ├────────────► ESP32
      │                  │
      │                  ├── RFID RC522
      │                  └── Servo Motor
      │
      └────────────► ESP32-CAM
                         │
                         └── License Plate Capture
```

---

## 📂 Project Structure

```
SMART-PARKING-MANAGEMENT-SYSTEM/
│
├── app.py
├── config.py
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│
├── templates/
│
├── models/
│
├── routes/
│
├── utils/
│
├── uploads/
│
├── database/
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Adnanriaz0/SMART-PARKING-MANAGEMENT-SYSTEM.git
```

### 2. Go to Project Folder

```bash
cd SMART-PARKING-MANAGEMENT-SYSTEM
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure MySQL Database

- Create a MySQL database.
- Update your database credentials in the configuration file.

### 7. Run the Application

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 📸 System Modules

- User Management
- Package Management
- Payment Management
- Parking Slot Management
- Booking Management
- RFID Authentication
- License Plate Verification
- Admin Dashboard
- IoT Device Authentication

---

## 🔐 Security Features

- Secure User Authentication
- Password Hashing
- Device Token Authentication
- REST API Protection
- RFID-Based Vehicle Verification
- Role-Based Access Control

---

## 🚀 Future Enhancements

- Mobile Application
- Online Payment Gateway
- AI-Based Parking Analytics
- Smart Navigation
- Smart City Integration
- QR Code Entry System
- Push Notifications

---

## 👨‍💻 Author

**Adnan Riaz**

- 📧 Email: adnanriaz2222@gmail.com
- 💼 LinkedIn: https://www.linkedin.com/in/adnan-riaz-a4a336279
- 🌐 Portfolio: https://adnan-riaz-portfolio.web.app
- 🐙 GitHub: https://github.com/Adnanriaz0

---

## 📄 License

This project is developed for educational and research purposes.

---

## ⭐ Support

If you like this project, don't forget to ⭐ star the repository.
