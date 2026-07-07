# ⚔️ Skill Duel

> **Skill Duel** is a full-stack web application where players challenge each other in competitive **1v1 skill battles**. Test your knowledge in **Coding** and **Math**, earn victories, climb the global leaderboard, and unlock legendary ranks.

## 🌐 Live Demo

**Try it here:**  
https://skill-duel-django-production.up.railway.app/


# ✨ Features

## 🎯 Duel Arena
- Challenge other players to exciting **1v1 battles**
- Choose a category:
  - 💻 Coding
  - ➗ Math
- Each duel consists of **5 multiple-choice questions**
- Fair, fast, and competitive gameplay

## ⚡ Auto Scoring
- Instant score calculation
- Automatic winner determination
- Accurate scoring with no manual intervention

## 🏆 Global Leaderboard
Compete against players worldwide and earn prestigious ranks:

| Rank | Badge |
|------|--------|
| 🥉 Bronze | Beginner |
| 🥈 Silver | Skilled |
| 🥇 Gold | Expert |
| 💎 Platinum | Elite |
| 👑 Legend | Top Players |

## 👤 User Profiles
Track your progress with:
- Total Wins
- Total Losses
- Win Rate
- Overall Statistics

## 📬 In-App Inbox
- View incoming challenges
- Track sent requests
- Monitor active duels

## 🛠 Admin Dashboard
Administrators can easily:
- Add Coding questions
- Add Math questions
- Manage the question bank

---

# 🛠 Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Python 3.12 |
| Framework | Django 4.x |
| Database | PostgreSQL (Production), SQLite (Development) |
| Frontend | Bootstrap 5, Tabler Icons |
| Deployment | Railway |

---

# 🚀 Getting Started

## Prerequisites

- Python 3.12+
- Git

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/skill-duel-django.git

# Navigate to the project directory
cd skill-duel-django

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt

#Database migrations
python manage.py makemigrations
python manage.py migrate

#Development server
python manage.py runserver

Open your browser and go to http://127.0.0.1:8000/
```

## Project Structure

The application follows a standard Django project structure:

Models
- **User**: Represents a player with attributes like username, email, password, and profile information.
- **Question**: Represents a question in the duel, including the question text, options,
- **Duel**: Represents a duel between two players, including the questions, scores, and winner.
- **DuelQuestion**: Represents the relationship between a duel and its questions, including the player's answers and scores.
- **Answer**: Represents the answers provided by players during a duel, including the selected option and correctness.

Views
- **Home View**: Displays the main page with options to start a duel or view the leaderboard.
- **Duel View**: Handles the logic for a 1v1 duel, including question display and answer submission.
- **Leaderboard View**: Shows the global leaderboard with player rankings.
- **Profile View**: Allows users to view their profile information and statistics.

Templates
- shared **base.html**
- Reusable Components

## 📈 Future Roadmap
- ✅ Build a REST API using Django REST Framework
- ✅ Add WebSockets (Django Channels) for real-time duels
- ✅ Introduce 30-second timed rounds
- ✅ Add comprehensive pytest unit and integration tests
- ✅ Improve matchmaking and player statistics

## 📸 Highlights
- 🎮 Competitive 1v1 gameplay
- ⚡ Instant scoring
- 🏆 Global rankings
- 👥 User profiles
- 📬 Challenge inbox
- 🛡 Django admin management
- ☁️ Deployed on Railway


## 👤 Author

Developed by **Shanuka Upendra**

GitHub: **@shanuka-upendra**  
https://github.com/shanuka-upendra
