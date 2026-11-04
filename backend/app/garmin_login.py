"""Einmaliger Login (inkl. MFA); speichert nur Tokens in GARMIN_TOKENSTORE.

    python -m app.garmin_login
"""
import getpass
import os

from garminconnect import Garmin

from . import config

email = os.getenv("GARMIN_EMAIL") or input("Garmin E-Mail: ")
password = os.getenv("GARMIN_PASSWORD") or getpass.getpass("Garmin Passwort: ")
client = Garmin(email, password, prompt_mfa=lambda: input("MFA-Code: "))
client.login(config.TOKENSTORE)
print(f"Login ok. Tokens liegen in {config.TOKENSTORE}")
