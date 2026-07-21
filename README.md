# ♻️ ECycle — Smart E-Waste Pickup & Recycling Platform

**ECycle** is an AI-powered, full-stack web application designed to streamline doorstep electronic waste pickup, device classification, CO₂ carbon footprint estimation, and eco-reward redemption. 

Developed in **2025** as the **4th Year Major Capstone Project** for **B.E. in Electronics and Computer Science Engineering (Honours in Artificial Intelligence & Machine Learning)** at **SIES Graduate School of Technology, Mumbai** by **Jailingam Santhanakumar**.

---

## 🌟 Key Features

* 📷 **Roboflow AI E-Waste Classification:** Snap a photo on a mobile device or upload an image to automatically detect device type, condition, and estimated eco-points.
* 🚚 **Doorstep Individual & Enterprise Bulk Pickups:** Schedule collection requests for homes or organizations with automated price estimations.
* 📜 **Disposal Certificates:** Automatically generates downloadable PDF green disposal certificates (powered by ReportLab).
* 🎁 **Eco-Rewards Store:** Redeem earned eco-points for real-world gift cards, vouchers, and sustainable products.
* 💬 **E-Talk Community Feed:** A real-time, Twitter/X-style social feed with verified recycler checkmarks, gold admin badges, hashtags, and instant post updates.
* 👑 **God-Mode Admin Portal:** Full administrative management over users, individual pickups, bulk pickup requests, inventory items, and rewards catalog.
* 📱 **100% Mobile Responsive:** Fluid glassmorphism UI with touch-friendly controls, 44px touch targets, and native camera integration.

---

## 🛠️ Technology Stack

* **Backend Framework:** Python 3.11, Flask
* **Database & ORM:** SQLite / PostgreSQL (Flask-SQLAlchemy)
* **AI & Machine Learning:** Roboflow Serverless Inference SDK (`e-waste-dataset-r0ojc/43`)
* **Frontend:** HTML5, Modern Vanilla CSS3 (Glassmorphism Design System), JavaScript (ES6+ AJAX)
* **PDF Generation:** ReportLab PDF Engine
* **Production Server:** Gunicorn WSGI

---

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jai30603/E-Cycle.git
cd E-Cycle
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root (or copy `.env.example`):
```env
SESSION_SECRET=your_secure_random_key_here
ROBOFLOW_API_KEY=ziswnQ61DQjFX1EST8IO
ROBOFLOW_API_URL=https://serverless.roboflow.com
```

### 4. Run Development Server
```bash
python main.py
```
Open **http://127.0.0.1:8000** in your browser.

---

## ☁️ Deployment Guide (Render.com)

1. Push this repository to **GitHub**.
2. Log in to [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your **E-Cycle** repository.
4. Configure service settings:
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn main:app`
5. Add **Environment Variables** in Render Dashboard:
   * `ROBOFLOW_API_KEY` = `ziswnQ61DQjFX1EST8IO`
   * `ROBOFLOW_API_URL` = `https://serverless.roboflow.com`
   * `SESSION_SECRET` = `<your_production_secret>`
6. Click **Deploy Web Service**! 🚀

---

## 👨‍💻 Project Developer Profile

* **Developer:** Jailingam Santhanakumar
* **Current Role:** Software Developer / Apprentice Tech Developer at **Barclays Bank PLC**
* **Education:** B.E. Electronics & Computer Science Engineering (CGPA: 9.67/10), SIES GST Mumbai (2021 – 2025)
* **Honours:** Artificial Intelligence & Machine Learning
* **Contact:** [jailingesh30603@gmail.com](mailto:jailingesh30603@gmail.com) | [LinkedIn](https://linkedin.com/in/jailingam-santhanakumar) | [GitHub](https://github.com/jai30603)

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
