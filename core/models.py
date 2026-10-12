from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models


def validate_image_size(f):
    if f.size > 5 * 1024 * 1024:
        raise ValidationError("Image must be 5 MB or smaller.")


def validate_pdf_size(f):
    if f.size > 10 * 1024 * 1024:
        raise ValidationError("Resume PDF must be 10 MB or smaller.")


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("qa", "QA & Test Automation"),
        ("swe", "Software Engineering"),
        ("ai", "AI & Intelligent Systems"),
    ]

    title = models.CharField(max_length=120)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default="qa",
        blank=True,
        help_text="Domain category for filtering."
    )
    summary = models.TextField(validators=[MaxLengthValidator(600)], help_text="Up to 600 characters.")
    tech = models.CharField("technologies", max_length=200, blank=True, help_text="Comma separated, e.g. Playwright, Allure")
    repo_url = models.URLField("code link", max_length=300, blank=True)
    live_url = models.URLField("live demo link", max_length=300, blank=True)
    featured = models.BooleanField(default=False, help_text="Featured projects show first.")
    sort_order = models.IntegerField(default=0, help_text="Lower numbers show first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "sort_order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = "qa"
        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech.split(",") if t.strip()]


class Achievement(models.Model):
    date = models.DateField()
    year_only = models.BooleanField(default=False, help_text="Tick this if you only know the year.")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True, validators=[MaxLengthValidator(500)], help_text="Optional, up to 500 characters.")
    link = models.URLField(max_length=300, blank=True, help_text="Optional link to a certificate, post or repo.")

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.title


class Profile(models.Model):
    """Single entry holding your photo, resume and About text. Only one can exist."""
    photo = models.ImageField(
        upload_to="profile/", blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size],
        help_text="JPG, PNG or WebP, up to 5 MB. A square photo of your face works best.",
    )
    resume = models.FileField(
        upload_to="resume/", blank=True,
        validators=[FileExtensionValidator(["pdf"]), validate_pdf_size],
        help_text="PDF document up to 10 MB. Recruiters will be able to download this from the hero and navigation.",
    )
    about = models.TextField(blank=True, validators=[MaxLengthValidator(1500)], help_text="Shown in the About section. Up to 1500 characters. Leave empty to hide the section.")

    def __str__(self):
        return "Profile"

    def save(self, *args, **kwargs):
        old = Profile.objects.filter(pk=self.pk).first() if self.pk else None
        old_photo = old.photo.name if old and old.photo else ""
        old_resume = old.resume.name if old and old.resume else ""
        super().save(*args, **kwargs)
        if old_photo and old_photo != self.photo.name:
            self.photo.storage.delete(old_photo)  # remove the replaced photo from disk
        if old_resume and old_resume != self.resume.name:
            self.resume.storage.delete(old_resume)  # remove the replaced resume from disk

    def delete(self, *args, **kwargs):
        photo_name = self.photo.name if self.photo else ""
        resume_name = self.resume.name if self.resume else ""
        super().delete(*args, **kwargs)
        if photo_name:
            self.photo.storage.delete(photo_name)
        if resume_name:
            self.resume.storage.delete(resume_name)


class Experience(models.Model):
    title = models.CharField(max_length=140, help_text="e.g. QA & Test Automation Engineer or BSc Electrical Engineering")
    organization = models.CharField(max_length=160, blank=True, help_text="Company, organisation or university.")
    period = models.CharField(max_length=80, blank=True, help_text="e.g. 2024 – Present or 2021 – 2024")
    description = models.TextField(blank=True, help_text="Optional summary or degree details.")
    bullets = models.TextField(blank=True, help_text="One achievement per line. Rendered as bullet points.")
    sort_order = models.IntegerField(default=0, help_text="Lower numbers show first.")

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.title} ({self.period})" if self.period else self.title

    @property
    def bullet_list(self):
        return [b.strip() for b in self.bullets.splitlines() if b.strip()]
