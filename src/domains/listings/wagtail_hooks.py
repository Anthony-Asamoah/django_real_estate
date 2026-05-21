from wagtail.snippets.models import register_snippet
from .models import Listing, ListingViewSet

register_snippet(ListingViewSet)
