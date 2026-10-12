import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Achievement, Experience, Profile, Project


class PublicSiteTests(TestCase):
    def test_home_is_open_and_lists_content(self):
        Project.objects.create(title="Zeta project", summary="Does things", tech="A, B")
        Achievement.objects.create(date=datetime.date(2026, 3, 1), title="Shipped v2")
        res = self.client.get(reverse("home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Zeta project")
        self.assertContains(res, "Shipped v2")

    def test_html_in_content_is_escaped(self):
        Project.objects.create(title="<script>alert(1)</script>", summary="x")
        res = self.client.get(reverse("home"))
        self.assertNotContains(res, "<script>alert(1)</script>")

    def test_featured_projects_come_first(self):
        Project.objects.all().delete()  # remove the starter projects added by the seed migration
        Project.objects.create(title="Plain", summary="x", sort_order=0)
        Project.objects.create(title="Star", summary="x", featured=True, sort_order=5)
        self.assertEqual(Project.objects.first().title, "Star")

    def test_project_categories_rendered(self):
        Project.objects.all().delete()
        Project.objects.create(title="API Test Suite", summary="QA project", category="qa")
        Project.objects.create(title="Cloud Microservice", summary="SWE project", category="swe")
        Project.objects.create(title="MCP Agent", summary="AI project", category="ai")
        res = self.client.get(reverse("home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'data-category="qa"')
        self.assertContains(res, 'data-category="swe"')
        self.assertContains(res, 'data-category="ai"')
        self.assertContains(res, "QA &amp; Test Automation")
        self.assertContains(res, "Software Engineering")
        self.assertContains(res, "AI &amp; Intelligent Systems")

    def test_experiences_rendered(self):
        Experience.objects.all().delete()
        Experience.objects.create(
            title="Lead QA Engineer",
            organization="Global Fintech Inc",
            period="2025 – Present",
            bullets="Architected distributed test runners\nReduced flaky test rate by 80%",
            sort_order=1,
        )
        res = self.client.get(reverse("home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Lead QA Engineer")
        self.assertContains(res, "Global Fintech Inc")
        self.assertContains(res, "2025 – Present")
        self.assertContains(res, "Architected distributed test runners")
        self.assertContains(res, "Reduced flaky test rate by 80%")

    def test_resume_link_rendering(self):
        Profile.objects.all().delete()
        res_empty = self.client.get(reverse("home"))
        self.assertEqual(res_empty.status_code, 200)
        self.assertContains(res_empty, "Request Resume")

        pdf_content = b"%PDF-1.4 test resume content"
        resume_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")
        profile = Profile.objects.create(resume=resume_file)
        res_with_resume = self.client.get(reverse("home"))
        self.assertEqual(res_with_resume.status_code, 200)
        self.assertContains(res_with_resume, "Download Resume")
        self.assertContains(res_with_resume, "Resume ⤓")
        profile.delete()


class AdminTests(TestCase):
    def test_admin_requires_login(self):
        res = self.client.get("/admin/core/project/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login/", res["Location"])

    def test_admin_crud(self):
        get_user_model().objects.create_superuser("owner", "o@example.com", "pw-for-tests-123")
        self.client.login(username="owner", password="pw-for-tests-123")
        # create
        res = self.client.post("/admin/core/project/add/", {"title": "New", "summary": "S", "sort_order": 1})
        self.assertEqual(res.status_code, 302)
        project = Project.objects.get(title="New")
        # update
        res = self.client.post(f"/admin/core/project/{project.pk}/change/", {"title": "Renamed", "summary": "S", "sort_order": 1})
        self.assertEqual(res.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.title, "Renamed")
        # delete
        res = self.client.post(f"/admin/core/project/{project.pk}/delete/", {"post": "yes"})
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_experience_admin_crud(self):
        get_user_model().objects.create_superuser("owner", "o@example.com", "pw-for-tests-123")
        self.client.login(username="owner", password="pw-for-tests-123")
        # create
        res = self.client.post("/admin/core/experience/add/", {
            "title": "Senior Engineer",
            "organization": "Acme Corp",
            "period": "2025",
            "sort_order": 1,
            "bullets": "Did things",
        })
        self.assertEqual(res.status_code, 302)
        exp = Experience.objects.get(title="Senior Engineer")
        # update
        res = self.client.post(f"/admin/core/experience/{exp.pk}/change/", {
            "title": "Principal Engineer",
            "organization": "Acme Corp",
            "period": "2025",
            "sort_order": 1,
            "bullets": "Did more things",
        })
        self.assertEqual(res.status_code, 302)
        exp.refresh_from_db()
        self.assertEqual(exp.title, "Principal Engineer")
        # delete
        res = self.client.post(f"/admin/core/experience/{exp.pk}/delete/", {"post": "yes"})
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Experience.objects.filter(pk=exp.pk).exists())

    def test_rejects_non_http_links(self):
        get_user_model().objects.create_superuser("owner", "o@example.com", "pw-for-tests-123")
        self.client.login(username="owner", password="pw-for-tests-123")
        res = self.client.post("/admin/core/project/add/", {"title": "Bad", "summary": "S", "sort_order": 0, "repo_url": "javascript:alert(1)"})
        self.assertEqual(res.status_code, 200)  # form re-rendered with an error
        self.assertFalse(Project.objects.filter(title="Bad").exists())


from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError

from .starter_data import ACHIEVEMENTS, PROJECTS

GOOD_ENV = {"ADMIN_USERNAME": "owner", "ADMIN_EMAIL": "o@example.com", "ADMIN_PASSWORD": "long-unusual-passphrase-91"}


class SeedCommandTests(TestCase):
    def run_seed(self, env=None, **kwargs):
        out = StringIO()
        with mock.patch.dict("os.environ", env or GOOD_ENV, clear=False):
            call_command("seed", stdout=out, **kwargs)
        return out.getvalue()

    def test_creates_superuser_who_can_log_in(self):
        self.run_seed()
        user = get_user_model().objects.get(username="owner")
        self.assertTrue(user.is_superuser and user.is_staff)
        self.assertTrue(self.client.login(username="owner", password=GOOD_ENV["ADMIN_PASSWORD"]))

    def test_running_twice_does_not_change_anything(self):
        self.run_seed()
        out = self.run_seed(env={**GOOD_ENV, "ADMIN_PASSWORD": "a-different-long-passphrase-55"})
        self.assertIn("already exists", out)
        self.assertEqual(get_user_model().objects.filter(username="owner").count(), 1)
        self.assertTrue(self.client.login(username="owner", password=GOOD_ENV["ADMIN_PASSWORD"]))

    def test_reset_password(self):
        self.run_seed()
        self.run_seed(env={**GOOD_ENV, "ADMIN_PASSWORD": "a-different-long-passphrase-55"}, reset_password=True)
        self.assertTrue(self.client.login(username="owner", password="a-different-long-passphrase-55"))

    def test_weak_password_is_rejected(self):
        with self.assertRaises(CommandError):
            self.run_seed(env={**GOOD_ENV, "ADMIN_PASSWORD": "12345678"})
        self.assertFalse(get_user_model().objects.filter(username="owner").exists())

    def test_missing_password_without_terminal_fails_cleanly(self):
        env = {k: v for k, v in GOOD_ENV.items() if k != "ADMIN_PASSWORD"}
        with mock.patch.dict("os.environ", env, clear=False), mock.patch.dict("os.environ", {"ADMIN_PASSWORD": ""}):
            with mock.patch("sys.stdin.isatty", return_value=False):
                with self.assertRaises(CommandError):
                    call_command("seed", stdout=StringIO())

    def test_existing_non_admin_user_is_promoted(self):
        get_user_model().objects.create_user("owner", password="whatever-long-123")
        self.run_seed()
        user = get_user_model().objects.get(username="owner")
        self.assertTrue(user.is_superuser and user.is_staff)

    def test_content_flag_only_fills_empty_tables(self):
        Project.objects.all().delete()
        self.run_seed(content=True)
        self.assertEqual(Project.objects.count(), len(PROJECTS))
        Project.objects.create(title="Mine", summary="x")
        self.run_seed(content=True)
        self.assertEqual(Project.objects.count(), len(PROJECTS) + 1)

    def test_reset_content_replaces_everything(self):
        Project.objects.create(title="Mine", summary="x")
        self.run_seed(reset_content=True)
        self.assertEqual(Project.objects.count(), len(PROJECTS))
        self.assertEqual(Achievement.objects.count(), len(ACHIEVEMENTS))
        self.assertFalse(Project.objects.filter(title="Mine").exists())


import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from .models import Profile

_MEDIA = tempfile.mkdtemp()


def image_bytes(fmt="PNG"):
    buf = BytesIO()
    Image.new("RGB", (20, 20), "red").save(buf, fmt)
    return buf.getvalue()


@override_settings(MEDIA_ROOT=_MEDIA)
class ProfileTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_MEDIA, ignore_errors=True)

    def login(self):
        get_user_model().objects.create_superuser("owner", "o@example.com", "pw-for-tests-123")
        self.client.login(username="owner", password="pw-for-tests-123")

    def test_home_has_no_photo_or_about_by_default(self):
        res = self.client.get(reverse("home"))
        self.assertNotContains(res, 'class="portrait"')
        self.assertNotContains(res, 'id="about"')

    def test_home_shows_photo_and_about_when_set(self):
        p = Profile(about="Line one\n\nLine two <b>x</b>")
        p.photo.save("me.png", ContentFile(image_bytes()))
        res = self.client.get(reverse("home"))
        self.assertContains(res, 'class="portrait"')
        self.assertContains(res, 'id="about"')
        self.assertContains(res, "Line two &lt;b&gt;x&lt;/b&gt;")  # escaped

    def test_admin_upload_works_and_file_is_served(self):
        self.login()
        up = SimpleUploadedFile("me.png", image_bytes(), "image/png")
        res = self.client.post("/admin/core/profile/add/", {"photo": up, "about": "Hello"})
        self.assertEqual(res.status_code, 302)
        profile = Profile.objects.get()
        self.assertTrue(Path(profile.photo.path).exists())
        self.assertEqual(self.client.get(profile.photo.url if profile.photo.url.startswith("/") else "/" + profile.photo.url).status_code, 200)

    def test_only_one_profile_allowed(self):
        self.login()
        Profile.objects.create(about="x")
        self.assertEqual(self.client.get("/admin/core/profile/add/").status_code, 403)

    def test_rejects_file_that_is_not_an_image(self):
        self.login()
        up = SimpleUploadedFile("me.png", b"definitely not an image", "image/png")
        res = self.client.post("/admin/core/profile/add/", {"photo": up, "about": "x"})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Profile.objects.exists())

    def test_rejects_disallowed_extension(self):
        self.login()
        up = SimpleUploadedFile("me.gif", image_bytes("GIF"), "image/gif")
        res = self.client.post("/admin/core/profile/add/", {"photo": up, "about": "x"})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Profile.objects.exists())

    def test_replacing_photo_deletes_old_file(self):
        p = Profile.objects.create(about="x")
        p.photo.save("one.png", ContentFile(image_bytes()))
        old_path = Path(p.photo.path)
        self.assertTrue(old_path.exists())
        p.photo.save("two.png", ContentFile(image_bytes()))
        self.assertFalse(old_path.exists())
        self.assertTrue(Path(p.photo.path).exists())
