# Portfolio (Django)

A personal portfolio site where the public pages are open to everyone, and you manage everything from Django's built-in admin at `/admin/`.

**What you can manage from the admin (full create, edit and delete):**
- **Projects:** title, summary, technologies, code link, live demo link, featured flag and display order.
- **Profile:** your professional photo and the About text. There is only one Profile entry. The photo appears at the top of the page and the text in an About section (the section stays hidden until you write something).
- **Achievements:** dated progress entries with an optional description and link. They appear in the "Achievements and progress" timeline, newest first.

Only you can log in. Visitors only see the public page.

## Run it

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
python manage.py migrate         # creates the database with starter content
python manage.py seed            # creates your admin login (asks for a password)
python manage.py runserver
```

- Site: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin/

The starter projects and achievements come from your CV (the data is in `core/starter_data.py`). Edit or delete them in the admin.

## Your photo

1. Log in at `/admin/` and open **Profile**, then **Add**.
2. Choose your photo (JPG, PNG or WebP, up to 5 MB; a square crop of your face works best) and write your About text.
3. Save. To change it later, open the same Profile entry and upload a new photo. The old file is removed automatically.

Uploads are checked: the file must really be an image, and other types (including SVG) are rejected. Files are stored in the `media/` folder.

## The seed command

`python manage.py seed` creates your admin account. It is safe to run repeatedly.

- It reads `ADMIN_USERNAME`, `ADMIN_EMAIL` and `ADMIN_PASSWORD` from `.env`. If `ADMIN_PASSWORD` is empty it asks for the password in the terminal, which is safer. Remove the password from `.env` after seeding.
- If the admin already exists it changes nothing, so it can't overwrite your password by accident.
- The password must pass Django's checks (length, not too common, not all numbers).

| Command | What it does |
|---|---|
| `python manage.py seed` | Create the admin if it doesn't exist |
| `python manage.py seed --reset-password` | Set a new password for the admin |
| `python manage.py seed --username me --email me@example.com` | Use a different username or email |
| `python manage.py seed --content` | Add starter projects and achievements, only to tables that are empty |
| `python manage.py seed --reset-content` | Delete ALL projects and achievements and reload the starter content |

On a host without a terminal, set `ADMIN_PASSWORD` as an environment variable and run `python manage.py seed` once, then remove the variable.

## Animations

All effects live in `core/static/core/main.js` and the bottom half of `core/static/core/style.css`:
- A hero test run that types its command, ticks each line, and retries one flaky test.
- Content that fades in as you scroll, a scroll progress bar, a sticky nav that highlights the current section, and hover effects on cards and buttons.
- A light/dark toggle that remembers the visitor's choice.

Visitors who prefer reduced motion see the finished page with no animation, and the page still works with JavaScript off.

## Tests

```bash
python manage.py test
```

They cover the public page, escaping of HTML in content, project ordering, admin login protection, admin create/update/delete, and rejection of non-http links.

## Make it yours

- Hero text, experience, skills and contact links are in `core/templates/core/home.html`.
- Colors and fonts are in `core/static/core/style.css`.
- Models are in `core/models.py`. After changing them run `python manage.py makemigrations` and `migrate`.

## Before you deploy

1. In `.env` set `DEBUG=0`, a long random `SECRET_KEY`, `ALLOWED_HOSTS` (your domain) and `CSRF_TRUSTED_ORIGINS` (for example `https://yourname.com`).
2. Run `python manage.py collectstatic --noinput` (WhiteNoise serves the files).
3. Serve with a production server, for example `pip install gunicorn` then `gunicorn config.wsgi`.
4. Use a host with a persistent disk (Render, Railway, a VPS), because data lives in `db.sqlite3` and your photo lives in `media/`. Back up both. Without a persistent disk the photo disappears on every redeploy. For a host without a disk, switch `DATABASES` in `config/settings.py` to PostgreSQL.
5. Use a strong superuser password and HTTPS.
