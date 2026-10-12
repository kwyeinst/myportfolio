from django.conf import settings
from django.shortcuts import render
from django.views.static import serve

from .models import Achievement, Experience, Profile, Project


def home(request):
    return render(request, "core/home.html", {
        "profile": Profile.objects.first(),
        "projects": Project.objects.all(),
        "achievements": Achievement.objects.all(),
        "experiences": Experience.objects.all(),
    })


def media(request, path):
    """Serve uploaded files (your photo). Fine for a small single-server portfolio; see the README before scaling up."""
    return serve(request, path, document_root=settings.MEDIA_ROOT)
