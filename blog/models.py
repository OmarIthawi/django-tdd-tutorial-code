from hashlib import md5

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


class Entry(models.Model):
    title = models.CharField(max_length=500)
    author = models.ForeignKey('auth.user')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    slug = models.SlugField(default='', editable=False)

    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={
            'year': self.created_at.year,
            'month': self.created_at.month,
            'day': self.created_at.day,
            'slug': self.slug,
            'pk': self.pk,
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __unicode__(self):
        return u'{title} by {author}'.format(
            title=self.title,
            author=self.author,
        )

    class Meta:
        verbose_name_plural = "entries"
        ordering = ('-pk',)


class Comment(models.Model):
    entry = models.ForeignKey(Entry)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def gravatar_url(self):
        email_md5 = md5(self.email.encode())
        return "http://www.gravatar.com/avatar/{email_md5}.jpg?r=g".format(
            email_md5=email_md5.hexdigest()
        )

    def __str__(self):
        return self.body
