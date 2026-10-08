from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Post, User
from .templatetags.blog_extras import render_post


class BlogTestBase(TestCase):
    def setUp(self):
        call_command("seed_data", verbosity=0)
        self.john = User.objects.get(email="john@example.com")
        self.jane = User.objects.get(email="jane@example.com")

    def login_john(self):
        self.client.login(username="john@example.com", password="password123")


class AuthTests(BlogTestBase):
    def test_login_with_email_and_password(self):
        response = self.client.post(
            reverse("login"), {"username": "john@example.com", "password": "password123"}
        )
        self.assertRedirects(response, reverse("home"))

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("login"), {"username": "john@example.com", "password": "nope"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials")

    def test_passwords_are_hashed(self):
        self.assertNotEqual(self.john.password, "password123")
        self.assertTrue(self.john.check_password("password123"))

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New Writer",
                "email": "new@example.com",
                "bio": "",
                "password1": "a-Strong-passw0rd!",
                "password2": "a-Strong-passw0rd!",
            },
        )
        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("a-Strong-passw0rd!"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "Dup",
                "email": "john@example.com",
                "password1": "a-Strong-passw0rd!",
                "password2": "a-Strong-passw0rd!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")


class PostViewTests(BlogTestBase):
    def test_home_lists_published_posts(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Getting Started with Django")

    def test_post_detail_is_public(self):
        post = Post.objects.get(title="Getting Started with Django")
        response = self.client.get(reverse("post_detail", args=[post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.author.name)

    def test_create_requires_login(self):
        response = self.client.get(reverse("post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_create_post_saves_expected_values(self):
        self.login_john()
        data = {
            "title": "Test Blog Post",
            "content": "This is a test blog post content with some sample text.",
            "excerpt": "This is a test excerpt",
            "category": "Technology",
            "tags_input": "test, blog , sample",
        }
        response = self.client.post(reverse("post_create"), data)
        self.assertRedirects(response, reverse("my_posts"))

        post = Post.objects.get(title="Test Blog Post")
        self.assertEqual(post.author, self.john)
        self.assertEqual(post.excerpt, "This is a test excerpt")
        self.assertEqual(post.category, "Technology")
        self.assertEqual(post.tags, ["test", "blog", "sample"])
        self.assertEqual(post.readTime, 1)
        self.assertTrue(post.published)

        listing = self.client.get(reverse("my_posts"))
        self.assertContains(listing, "Test Blog Post")

    def test_blank_excerpt_is_generated_from_content(self):
        self.login_john()
        content = "word " * 100
        self.client.post(
            reverse("post_create"),
            {"title": "Auto excerpt", "content": content, "excerpt": "", "category": "Travel"},
        )
        post = Post.objects.get(title="Auto excerpt")
        self.assertEqual(post.excerpt, content[:150])

    def test_author_can_edit_own_post(self):
        self.login_john()
        post = Post.objects.filter(author=self.john).first()
        response = self.client.post(
            reverse("post_edit", args=[post.pk]),
            {"title": "Edited title", "content": "New body", "excerpt": "", "category": "Health"},
        )
        self.assertRedirects(response, reverse("my_posts"))
        post.refresh_from_db()
        self.assertEqual(post.title, "Edited title")
        self.assertEqual(post.category, "Health")

    def test_user_cannot_edit_or_delete_someone_elses_post(self):
        self.login_john()
        post = Post.objects.filter(author=self.jane).first()
        edit = self.client.post(
            reverse("post_edit", args=[post.pk]),
            {"title": "Hacked", "content": "x", "excerpt": "", "category": "Food"},
        )
        self.assertRedirects(edit, reverse("post_detail", args=[post.pk]))
        self.client.post(reverse("post_delete", args=[post.pk]))
        post.refresh_from_db()
        self.assertNotEqual(post.title, "Hacked")
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())

    def test_author_can_delete_own_post(self):
        self.login_john()
        post = Post.objects.filter(author=self.john).first()
        response = self.client.post(reverse("post_delete", args=[post.pk]))
        self.assertRedirects(response, reverse("my_posts"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_delete_rejects_get(self):
        self.login_john()
        post = Post.objects.filter(author=self.john).first()
        response = self.client.get(reverse("post_delete", args=[post.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())

    def test_my_posts_only_shows_own_posts(self):
        self.login_john()
        response = self.client.get(reverse("my_posts"))
        titles = [p.title for p in response.context["posts"]]
        self.assertTrue(titles)
        self.assertTrue(all(Post.objects.get(title=t).author == self.john for t in titles))


class RenderPostTests(TestCase):
    def test_html_is_escaped(self):
        html = render_post("<script>alert(1)</script>")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_basic_markup(self):
        html = render_post("# Title\n\nSome **bold** and `code`.")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<code>code</code>", html)

    def test_fenced_code_block(self):
        html = render_post("```\nx = 1 < 2\n```")
        self.assertIn("<pre><code>x = 1 &lt; 2</code></pre>", html)

    def test_paragraph_starting_with_inline_code_is_wrapped(self):
        html = render_post("`x` is a variable")
        self.assertTrue(html.startswith("<p><code>x</code>"))
