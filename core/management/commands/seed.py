import getpass
import os
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Achievement, Experience, Project
from core.starter_data import ACHIEVEMENTS, EXPERIENCES, PROJECTS


class Command(BaseCommand):
    help = (
        "Create the admin account (safe to run repeatedly) and optionally load the starter content. "
        "Reads ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD from the environment or .env, "
        "and asks for the password if it is not set."
    )

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Admin username (default: ADMIN_USERNAME or 'admin')")
        parser.add_argument("--email", help="Admin email (default: ADMIN_EMAIL)")
        parser.add_argument("--reset-password", action="store_true", help="Set a new password on an existing admin account")
        parser.add_argument("--content", action="store_true", help="Load starter projects and achievements into any empty table")
        parser.add_argument("--reset-content", action="store_true", help="DELETE all projects and achievements, then reload the starter content")

    def handle(self, *args, **opts):
        self.seed_admin(opts)
        if opts["reset_content"] or opts["content"]:
            self.seed_content(reset=opts["reset_content"])
        self.stdout.write(self.style.SUCCESS("Done. Log in at /admin/"))

    # ---- admin account ----
    def seed_admin(self, opts):
        User = get_user_model()
        username = opts["username"] or os.environ.get("ADMIN_USERNAME") or "admin"
        email = opts["email"] or os.environ.get("ADMIN_EMAIL") or ""
        user = User.objects.filter(username=username).first()

        if user and not opts["reset_password"]:
            changed = []
            if not user.is_staff:
                user.is_staff = True
                changed.append("is_staff")
            if not user.is_superuser:
                user.is_superuser = True
                changed.append("is_superuser")
            if not user.is_active:
                user.is_active = True
                changed.append("is_active")
            if changed:
                user.save(update_fields=changed)
                self.stdout.write(f"Admin '{username}' already existed; fixed: {', '.join(changed)}.")
            else:
                self.stdout.write(f"Admin '{username}' already exists. Use --reset-password to change the password.")
            return

        password = os.environ.get("ADMIN_PASSWORD") or self.ask_password()
        try:
            validate_password(password, user=User(username=username, email=email))
        except ValidationError as err:
            raise CommandError("Password rejected: " + " ".join(err.messages))

        if user:
            user.set_password(password)
            user.is_staff = user.is_superuser = user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password updated for '{username}'."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created admin '{username}'."))

    def ask_password(self):
        if not sys.stdin.isatty():
            raise CommandError("No password given. Set ADMIN_PASSWORD in .env (or the environment), or run this in a terminal.")
        first = getpass.getpass("Admin password: ")
        if first != getpass.getpass("Repeat password: "):
            raise CommandError("Passwords did not match.")
        return first

    # ---- starter content ----
    @transaction.atomic
    def seed_content(self, reset):
        if reset:
            Project.objects.all().delete()
            Achievement.objects.all().delete()
            Experience.objects.all().delete()
        added_p = added_a = added_e = 0
        if not Project.objects.exists():
            Project.objects.bulk_create([Project(**p) for p in PROJECTS])
            added_p = len(PROJECTS)
        if not Achievement.objects.exists():
            Achievement.objects.bulk_create([Achievement(**a) for a in ACHIEVEMENTS])
            added_a = len(ACHIEVEMENTS)
        if not Experience.objects.exists():
            Experience.objects.bulk_create([Experience(**e) for e in EXPERIENCES])
            added_e = len(EXPERIENCES)
        self.stdout.write(f"Starter content: {added_p} projects, {added_a} achievements and {added_e} experiences added.")
