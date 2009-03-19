from urllib import urlencode, urlopen
from urlparse import urljoin

from django.conf import settings

from django.contrib.auth.models import User

__all__ = ['CASBackend']

service = settings.CAS_SERVICE
cas_base = settings.CAS_BASE
cas_login = cas_base + 'login/'
cas_validate = cas_base + 'validate/'
cas_logout = cas_base + 'logout/'
cas_next_default = settings.CAS_NEXT_DEFAULT
cas_profile = settings.CAS_PROFILE
cas_register = settings.CAS_REGISTER

def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}
    url = cas_validate + '?' + urlencode(params)
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip()
        else:
            return None
    finally:
        page.close()
        
class CASBackend(object):
    """CAS authentication backend"""

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""

        username = _verify_cas1(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None