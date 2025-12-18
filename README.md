# 🩺 Health Tracker

**Project Overview**  

Health Tracker is a **console-based Python application** that helps users track their daily health metrics including **water intake, sleep, exercise, and mood**. It provides **personalized health insights**, calculates **BMI**, gives **diet and exercise suggestions**, and allows exporting a **shareable PDF health report**. The project encourages healthy habits and monitors progress with a **streak system** and weekly summaries.

---

## **🚀 Features**

- 📝 **Log daily metrics**: Water, Sleep, Exercise, Mood  
- ⚠️ **Smart alerts** for low water intake, insufficient sleep, or low exercise  
- 📊 **Health summary** with BMI and status  
- 🍴 **Diet suggestions** based on BMI and age  
- 🏃 **Exercise suggestions** tailored to fitness goals  
- 📅 **Weekly summary** and streak tracking for motivation  
- 📄 **Exportable PDF health report** including:
  - User name
  - Date
  - BMI & status
  - Food and exercise suggestions
  - All logged metrics  
- 💡 **Daily health tips** for guidance  

---

## **🛠️ Tech Stack**

- **Python 3** – Core language  
- **SQLite3** – Database for user and logs  
- **Colorama** – Colored console output  
- **ReportLab** – PDF report generation  
- **Hashlib** – Secure password hashing  

---

## **Project Structure**
health-tracker/
      
      ├── tracker.py # Main Python program
      ├── health_tracker.db # SQLite database (auto-created)
      ├── health_report.pdf # Generated PDF report
      ├── README.md # Project documentation
      ├── .gitignore # Git ignore file
      └── requirements.txt # Python dependencies

1. Clone the repository

      git clone https://github.com/HARRINI916/health-tracker.git
      cd health-tracker

2. Install Python dependencies

      pip install colorama reportlab

3. Run the project

      python tracker.py

**How Health Tracker Works**

**User Authentication**

Register a new account with username & password

Login to access your personal health data

Logging Metrics

Log water intake, sleep hours, exercise minutes, and mood

Health Summary

View BMI, daily/weekly metrics, and streaks

Get personalized diet and exercise suggestions

Weekly Report

Displays averages of your metrics over the last 7 days

Export PDF Report

Generates a shareable PDF with all metrics and recommendations

Auto-opens for viewing

**Usage Example**

**Register a new user:**

1. Register
  
2. Login
   
Choose: 1

Username: HARRINI

Password: YourPassword

Age: 22

Weight (kg): 55

Height (cm): 160

✅ Registration successful!

**Login:**

1. Register
  
2. Login
   
Choose: 2

Username: HARRINI

Password: YourPassword

✅ Login successful!

**Main Menu:**

1. Log Water

2. Log Sleep

3. Log Exercise

4. Log Mood

5. View Summary

6. Weekly Report

7. Export Report (PDF)

8. Exit

**📦 Running Locally**

Track daily metrics and mood

View summary for current progress

Export a personalized PDF report for sharing

Future Enhancements

Add GUI version with Tkinter or PyQt

Implement email notifications for daily reminders

Add cloud storage for multi-device syncing

Integrate AI suggestions for health improvement

Add graphs for better visualization of progress

**AUTHOR**

HARRINI D S

GitHub: https://github.com/HARRINI916
