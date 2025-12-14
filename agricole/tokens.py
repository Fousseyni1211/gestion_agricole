from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int
from django.utils import timezone

class ExpiringTokenGenerator(PasswordResetTokenGenerator):
    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False
        try:
            ts_b36 = token.split("-")[1]
            ts = base36_to_int(ts_b36)
        except Exception:
            return False
        # Expire après 24 heures
        now_ts = self._num_seconds(self._today())
        return (now_ts - ts) <= 86400  # 24h en secondes

token_generator_24h = ExpiringTokenGenerator()
