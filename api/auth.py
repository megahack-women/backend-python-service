from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication, exceptions
from datetime import datetime
from api.models import User
import local


class CustomAuthentication(authentication.TokenAuthentication):
	keyword = 'Bearer'

	def authenticate_credentials(self, key):
		try:
			user = User.objects.get(key=key, is_active=1)
		except:
			raise exceptions.AuthenticationFailed(_('Invalid token.'))
		
		user.last_login = datetime.now()
		user.save(update_fields=['last_login'])
		
		return (user, None)
		