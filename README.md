# One Pension One ID

> A modern pension management system for seamless pension tracking, grievance handling, and certificate management — all tied to a single ID.
# 📁 Project Report


## 📚 About
[ProjectReport.pdf](https://github.com/user-attachments/files/19976548/Final.Submission.pdf)

**One Pension One ID** is a Django-powered web application designed to centralize pensioner information and services.  
It simplifies pension tracking, grievance redressal, announcements, and life certificate submissions — all in one place.

## ✨ Features

- 🔒 **Secure Login and OTP Verification**
- 👤 **Role-Based Access** (Admin, Pensioner, etc.)
- 📄 **Life Certificate Management**
- 📢 **Announcement System**
- 📑 **Grievance Redressal Mechanism**
- 💳 **Pension History Tracking**
- 📊 **Dashboard for Admins and Pensioners**

## 🚀 Tech Stack

- Backend: **Django** (Python)
- Database: **PostgreSQL** (or SQLite for testing)
- Frontend: **Django Templates / Bootstrap**
- Authentication: **Django Auth** + **Custom OTP System**

## 🛠️ Installation Guide

1. **Clone the Repository**

   ```bash
   git clone https://github.com/SrikantAich/OnePensionOneID.git
   cd one-pension-one-id
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv env
   source env/bin/activate  # For Windows: env\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**

   - Update your `settings.py` with your database credentials.

5. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create Admin User**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**

   ```bash
   python manage.py runserver
   ```

8. **Access**

   - Admin Panel: `http://127.0.0.1:8000/admin/`
   - Main App: `http://127.0.0.1:8000/`



## 🧪 Testing

Run all tests using:

```bash
python manage.py test
```

## 🤝 Contributing

Contributions are welcome!  
Feel free to fork this project, make your changes, and submit a pull request.

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
