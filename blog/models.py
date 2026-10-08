from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, bio=""):
        if not email:
            raise ValueError("The Email field must be set.")
        if not name:
            raise ValueError("The Name field must be set.")
        if not password:
            raise ValueError("The Password field must be set.")

        user = self.model(email=self.normalize_email(email), name=name, bio=bio)
        user.set_password(password)  # hashed, never stored in plain text
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, bio=""):
        user = self.create_user(email, name, password, bio)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def find_by_email(self, email):
        try:
            return self.get(email=email)
        except self.model.DoesNotExist:
            return None


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(default="", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    @property
    def initial(self):
        return self.name[:1].upper() if self.name else "?"


class Post(models.Model):
    CATEGORY_CHOICES = [
        ("Technology", "Technology"),
        ("Lifestyle", "Lifestyle"),
        ("Travel", "Travel"),
        ("Food", "Food"),
        ("Business", "Business"),
        ("Health", "Health"),
        ("Education", "Education"),
        ("Entertainment", "Entertainment"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.CharField(max_length=500, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tags = models.JSONField(default=list, blank=True)
    readTime = models.IntegerField(default=5)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def findAll(cls):
        return cls.objects.filter(published=True).select_related("author").order_by("-created_at")

    @classmethod
    def findByAuthor(cls, author_id):
        return cls.objects.filter(author_id=author_id).select_related("author").order_by("-created_at")

    @classmethod
    def findByCategory(cls, category):
        return (
            cls.objects.filter(category=category, published=True)
            .select_related("author")
            .order_by("-created_at")
        )

    @property
    def was_updated(self):
        """True when the post was edited noticeably after it was created."""
        return (self.updated_at - self.created_at).total_seconds() > 60
