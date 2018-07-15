from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.encoding import python_2_unicode_compatible
from django import forms
from django.core.mail import EmailMultiAlternatives

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    InlinePanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import (
    TextBlock,
    StructBlock,
    StreamBlock,
    FieldBlock,
    CharBlock,
    RichTextBlock,
    RawHTMLBlock,
)
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from django.shortcuts import render
from django.utils.html import strip_tags
from django.utils import translation
from django.utils.translation import gettext as _

import django

if django.get_version() >= "1.8":
    from django.template.loader import render_to_string
else:
    from django.template import loader, RequestContext

    def render_to_string(template_name, context=None, request=None):
        context_instance = RequestContext(request) if request else None
        return loader.render_to_string(template_name, context, context_instance)


# A couple of abstract classes that contain commonly used fields

EVENT_AUDIENCE_CHOICES = (("public", "Public"), ("private", "Private"))


class TranslatedField(object):
    def __init__(self, en_field, tet_field):
        self.en_field = en_field
        self.tet_field = tet_field

    def __get__(self, instance, owner):
        if translation.get_language() == "tet":
            return getattr(instance, self.tet_field)
        else:
            return getattr(instance, self.en_field)


class LinkFields(models.Model):
    link_external = models.URLField(_("External link"), blank=True)
    link_page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, related_name="+"
    )
    link_document = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True, related_name="+"
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel("link_external"),
        PageChooserPanel("link_page"),
        DocumentChooserPanel("link_document"),
    ]

    class Meta:
        abstract = True


class ContactMessage(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name=_("Name"))
    organisation = models.CharField(
        max_length=255, blank=True, verbose_name=_("Organisation")
    )
    email = models.EmailField(
        max_length=255, blank=True, verbose_name=_("Email Address")
    )
    phone = models.CharField(max_length=255, blank=True, verbose_name=_("Phone Number"))
    preffered = models.TextField(
        blank=True, null=True, verbose_name=_("Prefered Form of Contact")
    )
    message = models.TextField(blank=True, null=True, verbose_name=_("Message"))
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return self.name


class MembershipRequest(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name=_("name"))
    email = models.EmailField(
        max_length=255, blank=True, verbose_name=_("Email Address")
    )
    phone = models.CharField(max_length=255, blank=True, verbose_name=_("Phone Number"))
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return self.name


class SpaceRequest(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name=_("Name"))
    organisation = models.CharField(
        max_length=255, blank=True, verbose_name=_("Organisation")
    )
    email = models.EmailField(
        max_length=255, blank=True, verbose_name=_("Email Address")
    )
    phone = models.CharField(max_length=255, blank=True, verbose_name=_("Phone Number"))
    preffered = models.TextField(
        blank=True, null=True, verbose_name=_("Prefered Form of Contact")
    )
    message = models.TextField(blank=True, null=True, verbose_name=_("Body of Inquiry"))
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return self.name


class MembershipForm(forms.ModelForm):
    class Meta(object):
        model = MembershipRequest
        fields = ("name", "email", "phone")

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.fields["name"].error_messages["required"] = _("Enter your name")
        self.fields["email"].error_messages["required"] = _("Enter your email")
        self.fields["phone"].error_messages["required"] = _("Enter your phone")


class SpaceForm(forms.ModelForm):
    class Meta(object):
        model = SpaceRequest
        fields = ("name", "email", "organisation", "phone", "message")

    def __init__(self, *args, **kwargs):
        super(SpaceForm, self).__init__(*args, **kwargs)
        self.fields["name"].error_messages["required"] = _("Enter your name")
        self.fields["email"].error_messages["required"] = _("Enter your email")
        self.fields["phone"].error_messages["required"] = _("Enter your phone")
        self.fields["message"].error_messages["required"] = _("Enter the message")


class ContactForm(forms.ModelForm):
    class Meta(object):
        model = ContactMessage
        fields = ("name", "organisation", "email", "phone", "message")

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["name"].error_messages["required"] = _("Enter your name")
        self.fields["email"].error_messages["required"] = _("Enter your email")
        self.fields["phone"].error_messages["required"] = _("Enter your phone")
        self.fields["message"].error_messages["required"] = _("Enter the message")


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ("left", "Wrap left"),
            ("right", "Wrap right"),
            ("mid", "Mid width"),
            ("full", "Full width"),
        )
    )


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(("normal", "Normal"), ("full", "Full width")))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class CustomStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label="Raw HTML")
    document = DocumentChooserBlock(icon="doc-full-inverse")


# Related links


class RelatedLink(LinkFields):
    title_en = models.CharField(max_length=255, help_text="Link title")
    title_tet = models.CharField(max_length=255, help_text="Link title", null=True)
    title = TranslatedField("title_en", "title_tet")

    panels = [
        FieldPanel("title_en"),
        FieldPanel("title_tet"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Carousel items


class CarouselItem(LinkFields):
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    embed_url = models.URLField(_("Embed URL"), blank=True)
    caption_en = models.CharField(max_length=255, blank=True)
    caption_tet = models.CharField(max_length=255, blank=True, null=True)
    caption = TranslatedField("caption_en", "caption_tet")
    description_en = models.TextField(blank=True)
    description_tet = models.TextField(blank=True, null=True)
    description = TranslatedField("description_en", "description_tet")
    button_link_en = models.TextField(blank=True)
    button_link_tet = models.TextField(blank=True, null=True)
    button_link = TranslatedField("button_link_en", "button_link_tet")

    panels = [
        ImageChooserPanel("image"),
        FieldPanel("embed_url"),
        FieldPanel("caption_en"),
        FieldPanel("caption_tet"),
        FieldPanel("description_en"),
        FieldPanel("description_tet"),
        FieldPanel("button_link_en"),
        FieldPanel("button_link_tet"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class LinkBlock(LinkFields):
    title_en = models.CharField(max_length=255, help_text=_("Title"))
    title_tet = models.CharField(max_length=255, help_text=_("Title"), null=True)
    title = TranslatedField("title_en", "title_tet")

    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")
    link_title_en = models.CharField(max_length=255, help_text=_("Link title"))
    link_title_tet = models.CharField(max_length=255, help_text=_("Link title"))
    link_title = TranslatedField("link_title_en", "link_title_tet")

    panels = [
        FieldPanel("title_en"),
        FieldPanel("title_tet"),
        FieldPanel("body_en"),
        FieldPanel("body_tet"),
        FieldPanel("link_title_en"),
        FieldPanel("link_title_tet"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class ContactFields(models.Model):
    telephone = models.CharField(max_length=20, blank=True, verbose_name=_("Telephone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address_1 = models.CharField(
        max_length=255, blank=True, verbose_name=_("Address 1")
    )
    address_2 = models.CharField(
        max_length=255, blank=True, verbose_name=_("Address 2")
    )
    city = models.CharField(max_length=255, blank=True, verbose_name=_("City"))
    country = models.CharField(max_length=255, blank=True, verbose_name=_("Country"))
    post_code = models.CharField(max_length=10, blank=True, verbose_name=_("Post Code"))

    panels = [
        FieldPanel("telephone"),
        FieldPanel("email"),
        FieldPanel("address_1"),
        FieldPanel("address_2"),
        FieldPanel("city"),
        FieldPanel("country"),
        FieldPanel("post_code"),
    ]

    class Meta:
        abstract = True


class HomePageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.HomePage", related_name="home_blocks")


class HomePage(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        InlinePanel("home_blocks", label="Top Content Blocks"),
    ]


HomePage.promote_panels = Page.promote_panels


class MuseumPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.MuseumPage", related_name="home_blocks")


class MuseumPage(Page):
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")
    intro = TranslatedField("intro_en", "intro_tet")

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        InlinePanel("home_blocks", label="Top Content Blocks"),
    ]


class LibraryPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.LibraryPage", related_name="home_blocks")


class LibraryPage(Page):

    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        InlinePanel("home_blocks", label="Top Content Blocks"),
    ]


class AboutPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.AboutPage", related_name="home_blocks")


class AboutPage(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        InlinePanel("home_blocks", label="Page Blocks"),
    ]


class ExhPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.ExhibitionPage", related_name="home_blocks")


class ExhibitionPage(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")
    date_from = models.DateField("Start date", null=True, blank=True)
    date_to = models.DateField(
        "End date",
        null=True,
        blank=True,
        help_text="Not required if event is on a single day",
    )
    time_from = models.TimeField(_("Start time"), null=True, blank=True)
    time_to = models.TimeField(_("End time"), null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    cost = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Cost")
    )
    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    IS_PERMANENT_CHOICES = ((True, "Permanent"), (False, "Temporary"))

    is_permanent = models.BooleanField(choices=IS_PERMANENT_CHOICES)

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("is_permanent", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        ImageChooserPanel("feed_image"),
        FieldPanel("date_from"),
        FieldPanel("date_to"),
        FieldPanel("time_from"),
        FieldPanel("time_to"),
        FieldPanel("location"),
        FieldPanel("cost"),
        InlinePanel("carousel_items", label="Carousel items"),
    ]


class TemporaryExhibitionIndex(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body = TranslatedField("body_en", "body_tet")
    subpage_types = ["home.ExhibitionPage"]

    @property
    def exhibitions(self):
        # Get list of live event pages that are descendants of this page
        exh = (
            ExhibitionPage.objects.live().descendant_of(self).filter(is_permanent=False)
        )

        return exh

    content_panels = Page.content_panels + [
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("home_blocks", label="Top Content Blocks"),
        InlinePanel("carousel_items", label="Carousel items"),
    ]


class PermanentExhibitionIndex(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body = TranslatedField("body_en", "body_tet")
    subpage_types = ["home.ExhibitionPage"]

    @property
    def exhibitions(self):
        # Get list of live event pages that are descendants of this page
        exh = (
            ExhibitionPage.objects.live().descendant_of(self).filter(is_permanent=True)
        )

        return exh

    content_panels = Page.content_panels + [
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("home_blocks", label="Top Content Blocks"),
        InlinePanel("carousel_items", label="Carousel items"),
    ]


class BookSpace(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body = TranslatedField("body_en", "body_tet")
    thank_you_text_en = RichTextField(blank=True)
    thank_you_text_tet = RichTextField(blank=True)
    thank_you_text = TranslatedField("thank_you_text_en", "thank_you_text_tet")
    to_address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional - form submissions will be emailed to this address",
    )
    from_address = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        FieldPanel("thank_you_text_en", classname="full"),
        FieldPanel("thank_you_text_tet", classname="full"),
        MultiFieldPanel(
            [
                FieldPanel("to_address", classname="full"),
                FieldPanel("from_address", classname="full"),
                FieldPanel("subject", classname="full"),
            ],
            "Email",
        ),
    ]

    def serve(self, request):
        if request.method == "POST":
            form = ContactForm(request.POST)

            if form.is_valid():
                contact_fields = form.save()

                if self.to_address:
                    to_address = [
                        address.strip() for address in self.to_address.split(",")
                    ]
                    from_address = self.from_address
                    if "%s" not in self.from_address:
                        from_address = from_address.replace("@", "-%s@")
                    try:
                        from_address = from_address % get_random_string(15)
                    except Exception:
                        pass
                    from_address = "New Contact <%s>" % from_address
                    content = render_to_string(
                        "home/email/new_contact.html", {"fields": contact_fields}
                    )
                    msg = EmailMultiAlternatives(
                        self.subject, strip_tags(content), from_address, to_address
                    )
                    # msg.attach_alternative(content, "text/html")
                    msg.send(fail_silently=True)

                return render(
                    request,
                    "home/contact_us_page.html",
                    {"self": self, "form": ContactForm()},
                )
        else:
            form = ContactForm(initial={"page": self})

        return render(request, self.template, {"self": self, "form": form})


class BookSpaceCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.BookSpace", related_name=_("carousel_items"))


class ContactUsPage(Page, ContactFields):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")
    thank_you_text_en = RichTextField(blank=True)
    thank_you_text_tet = RichTextField(blank=True)
    thank_you_text = TranslatedField("thank_you_text_en", "thank_you_text_tet")
    to_address = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Optional - form submissions will be emailed to this address"),
    )

    from_address = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        FieldPanel("thank_you_text_en", classname="full"),
        FieldPanel("thank_you_text_tet", classname="full"),
        MultiFieldPanel(
            [
                FieldPanel("to_address", classname="full"),
                FieldPanel("from_address", classname="full"),
                FieldPanel("subject", classname="full"),
            ],
            "Email",
        ),
    ]

    def serve(self, request):
        if request.method == "POST":
            form = ContactForm(request.POST)

            if form.is_valid():
                contact_fields = form.save()

                if self.to_address:
                    to_address = [
                        address.strip() for address in self.to_address.split(",")
                    ]
                    from_address = self.from_address
                    if "%s" not in self.from_address:
                        from_address = from_address.replace("@", "-%s@")
                    try:
                        from_address = from_address % get_random_string(15)
                    except Exception:
                        pass
                    from_address = "New Contact <%s>" % from_address
                    content = render_to_string(
                        "home/email/new_contact.html", {"fields": contact_fields}
                    )
                    msg = EmailMultiAlternatives(
                        self.subject, strip_tags(content), from_address, to_address
                    )
                    # msg.attach_alternative(content, "text/html")
                    msg.send(fail_silently=True)

                return render(
                    request,
                    "home/contact_us_page.html",
                    {"self": self, "form": ContactForm()},
                )
        else:
            form = ContactForm(initial={"page": self})

        return render(request, self.template, {"self": self, "form": form})


class MemberShipPage(Page, ContactFields):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")
    thank_you_text_en = RichTextField(blank=True)
    thank_you_text_tet = RichTextField(blank=True)
    thank_you_text = TranslatedField("thank_you_text_en", "thank_you_text_tet")
    to_address = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Optional - form submissions will be emailed to this address"),
    )
    from_address = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro_en", classname="full"),
        FieldPanel("intro_tet", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("body_tet", classname="full"),
        FieldPanel("thank_you_text_en", classname="full"),
        FieldPanel("thank_you_text_tet", classname="full"),
        InlinePanel("carousel_items", label="Carousel items"),
        MultiFieldPanel(
            [
                FieldPanel("to_address", classname="full"),
                FieldPanel("from_address", classname="full"),
                FieldPanel("subject", classname="full"),
            ],
            "Email",
        ),
    ]

    def serve(self, request):
        if request.method == "POST":
            form = MembershipForm(request.POST)

            if form.is_valid():
                m_fields = form.save()

                if self.to_address:
                    to_address = [
                        address.strip() for address in self.to_address.split(",")
                    ]
                    from_address = self.from_address
                    if "%s" not in self.from_address:
                        from_address = from_address.replace("@", "-%s@")
                    try:
                        from_address = from_address % get_random_string(15)
                    except Exception:
                        pass
                    from_address = "New Contact <%s>" % from_address
                    content = render_to_string(
                        "home/email/new_contact.html", {"fields": m_fields}
                    )
                    msg = EmailMultiAlternatives(
                        self.subject, strip_tags(content), from_address, to_address
                    )
                    # msg.attach_alternative(content, "text/html")
                    msg.send(fail_silently=True)

                return render(
                    request,
                    "home/member_ship_page.html",
                    {"self": self, "form": MembershipForm()},
                )
        else:
            form = MembershipForm(initial={"page": self})

        return render(request, self.template, {"self": self, "form": form})


class BlogIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("home.BlogIndexPage", related_name="related_links")


class BlogIndexPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.BlogIndexPage", related_name="carousel_items")


class BlogIndexPage(Page):
    title_en = RichTextField(blank=True)
    title_tet = RichTextField(blank=True)
    title = TranslatedField("title_en", "title_tet")
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    subpage_types = ["home.BlogPage"]

    search_fields = Page.search_fields + [
        index.SearchField("intro_en"),
        index.SearchField("intro_tet"),
    ]

    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by("-date")

        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get("tag")
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get("page")
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context["blogs"] = blogs
        return context


BlogIndexPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("intro_en", classname="full"),
    FieldPanel("intro_tet", classname="full"),
    InlinePanel("carousel_items", label="Carousel items"),
]

BlogIndexPage.promote_panels = Page.promote_panels


# Blog page


class BlogPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.BlogPage", related_name="carousel_items")


class BlogPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("home.BlogPage", related_name="related_links")


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey("home.BlogPage", related_name="tagged_items")


class BlogPage(Page):

    title_en = RichTextField(blank=True)
    title_tet = RichTextField(blank=True)
    title = TranslatedField("title_en", "title_tet")
    tease_en = RichTextField(blank=True)
    tease_tet = RichTextField(blank=True)
    body_en = StreamField(CustomStreamBlock())
    body_tet = StreamField(CustomStreamBlock())
    body = TranslatedField("body_en", "body_tet")
    tease = TranslatedField("tease_en", "tease_tet")

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")

    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_fields = Page.search_fields + [index.SearchField("body")]

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()


BlogPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("tease_en", classname="blog tease"),
    FieldPanel("tease_tet", classname="blog tease"),
    FieldPanel("date"),
    StreamFieldPanel("body_en"),
    StreamFieldPanel("body_tet"),
    InlinePanel("carousel_items", label="Carousel items"),
    ImageChooserPanel("feed_image"),
]

BlogPage.promote_panels = Page.promote_panels + [FieldPanel("tags")]


# Event index page


class EventIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("home.EventIndexPage", related_name="related_links")


class EventIndexPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.EventIndexPage", related_name="carousel_items")


class EventIndexPage(Page):
    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    subpage_types = ["home.EventPage"]

    search_fields = Page.search_fields + [
        index.SearchField("intro_en"),
        index.SearchField("intro_tet"),
    ]

    @property
    def events(self):
        # Get list of live event pages that are descendants of this page
        events = EventPage.objects.live().descendant_of(self)

        # Order by date
        events = events.order_by("-date_from")

        return events


EventIndexPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("intro_en", classname="full"),
    FieldPanel("intro_tet", classname="full"),
    InlinePanel("carousel_items", label="Carousel items"),
]

EventIndexPage.promote_panels = Page.promote_panels


# Event page


class EventPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.EventPage", related_name="carousel_items")


class EventPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("home.EventPage", related_name="related_links")


class EventPageSpeaker(Orderable, LinkFields):
    page = ParentalKey("home.EventPage", related_name="speakers")
    first_name = models.CharField(_("Name"), max_length=255, blank=True)
    last_name = models.CharField(_("Surname"), max_length=255, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    @property
    def name_display(self):
        return self.first_name + " " + self.last_name

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        ImageChooserPanel("image"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]


class EventPage(Page):
    date_from = models.DateField("Start date")
    date_to = models.DateField(
        _("End date"),
        null=True,
        blank=True,
        help_text=_("Not required if event is on a single day"),
    )
    time_from = models.TimeField(_("Start time"), null=True, blank=True)
    time_to = models.TimeField(_("End time"), null=True, blank=True)
    audience = models.CharField(max_length=255, choices=EVENT_AUDIENCE_CHOICES)
    location = models.CharField(max_length=255)

    intro_en = RichTextField(blank=True)
    intro_tet = RichTextField(blank=True)
    intro = TranslatedField("intro_en", "intro_tet")
    body_en = RichTextField(blank=True)
    body_tet = RichTextField(blank=True)
    body = TranslatedField("body_en", "body_tet")

    title_en = RichTextField(blank=True)
    title_tet = RichTextField(blank=True)
    title = TranslatedField("title_en", "title_tet")
    cost = models.CharField(max_length=255)
    signup_link = models.URLField(blank=True)
    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_fields = Page.search_fields + [
        index.SearchField("get_audience_display"),
        index.SearchField("location"),
        index.SearchField("body"),
    ]

    @property
    def event_index(self):
        # Find closest ancestor which is an event index
        return self.get_ancestors().type(EventIndexPage).last()

    def serve(self, request):
        if "format" in request.GET:
            if request.GET["format"] == "ical":
                # Export to ical format
                response = HttpResponse(
                    export_event(self, "ical"), content_type="text/calendar"
                )
                response["Content-Disposition"] = (
                    "attachment; filename=" + self.slug + ".ics"
                )
                return response
            else:
                # Unrecognised format error
                message = (
                    "Could not export event\n\nUnrecognised format: "
                    + request.GET["format"]
                )
                return HttpResponse(message, content_type="text/plain")
        else:
            # Display event page as usual
            return super(EventPage, self).serve(request)


EventPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("intro_en", classname="full title"),
    FieldPanel("intro_tet", classname="full title"),
    FieldPanel("body_en", classname="full body"),
    FieldPanel("body_tet", classname="full body"),
    ImageChooserPanel("feed_image"),
    FieldPanel("date_from"),
    FieldPanel("date_to"),
    FieldPanel("time_from"),
    FieldPanel("time_to"),
    FieldPanel("location"),
    FieldPanel("audience"),
    FieldPanel("cost"),
    FieldPanel("signup_link"),
    InlinePanel("carousel_items", label="Carousel items"),
    InlinePanel("speakers", label="Speakers"),
]


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="form_fields")


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)


FormPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("intro", classname="full"),
    InlinePanel("form_fields", label="Form fields"),
    FieldPanel("thank_you_text", classname="full"),
    MultiFieldPanel(
        [
            FieldRowPanel(
                [
                    FieldPanel("from_address", classname="col6"),
                    FieldPanel("to_address", classname="col6"),
                ]
            ),
            FieldPanel("subject"),
        ],
        "Email",
    ),
]


class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.HomePage", related_name="carousel_items")


class LibraryPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.LibraryPage", related_name="carousel_items")


class MuseumPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.MuseumPage", related_name="carousel_items")


class ContactUsPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.ContactUsPage", related_name="carousel_items")


class MemberShipPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.MemberShipPage", related_name="carousel_items")


class ExhibitionPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.ExhibitionPage", related_name="carousel_items")


class PermanentExhibitionPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.PermanentExhibitionIndex", related_name="carousel_items")


class TemporaryExhibitionPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.TemporaryExhibitionIndex", related_name="carousel_items")


class PermExhibPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.PermanentExhibitionIndex", related_name="home_blocks")


class TempExhibPageBlocks(Orderable, LinkBlock):
    page = ParentalKey("home.TemporaryExhibitionIndex", related_name="home_blocks")


class AboutPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey("home.AboutPage", related_name="carousel_items")
