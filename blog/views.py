from django.views.generic import CreateView

from .forms import CommentForm
from .models import Entry


class EntryDetail(CreateView):
    model = Entry
    template_name = 'blog/entry_detail.html'
    from_class = CommentForm
