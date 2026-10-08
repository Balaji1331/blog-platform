# BlogPlatform (Django)

A blogging platform rebuilt as a server-rendered **Django** app with **HTML, CSS, JavaScript and Bootstrap 5**.
Write, edit, delete and browse posts; filter by category and search live; sign in with email and password.

## Quick start

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data          # demo users + sample posts (optional)
```

### Run on port 8000 **and** 8080

Easiest, one terminal:

```bash
python run_servers.py               # http://127.0.0.1:8000  and  http://127.0.0.1:8080
python run_servers.py --host 0.0.0.0  # also reachable from other devices on your network
```

Or two terminals:

```bash
python manage.py runserver 8000
python manage.py runserver 0.0.0.0:8080
```

Open <http://localhost:8000> or <http://localhost:8080>.

### Demo login (after `seed_data`)

| Email | Password |
|---|---|
| john@example.com | password123 |
| jane@example.com | password123 |

You can also register a new account at `/register/`. Create an admin with `python manage.py createsuperuser`, then visit `/admin/`.

### Tests

```bash
python manage.py test
```

## Project layout

```
blog_platform/
├── manage.py
├── run_servers.py              # starts 8000 + 8080 together
├── requirements.txt
├── blog_backend/               # settings, urls, wsgi/asgi
└── blog/
    ├── models.py               # User (email login), Post
    ├── forms.py                # login, register, post forms
    ├── views.py                # home, detail, my posts, create, edit, delete, register
    ├── urls.py
    ├── admin.py
    ├── tests.py
    ├── migrations/0001_initial.py
    ├── management/commands/seed_data.py
    ├── templatetags/blog_extras.py   # safe post-content renderer
    ├── templates/blog/         # base, navbar, home, post_detail, my_posts, post_form, login, register
    └── static/blog/            # css/style.css, js/main.js
```

## Pages

| URL | What it does | Login needed |
|---|---|---|
| `/` | All posts, live search + category filter | No |
| `/post/<id>/` | Post detail; edit/delete shown to the author | No |
| `/my-posts/` | Your posts with edit and delete | Yes |
| `/create/` | New post | Yes |
| `/edit/<id>/` | Edit your own post | Yes |
| `/login/`, `/register/`, `/logout/` | Authentication | – |

## What changed from the React + REST version

- **React/Tailwind frontend replaced** by Django templates, Bootstrap 5, `static/blog/css/style.css` (same dark/purple look) and `static/blog/js/main.js` (live filter, delete confirmation, char counter, toasts).
- **REST API, JWT and CORS removed.** Django now renders pages directly, so DRF, simplejwt and django-cors-headers are no longer needed.
- **Security fixes:** passwords are now hashed (they were stored and compared as plain text); login uses Django sessions + CSRF instead of trusting a client-supplied `x-user-id` header, which let anyone impersonate any user; post content is HTML-escaped before formatting (the old renderer allowed script injection).
- **Bug fixes:** the old `create_post` never read the request body and returned an unserialisable object; `pytest.ini`, `manage..py` and `requirementst.txt` had typos in their names or headers.
- **Added:** registration page, `seed_data` command (the old tests called it but it did not exist), admin for the custom user.

## Notes

- Bootstrap and Bootstrap Icons load from the jsDelivr CDN, so the pages need internet access the first time they load.
- Data lives in `db.sqlite3` (created by `migrate`). Delete the file to start fresh.
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS` environment variables override the dev defaults; set them before deploying anywhere public.
