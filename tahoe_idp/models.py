from urllib.parse import urlencode, urljoin

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from tahoe_idp import magiclink_settings

User = get_user_model()


class MagicLinkError(Exception):
    pass


class MagicLink(models.Model):
    username = models.CharField()
    token = models.TextField()
    expiry = models.DateTimeField()
    redirect_url = models.TextField()
    disabled = models.BooleanField(default=False)
    times_used = models.IntegerField(default=0)
    created = models.DateTimeField()

    def __str__(self):
        return '{username} - {expiry}'.format(username=self.username, expiry=self.expiry)

    def used(self) -> None:
        self.times_used += 1
        if self.times_used >= magiclink_settings.TOKEN_USES:
            self.disabled = True
        self.save()

    def disable(self) -> None:
        self.times_used += 1
        self.disabled = True
        self.save()

    def generate_url(self, request: HttpRequest) -> str:
        url_path = reverse(magiclink_settings.LOGIN_VERIFY_URL)

        params = {'token': self.token}
        if magiclink_settings.VERIFY_INCLUDE_USERNAME:
            params['username'] = self.username
        query = urlencode(params)

        url_path = '{url_path}?{query}'.format(url_path=url_path, query=query)
        scheme = request.is_secure() and 'https' or 'http'
        url = urljoin(
            '{scheme}://{studio_domain}'.format(scheme=scheme, studio_domain=magiclink_settings.STUDIO_DOMAIN),
            url_path
        )
        return url

    def validate(
        self,
        request: HttpRequest,
        username: str = '',
    ) -> AbstractUser:
        if magiclink_settings.VERIFY_INCLUDE_USERNAME and self.username != username:
            raise MagicLinkError('username does not match')

        if timezone.now() > self.expiry:
            self.disable()
            raise MagicLinkError('Magic link has expired')

        if self.times_used >= magiclink_settings.TOKEN_USES:
            self.disable()
            raise MagicLinkError('Magic link has been used too many times')

        user = User.objects.get(username=self.username)

        if not magiclink_settings.ALLOW_SUPERUSER_LOGIN and user.is_superuser:
            self.disable()
            raise MagicLinkError(
                'You can not login to a super user account using a magic link')

        if not magiclink_settings.ALLOW_STAFF_LOGIN and user.is_staff:
            self.disable()
            raise MagicLinkError(
                'You can not login to a staff account using a magic link')

        return user
