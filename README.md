# 🐾 Paws & Hearts — Pet Adoption and Management Portal

<p align="center">
  <img src="assets/home.png" alt="Paws & Hearts Home Page" width="100%">
</p>

<p align="center">
A full-stack Pet Adoption and Management web application built with <strong>Django 4.2</strong>. Users can browse pets, submit adoption applications, and surrender pets for rehoming. Admins manage everything through a dedicated dashboard with email notifications throughout.
</p>

<p align="center">
  <strong>🌐 Live Site: <a href="https://pet-adoption-and-management-74e2.onrender.com">https://pet-adoption-and-management-74e2.onrender.com</a></strong>
</p>

---

## 🌟 Features

### For Adopters
- Register and log in securely (email as username, rate-limited login)
- Browse available pets with filters (species, breed, gender, size, age, location)
- View full pet profiles with photo galleries
- Submit and track adoption applications
- Receive email confirmation on submission and status updates

### For Admins
- Register via secret key (set in environment variable)
- Dashboard with live stats: available pets, pending applications, new surrenders, total adopters
- Full pet management — add, edit, delete, upload photos
- Review adoption applications (pending → under review → approved / rejected)
- Approve application → auto-marks pet as adopted, rejects competing applications, sends email
- Manage adopter accounts (deactivate / reactivate)
- Process pet surrender requests (submitted anonymously, no login required)

### General
- Custom 404, 403, 500 error pages
- Responsive design — works on desktop, tablet, and mobile
- WCAG 2.1 AA accessible (4.5:1 colour contrast, keyboard nav, skip links, ARIA labels)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2.30, Python 3.x |
| Database | SQLite (dev) / PostgreSQL via Neon (production) |
| Hosting | Render |
| Static files | WhiteNoise 6.9.0 |
| Image handling | Pillow 10.4.0 |
| WSGI server | Gunicorn 23.0.0 |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Fonts | Google Fonts — Nunito + Inter |

---

## 📸 Screenshots

### 🏠 Home Page
<p align="center"><img src="assets/home.png" width="90%"></p>

### 🔐 Login Page
<p align="center"><img src="assets/login.png" width="90%"></p>

### 🐶 Browse Pets
<p align="center"><img src="assets/pet-list.png" width="90%"></p>

### 📊 Admin Dashboard
<p align="center"><img src="assets/dashboard.png" width="90%"></p>

---

## 📂 Project Structure

```
Pet-Adoption-And-Management/
├── accounts/               # Auth: register, login, logout, UserProfile model
│   ├── decorators.py       # @admin_required, @adopter_required
│   ├── forms.py            # AdopterRegistrationForm, AdminRegistrationForm, LoginForm
│   ├── models.py           # UserProfile (role: admin | adopter)
│   └── views.py            # register, admin_register, login, logout
├── adoptions/              # Adoption applications
│   ├── models.py           # AdoptionApplication
│   ├── forms.py            # AdoptionApplicationForm
│   └── views.py            # apply, my_applications, detail, admin review/approve/reject
├── dashboard/              # Admin dashboard (no models — view aggregator)
│   └── views.py            # home, user_list, user_detail
├── notifications/          # Email helpers (not a Django app)
│   └── emails.py           # send_application_confirmation, send_status_update, send_surrender_notification
├── pets/                   # Pet listings
│   ├── models.py           # Pet, PetPhoto
│   ├── forms.py            # PetFilterForm, PetPhotoForm
│   └── views.py            # browse, detail, admin CRUD
├── surrenders/             # Anonymous surrender requests
│   ├── models.py           # SurrenderRequest
│   ├── forms.py            # SurrenderRequestForm
│   └── views.py            # public form, admin list/detail
├── pet_adoption/           # Project config
│   ├── settings.py
│   ├── urls.py             # Root URL conf + home_view
│   └── error_views.py      # Custom 403/404/500 handlers
├── static/
│   ├── css/style.css       # Full design system (orange theme)
│   ├── js/forms.js         # Form helpers (landlord toggle, double-submit prevention)
│   ├── js/pets.js          # Dynamic breed dropdown + photo gallery
│   └── images/             # SVG placeholder images per species
├── templates/
│   ├── base.html           # Master layout
│   ├── navbar.html
│   ├── home.html           # Hero + featured pets + stats
│   ├── 403.html / 404.html / 500.html
│   ├── accounts/
│   ├── pets/
│   ├── adoptions/
│   ├── surrenders/
│   └── dashboard/
├── media/                  # Uploaded pet photos (gitignored)
├── THEORY/                 # Documentation files
├── build.sh                # Render build script
├── requirements.txt
├── runtime.txt
├── manage.py
└── .env                    # Local secrets (gitignored)
```

---

## 🚀 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/Sujal00005/Pet-Adoption-And-Management.git
cd Pet-Adoption-And-Management
```

### 2. Create and activate a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `.env` file in the project root:

```env
# Database — omit DATABASE_URL to use SQLite locally
DATABASE_URL=postgresql://user:password@host/dbname

# Email (Gmail SMTP)
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
ADMIN_EMAIL=your-gmail@gmail.com
```

> **Never commit `.env` to Git** — it's already in `.gitignore`.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin account

**Option A — via the web UI:**
Visit `http://127.0.0.1:8000/accounts/admin-register/` and enter the admin registration key (set via the `ADMIN_REGISTRATION_KEY` environment variable in your `.env` file).

**Option B — via Django's built-in superuser:**
```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`

---

## 🌐 Deployment (Render + Neon)

### Database (Neon PostgreSQL)
1. Create a free account at [neon.tech](https://neon.tech)
2. Create a project and copy the connection string

### Hosting (Render)
1. Connect your GitHub repo on [render.com](https://render.com)
2. Create a new Web Service with:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn pet_adoption.wsgi:application`
3. Add environment variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | A long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Your Neon connection string |
| `ALLOWED_HOSTS` | `pet-adoption-and-management-74e2.onrender.com` |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |
| `ADMIN_EMAIL` | Inbox for surrender notifications |

Push to `main` — Render auto-deploys via `build.sh` which runs:
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## 🔐 Security Notes

- Login is rate-limited: 5 failed attempts per IP per 15 minutes (Django cache)
- Admin registration requires a secret key (`ADMIN_REGISTRATION_KEY` in settings)
- `@admin_required` decorator raises 403 for non-admins; `@adopter_required` requires any login
- CSRF protection enabled on all POST forms
- SQL injection protection via Django ORM
- XSS protection via Django template auto-escaping
- Sessions expire after 60 minutes of inactivity

**Before going to production, set these in environment variables:**
- `SECRET_KEY` (move out of settings.py)
- `ADMIN_REGISTRATION_KEY` (move out of settings.py)
- `DEBUG=False`
- `ALLOWED_HOSTS` (your domain only)

---

## 🔗 URL Map

| URL | Description |
|-----|-------------|
| `/` | Home — hero + featured pets |
| `/pets/` | Browse all available pets |
| `/pets/<pk>/` | Pet detail + apply |
| `/accounts/register/` | Adopter registration |
| `/accounts/admin-register/` | Admin registration (requires secret key) |
| `/accounts/login/` | Login |
| `/adoptions/apply/<pk>/` | Submit adoption application |
| `/adoptions/my-applications/` | Adopter's application history |
| `/surrender/` | Anonymous pet surrender form |
| `/dashboard/` | Admin home |
| `/dashboard/pets/` | Manage pet listings |
| `/dashboard/applications/` | Review all applications |
| `/dashboard/users/` | Manage adopter accounts |
| `/dashboard/surrenders/` | Process surrender requests |
| `/admin/` | Django admin site |

---

## 🚀 Future Enhancements

- AI-based pet recommendation
- Donation / payment integration
- Real-time chat with the shelter
- Location-based pet search
- Mobile app
- Analytics dashboard
- Wishlist / favourite pets
- Multi-language support

---

## 👨‍💻 Author

**Sujal Yadav**
- GitHub: [github.com/Sujal00005](https://github.com/Sujal00005)
- LinkedIn: [linkedin.com/in/sujal-yadav-sy00005](https://www.linkedin.com/in/sujal-yadav-sy00005)

---

## ⭐ Support

If this project helped you, drop a ⭐ on GitHub — it means a lot!

---

## 📄 License

MIT License
