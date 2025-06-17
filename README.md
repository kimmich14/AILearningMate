---

## 📘 LearnMate

**LearnMate** is an AI-powered personalized learning platform built with Django. It connects learners and tutors through adaptive course content, interactive lessons, discussions, and real-time performance tracking.

---

### 🚀 Features

- 🎓 User Roles: Learners and Tutors with tailored dashboards
- 📚 Course & Lesson Management
- 🖼️ Video/Image Support per Lesson
- 💬 Discussion Boards with Replies
- ✅ AI-Recommended Learning Paths _(coming soon)_
- 🔐 Authentication and Role-Based Redirection
- 📈 Progress Tracking
- 🎨 Responsive Frontend using HTML/CSS + Django Templating

---

### 🏗️ Tech Stack

- **Backend:** Django, Python 3
- **Frontend:** HTML5, CSS3, Bootstrap
- **Database:** SQLite (Dev), PostgreSQL (Production-ready)
- **Media Handling:** Django Media & Static files
- **User Management:** Custom `User` model (with `learner` and `tutor` roles)

---

### 📂 Project Structure Overview

```
LearnMate/
├── learning/             # App for courses, lessons, discussions
├── users/                # Custom user model and authentication logic
├── templates/            # All HTML templates
├── static/               # CSS/JS/Images
├── media/                # User-uploaded files (e.g., course images)
├── manage.py
└── db.sqlite3
```

---

### 🧑‍💻 Setup Instructions

1. **Clone the Repo:**

   ```bash
   git clone https://github.com/yourusername/LearnMate.git
   cd LearnMate
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Server:**

   ```bash
   python manage.py runserver
   ```

7. **Access the App:**
   Visit `http://127.0.0.1:8000/` in your browser.

---

### 🔑 Default Credentials (for demo)

```
Email: demo@learnmate.com
Password: learn123
```

> _(Only if using test fixtures — otherwise create manually via admin panel)_

---

### 📌 TODOs / Future Improvements

- [ ] AI-generated quiz generation
- [ ] Real-time tutor messaging
- [ ] Student activity heatmaps
- [ ] Tutor rating system

---

### 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---
