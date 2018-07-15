from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from search import views as search_views
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_control
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    url(r"^django-admin/", include(admin.site.urls)),
    url(r"^admin/", include(wagtailadmin_urls)),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(r"^rosetta/", include("rosetta.urls")),
    url("^i18n/", include("django.conf.urls.i18n")),
    url(
        r"^sw.js",
        cache_control(max_age=25920000)(
            TemplateView.as_view(
                template_name="sw.js", content_type="application/javascript"
            )
        ),
        name="sw.js",
    ),
    url(
        r"^manifest.json",
        cache_control(max_age=25920000)(
            TemplateView.as_view(
                template_name="manifest.json", content_type="application/javascript"
            )
        ),
        name="manifest.json",
    ),
]


urlpatterns += i18n_patterns(
    # These URLs will have /<language_code>/ appended to the beginning
    url(r"^search/$", search_views.search, name="search"),
    url(r"", include(wagtail_urls)),
)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
