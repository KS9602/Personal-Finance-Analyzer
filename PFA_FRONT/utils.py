import streamlit as st
from streamlit_cookies_controller import CookieController
import pandas as pd
from urllib.parse import urlencode
import hashlib
import os
import base64
import httpx
import asyncio

KEYCLOAK_URL = "http://localhost:9000"
REALM = "PFA"
CLIENT_ID = "pfa_frontend"
REDIRECT_URI = "http://localhost:3000"



def generate_code_verifier():
    random_bytes = os.urandom(32)
    return base64.urlsafe_b64encode(random_bytes).rstrip(b"=").decode("utf-8")

def generate_code_challenge(verifier: str):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")


def get_login_url(controller):
    code_verifier = generate_code_verifier()
    controller.set("kc_pkce_verifier",code_verifier)
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print(f"XXXXXXXXXXXXXXXXXXXXXXX {code_verifier}")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    print("XXXXXXXXXXXXXXXXXXXXXXX")
    # controller.set("logged_in_process",True)
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth?{urlencode(params)}"
    return url


async def post_request(data):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://pfa:8000/auth/login",
            json=data)

        resp.raise_for_status()
        tokens = resp.json()
        return resp.json()

# Funkcja do generowania URL rejestracji
def get_register_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "kc_action": "register"
    }
    return f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth?{urlencode(params)}"

def get_logout_url():
    return f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/logout?post_logout_redirect_uri={REDIRECT_URI}"

