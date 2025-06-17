# **AILearningMate**

**an AI-powered personalized learning platform built with Django. It connects learners and tutors through adaptive course content, interactive lessons, discussions, and real-time performance tracking**

---

## **📘 Project Overview**

A Django-based e-learning platform that leverages AI to:

- **Personalize learning paths** with course recommendations.
- **Automate assessments** via AI-generated quizzes.
- **Facilitate discussions** among learners and instructors.
- **Track progress** using AI analytics.

**Target Users**:

- **Learners**: Enroll in courses, take quizzes, track progress.
- **Instructors/Tutors**: Create courses, design quizzes, moderate discussions.
- **Admins**: Manage users, content, and platform settings.

---

## **⚙️ Installation & Setup**

### **Prerequisites**

- Python 3.7
- OpenAI API key (for AI features)

### **Steps**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/kimmich14/AILearningMate.git
   cd AILearningMate
   ```

2. **Set Up Environment**:

   - Create `.env` file:
     ```
     SECRET_KEY=your_django_secret_key
     DATABASE_URL=postgres://user:password@localhost:5432/ailm_db
     OPENAI_API_KEY=your_openai_key
     DEBUG=True
     ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Start the Server**:
   ```bash
   python manage.py runserver
   ```
   Access at: `http://localhost:8000`

---

## **🔐 Authentication & User Roles**

### **User URLs (`usersapp/urls.py`)**

| URL                | Description                                                               | User Role                  |
| ------------------ | ------------------------------------------------------------------------- | -------------------------- |
| `/signup/`         | User registration with email/password.                                    | Guest → Learner/Instructor |
| `/login/`          | Login page with role-based redirect.                                      | All                        |
| `/logout/`         | Logs out the user.                                                        | Authenticated              |
| `/profile/`        | View/update user profile (e.g., bio, profile picture).                    | Authenticated              |
| `/dashboard/`      | Learner dashboard: Shows enrolled courses, quiz results, progress.        | Learner                    |
| `/instructor/`     | Instructor dashboard: CRUD for courses/quizzes, view student submissions. | Instructor                 |
| `/password-reset/` | Password reset flow with email confirmation.                              | All                        |

---

## **🗺️ Feature Breakdown**

### **1. Course Management (`learningapp/urls.py`)**

| URL                        | Description                                                                |
| -------------------------- | -------------------------------------------------------------------------- |
| `/`                        | Homepage: Recommended courses based on user’s learning history.            |
| `/courses/`                | Lists all available courses with filters (e.g., topic, difficulty).        |
| `/course/<int:course_id>/` | Course details + enrollment button. Enrolled users access lessons/quizzes. |
| `/enroll/<int:course_id>/` | Enrolls a user in a course.                                                |

### **2. AI Tutor & Quizzes**

| URL                                 | Description                                              |
| ----------------------------------- | -------------------------------------------------------- |
| `/ai-tutor/`                        | AI-powered tutor: Answers questions, suggests resources. |
| `/quiz/<int:quiz_id>/`              | Take a quiz (MCQ/essay) with timer.                      |
| `/quiz/<int:quiz_id>/start/`        | Restart a quiz (if attempts remain).                     |
| `/submit-quiz/`                     | Submit quiz answers for AI grading.                      |
| `/quiz-result/<int:result_id>/pdf/` | Export quiz results as PDF.                              |

### **3. Progress Tracking**

| URL             | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| `/progress/`    | Visualizes learning progress (e.g., course completion, quiz scores).  |
| `/assessments/` | AI-generated insights on performance (weak areas, suggested reviews). |

### **4. Community & Support**

| URL                   | Description                                 |
| --------------------- | ------------------------------------------- |
| `/submit-discussion/` | Post questions to course discussion boards. |
| `/submit-reply/`      | Reply to discussions.                       |
| `/about-us/`          | Platform mission, team, and FAQs.           |
| `/support/`           | Contact support team for technical issues.  |

---

## **🧪 Testing**

Run tests with:

```bash
python manage.py test learningapp usersapp
```

- Includes unit tests for:
  - User authentication.
  - Quiz submission logic.
  - Course enrollment permissions.

---

## **🚀 Deployment Guide**

### **Heroku**

1. **Procfile**:
   ```
   web: gunicorn AILearningMate.wsgi --log-file -
   ```
2. **Deploy**:
   ```bash
   heroku create
   git push heroku main
   heroku run python manage.py migrate
   ```

### **Gunicorn + Nginx**

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Start Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:8000 AILearningMate.wsgi
   ```

---

## **🧩 Tech Stack**

- **Backend**: Django,
- **Frontend**: Bootstrap, HTMX (for dynamic UI), JavaScript, jQuery & AJAX
- **AI**: OpenAI API
- **Database**: SQLite
- **Other**: WeasyPrint (for async tasks like PDF generation)

---

## **📁 Directory Structure**

```
AILearningMate/
├── learningapp/               # Core learning features
│   ├── models.py             # Course, Quiz, Discussion models etc
│   ├── views.py              # All views (home, quizzes, AI tutor etc)
├── usersapp/                 # Authentication & profiles
│   ├── models.py             # Custom User model
│   └── views.py              # Signup, login, dashboards, Profile
├── static/                   # CSS, JS, images
├── templates/                # HTML templates
├── requirements.txt          # Dependencies
```

---

## **🧑‍💻 Contributing**

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Submit a pull request with tests.

---

## **📜 License**

MIT License (see `LICENSE` file).
