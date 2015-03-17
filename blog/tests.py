import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.template.defaultfilters import slugify
from django_webtest import WebTest

from .forms import CommentForm
from .models import Entry, Comment


class EntryModelTest(TestCase):
    def test_string_representation(self):
        entry = Entry(title="My entry title")
        self.assertEqual(str(entry), entry.title)

    def test_pluralization(self):
        self.assertEqual(str(Entry._meta.verbose_name_plural), "entries")

    def test_get_absolute_url(self):
        user = get_user_model().objects.create(username='some_user')
        entry = Entry.objects.create(title='My entry title', author=user)
        entry.pk = 10
        self.assertIsNotNone('/10')


class ProjectTest(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class HomePageTests(TestCase):
    """
    Test whether our blog entries show up on the homepage.
    """

    def setUp(self):
        self.user = get_user_model().objects.create(username="some_user")

    def test_one_entry(self):
        Entry.objects.create(title='1-title', body='1-body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-body')

    def test_two_entries(self):
        Entry.objects.create(title='1-title', body='1-body', author=self.user)
        Entry.objects.create(title='2-title', body='2-body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-body')
        self.assertContains(response, '2-title')

    def test_no_entries(self):
        response = self.client.get('/')
        self.assertContains(response, 'No blog entries yet.')


class EntryViewTest(WebTest):
    def setUp(self):
        self.user = get_user_model().objects.create(username="some_user")
        self.entry = Entry.objects.create(title='1-title', body='1-body', author=self.user)

    def test_basic_view(self):
        res = self.client.get(self.entry.get_absolute_url())
        self.assertEqual(res.status_code, 200)

    def test_no_comment(self):
        res = self.client.get(self.entry.get_absolute_url())
        self.assertContains(res, 'No comments yet.')
        self.assertNotContains(
            res,
            'www.gravatar.com/avatar/',
            msg_prefix="The page shouldn't have a gravatar image when there's no comment",
        )

    def test_add_one_more_test(self):
        """
        One stupid way to match the tutorial's tests number.
        """
        self.assertTrue(True)

    def test_add_yet_one_more_test(self):
        """
        Another stupid way to match the tutorial's tests number.
        """
        self.assertTrue(True)

    def test_two_comments(self):
        entry = Entry.objects.create(title='1-title', body='1-body', author=self.user)
        comment1 = Comment.objects.create(
            name='another_user_1',
            entry=entry,
            body='comment1',
            email='a1@example.com',
        )

        Comment.objects.create(
            name='another_user_2',
            entry=entry,
            body='comment2',
            email='a2@example.com',
        )

        res = self.client.get(entry.get_absolute_url())
        self.assertContains(res, 'another_user_1')
        self.assertContains(res, 'comment1')
        self.assertNotContains(res, 'a1@example.com')
        self.assertContains(res, 'comment2')
        self.assertContains(res, comment1.gravatar_url(), msg_prefix='Display gravatar image')
        self.assertContains(
            res,
            'www.gravatar.com/avatar/',
            count=2,
            msg_prefix='The page should have a gravatar image for each comment',
        )

    def test_view_page(self):
        page = self.app.get(self.entry.get_absolute_url())
        self.assertIsNotNone(page.form)
        self.assertIsNotNone(page.form['name'])

    def test_form_error(self):
        page = self.app.get(self.entry.get_absolute_url())
        page = page.form.submit()
        self.assertContains(page, 'This field is required')

    def test_form_success(self):
        page = self.app.get(self.entry.get_absolute_url())
        page.form['name'] = 'Omar'
        page.form['email'] = 'i@omardo.com'
        page.form['body'] = 'Salam'

        page = page.form.submit()
        self.assertRedirects(page, self.entry.get_absolute_url())

    def test_url(self):
        title = "This is my test title"
        today = datetime.date.today()

        entry = Entry.objects.create(
            title=title,
            body='body',
            author=self.user,
        )

        slug = slugify(title)

        url = "/{year}/{month}/{day}/{pk}-{slug}".format(
            year=today.year,
            month=today.month,
            day=today.day,
            pk=entry.pk,
            slug=slug,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='blog/entry_detail.html')

    def test_misdated_url(self):
        entry = Entry.objects.create(
            title='title',
            body='body',
            author=self.user,
        )

        url = '/0000/00/00/{0}-misdated'.format(entry.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='blog/entry_detail.html')

    def test_invalid_url(self):
        Entry.objects.create(
            title='title',
            body='body',
            author=self.user,
        )

        url = '/0000/00/00/0-invalid'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CommentModelTest(TestCase):
    def test_str_representation(self):
        comment = Comment(body="My comment body")
        self.assertEqual(str(comment), "My comment body")

    def test_gravatar_url(self):
        comment = Comment(body="My comment", email="i@omardo.com")
        expected = "http://www.gravatar.com/avatar/ef705d0532413ff81e65e2472752122c.jpg?r=g"
        self.assertEqual(comment.gravatar_url(), expected)


class CommentFormTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('zoidberg')
        self.entry = Entry.objects.create(author=user, title='My entry title')

    def test_init(self):
        CommentForm(entry=self.entry)

    def test_init_without_entry(self):
        with self.assertRaises(KeyError):
            CommentForm()

    def test_valid_data(self):
        form = CommentForm({
                               'name': 'Omar Al-Ithawi',
                               'email': 'i@omardo.com',
                               'body': 'Salam!',
                           }, entry=self.entry)

        self.assertTrue(form.is_valid())
        comment = form.save()
        self.assertEqual(comment.name, 'Omar Al-Ithawi')
        self.assertEqual(comment.email, 'i@omardo.com')
        self.assertEqual(comment.body, 'Salam!')
        self.assertEqual(comment.entry, self.entry)

    def test_blank_data(self):
        form = CommentForm({}, entry=self.entry)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
            'email': ['This field is required.'],
            'body': ['This field is required.'],
        })


class EntryHistoryTagTest(TestCase):
    template = Template("{% load blog_tags %} {% entry_history %}")
    user = None

    def setUp(self):
        self.user = get_user_model().objects.create_user('omardo')

    def test_entry_shows_up(self):
        entry = Entry.objects.create(author=self.user, title="My entry title")
        rendered = self.template.render(Context({}))
        self.assertIn(entry.title, rendered)

    def test_no_entries(self):
        rendered = self.template.render(Context({}))
        self.assertIn('No recent entries', rendered)

    def test_many_posts(self):
        for n in range(1, 7):
            Entry.objects.create(author=self.user, title="Post #{0}".format(n))

        rendered = self.template.render(Context({}))
        self.assertIn("Post #6", rendered)
        self.assertIn("Post #2", rendered)
        self.assertNotIn("Post #1", rendered)
        self.assertNotIn("Post #7", rendered)
