# 🐾 Paws & Hearts — Pet Adoption Portal

## 🌐 Live Website
**Production URL:** https://pet-adoption-and-management-74e2.onrender.com

---

## 📋 Project Overview

A modern, full-featured pet adoption and management portal built with Django, featuring:

- **Public Portal:** Browse available pets, submit adoption applications
- **Admin Dashboard:** Manage pets, applications, users, and surrenders
- **Modern UI:** Beautiful, responsive design with warm orange color scheme
- **Full CRUD:** Complete pet and application management
- **Image Upload:** Support for multiple pet photos
- **Email Notifications:** Automated emails for key actions
- **Mobile Responsive:** Works perfectly on all devices

---

## 🚀 Technology Stack

- **Backend:** Django 4.2
- **Database:** PostgreSQL (Neon)
- **Hosting:** Render
- **Storage:** Render Static Files + Media
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Fonts:** Google Fonts (Nunito, Inter)

---

## ✨ Key Features

### For Adopters:
- Browse available pets with advanced filters
- View detailed pet profiles with photo galleries
- Submit adoption applications
- Track application status
- Surrender pets that need rehoming

### For Admins:
- Dashboard with key statistics
- Manage pet listings (CRUD operations)
- Review and approve/reject applications
- Manage user accounts
- Process surrender requests
- Track adoption metrics

---

## 📁 Project Structure

```
Pet-Adoption-And-Management/
├── accounts/           # User authentication & profiles
├── adoptions/          # Adoption applications
├── pets/              # Pet listings
├── dashboard/         # Admin dashboard
├── surrenders/        # Pet surrender requests
├── notifications/     # Email notifications
├── static/           # CSS, JS, images
├── templates/        # HTML templates
├── media/           # Uploaded pet photos
└── pet_adoption/    # Main project settings
```

---

## 🔧 Local Development

### Prerequisites:
- Python 3.8+
- PostgreSQL (or SQLite for dev)
- pip

### Setup:

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd Pet-Adoption-And-Management
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## 🌐 Deployment to Render

### Database Setup (Neon):
1. Create Neon account at [neon.tech](https://neon.tech)
2. Create new project and database
3. Copy connection string (looks like: `postgresql://user:pass@host/dbname`)

### Web Service Setup (Render):
1. Create Render account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new Web Service
4. Configure:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn pet_adoption.wsgi:application`
   - **Environment:** Python 3

### Environment Variables on Render:
Add these in Render dashboard:
```
SECRET_KEY=<generate-random-secret>
DEBUG=False
DATABASE_URL=<your-neon-connection-string>
ALLOWED_HOSTS=pet-adoption-and-management-74e2.onrender.com
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
```

### Deploy:
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

Render will automatically build and deploy!

---

## 🔐 Security Checklist

- [x] HTTPS enabled (Render provides)
- [x] CSRF protection enabled
- [x] SQL injection protection (Django ORM)
- [x] XSS protection (Django templates)
- [x] Secure cookies in production
- [x] Rate limiting on login
- [x] Environment variables for secrets
- [ ] reCAPTCHA on public forms (optional)

---

## 📊 Monitoring

### Check Logs:
- **Render:** Dashboard → Your Service → Logs
- **Neon:** Dashboard → Your Project → Metrics

### Performance:
- Page load time should be < 3 seconds
- Database queries optimized with select_related
- Static files served via WhiteNoise

---

## 🛠️ Maintenance

### Database Backups:
Neon provides automatic daily backups. You can also:
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Update Dependencies:
```bash
pip list --outdated
pip install --upgrade <package-name>
pip freeze > requirements.txt
```

### Clear Cache:
```bash
python manage.py clearsessions
```

---

## 📱 Testing

### Manual Testing:
- [ ] User registration works
- [ ] User login works
- [ ] Pet browsing works
- [ ] Filters work correctly
- [ ] Application submission works
- [ ] Admin dashboard accessible
- [ ] Pet CRUD operations work
- [ ] Email notifications send
- [ ] Mobile responsive
- [ ] Forms validate correctly

### Browser Testing:
- [ ] Chrome (Desktop & Mobile)
- [ ] Firefox
- [ ] Safari (Desktop & Mobile)
- [ ] Edge

---

## 🐛 Troubleshooting

### Common Issues:

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Database connection error:**
- Check DATABASE_URL is correct
- Verify Neon database is active

**500 errors in production:**
- Check Render logs
- Verify all environment variables set
- Check DEBUG=False in production

**Email not sending:**
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Use Gmail App Password (not regular password)

---

## 📞 Support

For issues or questions:
1. Check logs on Render dashboard
2. Check database status on Neon
3. Review Django error messages
4. Check this README for common solutions

---

## 📝 License

This project is for educational purposes.

---

## 🎉 Credits

- **Framework:** Django
- **Hosting:** Render
- **Database:** Neon (PostgreSQL)
- **Fonts:** Google Fonts
- **Icons:** Unicode Emoji

---

**Made with ❤️ for rescuing pets and finding them loving homes** 🐾
