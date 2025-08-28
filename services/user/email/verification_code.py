import random
import time
from typing import Tuple

class VerificationCodeManager:
    CODE_RESEND_INTERVAL = 60
    VERIFICATION_CODE_LENGTH = 6

    def __init__(self):
        self._last_code_sent = {}

    def can_send_code(self, email: str) -> Tuple[bool, int]:
        current_time = time.time()
        last_sent_time = self._last_code_sent.get(email, 0)

        if current_time - last_sent_time < self.CODE_RESEND_INTERVAL:
            wait_time = int(self.CODE_RESEND_INTERVAL - (current_time - last_sent_time))
            return False, wait_time

        self._last_code_sent[email] = current_time
        return True, 0

    def generate_code(self) -> str:
        code = ''.join(random.choices('0123456789', k=self.VERIFICATION_CODE_LENGTH))
        return code
