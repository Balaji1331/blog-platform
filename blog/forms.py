from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import Post, User


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that asks for an email address instead of a username."""

    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Invalid credentials. Check your email and password.",
    }


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        help_text="At least 8 characters; avoid common or all-numeric passwords.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["name", "email", "bio"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "bio": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "A short bio (optional)"}
            ),
        }

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The two password fields didn't match.")
        elif p1:
            candidate = User(name=cleaned.get("name", ""), email=cleaned.get("email", ""))
            try:
                password_validation.validate_password(p1, candidate)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        label="Tags",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Tag names"}
        ),
    )

    class Meta:
        model = Post
        fields = ["title", "category", "excerpt", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter an engaging title..."}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief description of your post (optional)",
                    "data-char-counter": "excerptCount",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control font-monospace",
                    "rows": 18,
                    "placeholder": "Write your post content here...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Drop the "---------" placeholder option; default to the first category.
        self.fields["category"].choices = Post.CATEGORY_CHOICES
        if not self.instance.pk:
            self.fields["category"].initial = Post.CATEGORY_CHOICES[0][0]
        else:
            self.fields["tags_input"].initial = ", ".join(self.instance.tags or [])

    def save(self, commit=True):
        post = super().save(commit=False)
        content = self.cleaned_data["content"]
        if not post.excerpt:
            post.excerpt = content[:150]
        post.tags = [t.strip() for t in self.cleaned_data.get("tags_input", "").split(",") if t.strip()]
        post.readTime = max(1, len(content.split()) // 200)  # ~200 words per minute
        if commit:
            post.save()
        return post
