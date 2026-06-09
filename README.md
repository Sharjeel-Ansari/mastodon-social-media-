# ⚡ Vibe — Social Media App

A full-featured social media web app built with **Django + HTML/CSS/JavaScript**.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd socialapp
pip install -r requirements.txt
```

### 2. Apply database migrations
```bash
python manage.py makemigrations core
python manage.py migrate
```

### 3. Create a superuser (admin)
```bash
python manage.py createsuperuser
```

### 4. Run the development server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/
```

---

## 📁 Project Structure

```
socialapp/
├── manage.py
├── requirements.txt
├── README.md
├── socialapp/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                # Main app
│   ├── models.py        # User, Post, Comment, Like, Follow, Notification
│   ├── views.py         # All view logic
│   ├── urls.py          # URL routing
│   ├── forms.py         # Form definitions
│   ├── admin.py         # Admin panel config
│   ├── context_processors.py
│   └── templatetags/
│       └── social_tags.py
├── templates/
│   ├── base.html        # Base layout with sidebar
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── feed/
│   │   ├── index.html       # Main feed
│   │   ├── explore.html     # Search & explore
│   │   ├── post_detail.html
│   │   └── notifications.html
│   ├── profile/
│   │   ├── profile.html
│   │   └── edit_profile.html
│   └── partials/
│       └── post_card.html
└── static/
    ├── css/style.css    # Full dark theme design
    ├── js/main.js       # Interactive features
    └── images/          # Default assets
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auth** | Register, Login, Logout with custom User model |
| **User Profiles** | Avatar, cover photo, bio, location, website |
| **Posts** | Create with text + image, delete, feed display |
| **Comments** | Add/delete via modal or post detail page |
| **Likes** | Toggle likes with animated heart |
| **Follow System** | Follow/unfollow users, follower/following counts |
| **Notifications** | Like, comment, follow notifications with unread badge |
| **Explore** | Search posts and users |
| **Responsive** | Mobile-friendly with collapsible sidebar |

---

## 🎨 Design

- **Theme**: Dark luxury (deep navy + electric purple + coral accents)
- **Fonts**: Outfit (headings) + Plus Jakarta Sans (body)
- **Animations**: Smooth fade-ins, hover states, modal transitions
- **Layout**: Sidebar navigation + centered feed + right panel

---

## 🛠 Tech Stack

- **Backend**: Django 4.2, SQLite
- **Frontend**: HTML5, CSS3 (custom), Vanilla JavaScript
- **Auth**: Django's built-in auth with custom User model
- **Media**: Pillow for image handling
