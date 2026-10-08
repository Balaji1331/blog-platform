from django.core.management.base import BaseCommand

from blog.models import Post, User

USERS = [
    {
        "email": "john@example.com",
        "name": "John Doe",
        "password": "password123",
        "bio": "Full-stack developer who loves writing about the web.",
    },
    {
        "email": "jane@example.com",
        "name": "Jane Smith",
        "password": "password123",
        "bio": "Traveller, home cook and occasional blogger.",
    },
]

POSTS = [
    {
        "author": "john@example.com",
        "title": "Getting Started with Django",
        "category": "Technology",
        "tags": ["Django", "Python", "Web Dev"],
        "excerpt": "A quick tour of models, views and templates, the three pieces of every Django app.",
        "content": (
            "# Why Django?\n\nDjango ships with an ORM, an admin site, authentication and a template "
            "engine, so you can focus on your product.\n\n## The basics\n\nEvery app is built from "
            "**models**, **views** and **templates**. Run `python manage.py runserver` to see it live.\n\n"
            "```\nfrom django.db import models\n\nclass Post(models.Model):\n    title = "
            "models.CharField(max_length=200)\n```"
        ),
    },
    {
        "author": "john@example.com",
        "title": "Building a Habit of Writing Every Day",
        "category": "Lifestyle",
        "tags": ["Writing", "Habits"],
        "excerpt": "Small, consistent sessions beat occasional marathons. Here is what worked for me.",
        "content": (
            "Start with **ten minutes** a day. Do not edit while you draft, and keep a running list "
            "of ideas.\n\nAfter a month the habit sticks and the ideas start to flow."
        ),
    },
    {
        "author": "jane@example.com",
        "title": "A Weekend in the Mountains",
        "category": "Travel",
        "tags": ["Hiking", "Outdoors"],
        "excerpt": "Two days, one backpack and a trail with a view that made the climb worth it.",
        "content": (
            "# Day one\n\nWe started early and reached the ridge by noon.\n\n# Day two\n\n"
            "A slow breakfast, a short walk down and a long drive home."
        ),
    },
    {
        "author": "jane@example.com",
        "title": "One-Pot Pasta for Busy Weeknights",
        "category": "Food",
        "tags": ["Recipe", "Quick Meals"],
        "excerpt": "Dinner in twenty minutes with one pot to wash.",
        "content": (
            "Combine pasta, stock, garlic and tomatoes in one pot and simmer until the liquid is "
            "absorbed.\n\nFinish with **basil** and plenty of parmesan."
        ),
    },
    {
        "author": "john@example.com",
        "title": "Five Habits of Productive Teams",
        "category": "Business",
        "tags": ["Teamwork", "Productivity"],
        "excerpt": "Clear goals, short meetings and honest retros go a long way.",
        "content": (
            "## 1. Clear goals\n\nEveryone knows what done looks like.\n\n## 2. Short meetings\n\n"
            "If it can be an email, make it an email."
        ),
    },
    {
        "author": "jane@example.com",
        "title": "Why Sleep Matters More Than You Think",
        "category": "Health",
        "tags": ["Sleep", "Wellness"],
        "excerpt": "Consistent sleep improves focus, mood and recovery.",
        "content": (
            "Aim for a consistent schedule, dim the lights an hour before bed and keep screens out "
            "of the bedroom."
        ),
    },
]


class Command(BaseCommand):
    help = "Create demo users and posts (safe to run repeatedly). Use --reset to wipe posts first."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete all posts before seeding.")

    def handle(self, *args, **options):
        if options["reset"]:
            Post.objects.all().delete()

        users = {}
        for data in USERS:
            user = User.objects.find_by_email(data["email"])
            if user is None:
                user = User.objects.create_user(
                    email=data["email"], name=data["name"], password=data["password"], bio=data["bio"]
                )
            users[data["email"]] = user

        for data in POSTS:
            content = data["content"]
            Post.objects.get_or_create(
                title=data["title"],
                author=users[data["author"]],
                defaults={
                    "content": content,
                    "excerpt": data["excerpt"],
                    "category": data["category"],
                    "tags": data["tags"],
                    "readTime": max(1, len(content.split()) // 200),
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed data ready. Log in with john@example.com / password123"))
