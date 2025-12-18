import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import platform

init(autoreset=True)

DB = "health_tracker.db"

GOALS = {
    "water": 2500,     # ml
    "sleep": 7,        # hours
    "exercise": 30     # minutes
}

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        age INTEGER,
        weight REAL,
        height REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        value REAL,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mood (
        user_id INTEGER,
        mood INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------- AUTH ----------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    username = input("Username: ")
    password = hash_password(input("Password: "))
    age = int(input("Age: "))
    weight = float(input("Weight (kg): "))
    height = float(input("Height (cm): "))

    try:
        cur.execute(
            "INSERT INTO users VALUES (NULL,?,?,?,?,?)",
            (username, password, age, weight, height)
        )
        conn.commit()
        print(Fore.GREEN + "✅ Registration successful!")
    except sqlite3.IntegrityError:
        print(Fore.RED + "❌ Username already exists")
    conn.close()

def login():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    username = input("Username: ")
    password = hash_password(input("Password: "))

    cur.execute(
        "SELECT id, age, weight, height FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cur.fetchone()
    conn.close()

    if user:
        print(Fore.GREEN + "✅ Login successful!")
        return user
    else:
        print(Fore.RED + "❌ Invalid credentials")
        return None

# ---------------- LOGGING ----------------
def log_metric(user_id, mtype, value):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO logs VALUES (NULL,?,?,?,?)",
        (user_id, mtype, value, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

    # Smart warnings
    if mtype == "water" and value < 500:
        print(Fore.YELLOW + "Low water intake for this entry")
    if mtype == "sleep" and value < 7:
        print(Fore.RED + "Sleep less than recommended")
    if mtype == "exercise" and value < 30:
        print(Fore.YELLOW + " Try to exercise more")

# ---------------- BMI ----------------
def bmi_status(weight, height_cm):
    h = height_cm / 100
    bmi = weight / (h * h)
    if bmi < 18.5:
        return bmi, "Underweight"
    elif bmi < 25:
        return bmi, "Normal"
    else:
        return bmi, "Overweight"

def food_and_exercise_suggestions(bmi, age):
    if bmi < 18.5:
        food = """
FOOD TO GAIN WEIGHT:
• Milk, curd, paneer
• Rice, chapati, potatoes
• Bananas, dates
• Eggs, peanut butter
"""
        exercise = """
EXERCISE:
• Strength training
• Resistance workouts
• Avoid excess cardio
"""
    elif bmi < 25:
        food = """
FOOD TO MAINTAIN WEIGHT:
• Balanced meals
• Fruits & vegetables
• Adequate protein
"""
        exercise = """
EXERCISE:
• Walking / jogging
• Yoga or stretching
"""
    else:
        food = """
FOOD TO LOSE WEIGHT:
• Vegetables, fruits
• Oats, brown rice
• Lean protein (dal, eggs)
• Avoid sugar & junk food
"""
        exercise = """
EXERCISE:
• Brisk walking
• Cardio (cycling, skipping)
• HIIT workouts
"""

    if age > 40:
        exercise += "\nFocus on yoga & flexibility"
    elif age < 18:
        food += "\nInclude calcium-rich foods"

    return food, exercise

# ---------------- STREAK ----------------
def streak(user_id, mtype):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    count = 0
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        cur.execute(
            "SELECT 1 FROM logs WHERE user_id=? AND type=? AND date=?",
            (user_id, mtype, day)
        )
        if cur.fetchone():
            count += 1
        else:
            break
    conn.close()
    return count

# ---------------- MOOD ----------------
def log_mood(user_id):
    mood = int(input("Mood today (1–5): "))
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mood VALUES (?,?,?)",
        (user_id, mood, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

# ---------------- SUMMARY ----------------
def summary(user_id, age, weight, height):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    data = {}
    for m in ["water", "sleep", "exercise"]:
        cur.execute(
            "SELECT SUM(value) FROM logs WHERE user_id=? AND type=?",
            (user_id, m)
        )
        data[m] = cur.fetchone()[0] or 0

    bmi, status = bmi_status(weight, height)
    food, exercise_tip = food_and_exercise_suggestions(bmi, age)

    conn.close()

    print(Fore.CYAN + "\nHEALTH SUMMARY")
    print(f"Water: {data['water']} / {GOALS['water']} ml")
    print(f"Sleep: {data['sleep']} hrs")
    print(f"Exercise: {data['exercise']} mins")

    print(Fore.YELLOW + f"\nBMI: {bmi:.2f}")
    print(Fore.MAGENTA + f"Status: {status}")

    if data["water"] < GOALS["water"]:
        print(Fore.RED + "Low water intake")
    if data["sleep"] < GOALS["sleep"]:
        print(Fore.RED + "Sleep is insufficient")
    if data["exercise"] < GOALS["exercise"]:
        print(Fore.RED + "Low physical activity")

    print(Fore.GREEN + f"\nWater Streak: {streak(user_id, 'water')} days")

    print(Fore.BLUE + "\nDIET SUGGESTION")
    print(food)

    print(Fore.BLUE + "EXERCISE SUGGESTION")
    print(exercise_tip)

# ---------------- WEEKLY REPORT ----------------
def weekly_report(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cur.execute(
        """
        SELECT type, AVG(value) 
        FROM logs 
        WHERE user_id=? AND date(date) >= date(?) 
        GROUP BY type
        """,
        (user_id, since)
    )

    rows = cur.fetchall()
    print(Fore.MAGENTA + "\nWEEKLY REPORT")
    if not rows:
        print("No logs found in last 7 days")
    for t, avg in rows:
        print(f"{t}: {round(avg,2)}")

    conn.close()

# ---------------- EXPORT PDF ----------------
def export_report(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # User info
    cur.execute("SELECT username, age, weight, height FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    username, age, weight, height = user

    # Logs
    cur.execute("SELECT type, value, date FROM logs WHERE user_id=?", (user_id,))
    logs = cur.fetchall()
    conn.close()

    bmi, status = bmi_status(weight, height)
    food, exercise_tip = food_and_exercise_suggestions(bmi, age)

    pdf_file = "health_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height_page = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height_page - 50, f"📄 Health Report: {username}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height_page - 80, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    y = height_page - 120

    # BMI & status
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f" BMI: {bmi:.2f} | Status: {status}")
    y -= 30

    # Food suggestions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Diet Suggestions:")
    y -= 20
    c.setFont("Helvetica", 11)
    for line in food.strip().splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height_page - 50

    # Exercise suggestions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Exercise Suggestions:")
    y -= 20
    c.setFont("Helvetica", 11)
    for line in exercise_tip.strip().splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height_page - 50

    # Logs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "📊 Logged Metrics:")
    y -= 20
    c.setFont("Helvetica", 11)
    if not logs:
        c.drawString(60, y, "No logs found.")
        y -= 15
    else:
        for log in logs:
            c.drawString(60, y, f"{log[2]} | {log[0].capitalize()} | {log[1]}")
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height_page - 50

    c.save()
    print(Fore.GREEN + f"📄 Health report exported to {pdf_file}!")

    # Auto-open PDF
    try:
        if platform.system() == "Windows":
            os.startfile(pdf_file)
        elif platform.system() == "Darwin":
            os.system(f"open {pdf_file}")
        else:
            os.system(f"xdg-open {pdf_file}")
    except Exception as e:
        print(Fore.YELLOW + f"⚠️Could not auto-open PDF: {e}")

# ---------------- TIP ----------------
def show_tip():
    tips = [
        "Drink water before meals",
        "Sleep boosts immunity",
        "Walking improves mental health",
        "Consistency beats intensity"
    ]
    print(Fore.BLUE + "Tip to improve health:", random.choice(tips))

# ---------------- MAIN ----------------
def main():
    init_db()
    show_tip()

    print("\n1. Register\n2. Login")
    choice = input("Choose: ")

    user = None
    if choice == "1":
        register()
        return
    elif choice == "2":
        user = login()
    else:
        return

    if not user:
        return

    user_id, age, weight, height = user

    while True:
        print("""
1. Log Water
2. Log Sleep
3. Log Exercise
4. Log Mood
5. View Summary
6. Weekly Report
7. Export Report (PDF)
8. Exit
""")
        c = input("Choose: ")

        if c == "1":
            log_metric(user_id, "water Intake", float(input("Water (ml): ")))
        elif c == "2":
            log_metric(user_id, "sleep Hours", float(input("Sleep (hrs): ")))
        elif c == "3":
            log_metric(user_id, "exercise Time", float(input("Exercise (mins): ")))
        elif c == "4":
            log_mood(user_id)
        elif c == "5":
            summary(user_id, age, weight, height)
        elif c == "6":
            weekly_report(user_id)
        elif c == "7":
            export_report(user_id)
        elif c == "8":
            print(Fore.GREEN + " Stay healthy Always!")
            break

if __name__ == "__main__":
    main()
