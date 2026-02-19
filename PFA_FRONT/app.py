import streamlit as st
from streamlit_cookies_controller import CookieController
import pandas as pd
from urllib.parse import urlencode
import hashlib
import os
import base64
import httpx
import asyncio
from utils import get_login_url, get_register_url, get_logout_url, post_request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = CookieController()

query_params = st.query_params


# if "code" in query_params and not st.session_state.get("auth_done", False):
#     st.session_state.auth_done = True
#     code = query_params["code"]
#     st.success(f"Otrzymano code: {query_params}")
#     cookies = controller.getAll()
#     pkce = cookies.get("kc_pkce_verifier")
#
#
#     logger.info(f"XXXXXXXXXXXXXXX")
#     logger.info(f"XXXXXXXXXXXXXXX {cookies.get("kc_pkce_verifier")}")
#     logger.info(f"XXXXXXXXXXXXXXX")
#
#
#     r =  httpx.post("http://pfa:8000/auth/login",json={"code":code, "code_verifier":pkce})
#     r.raise_for_status()
#     r_data = r.json()
#     st.error(f"Otrzymano code: {r_data}")
#
#     st.session_state.logged_in = True



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    st.title("Witaj w aplikacji Bla Bla!")
    st.write("To jest przykładowa aplikacja Streamlit. Zaloguj się lub zarejestruj, aby kontynuować.")

    col1, col2, col3 = st.columns(3)
    with col1:
        # login_url = get_login_url(controller)
        # st.link_button(
        #     "Zaloguj",
        #     login_url
        # )
        st.link_button(
            "Zaloguj",
            "http://localhost:8000/auth/login"
        )

    with col2:
        register_url = get_register_url()
        st.link_button(
            "Rejestracja",
            register_url
        )

    with col3:
        logout_url = get_logout_url()
        st.link_button(
            "Wyloguj",
            logout_url
        )




if st.session_state.logged_in:
    st.title("Panel użytkownika")

    # Przykładowe przyciski
    st.subheader("Akcje")
    if st.button("Powiedz cześć"):
        st.write("Cześć! Miło Cię widzieć!")

    if st.button("Pokaż info"):
        st.write("To jest przykładowa aplikacja z formularzem, plikami i tabelą.")

    # Formularz
    st.subheader("Formularz")
    with st.form("formularz"):
        name = st.text_input("Twoje imię")
        age = st.number_input("Twój wiek", min_value=0, max_value=120)
        submitted = st.form_submit_button("Wyślij")
        if submitted:
            st.write(f"Witaj {name}, masz {age} lat!")

    # Dodawanie pliku
    st.subheader("Dodaj plik")
    uploaded_file = st.file_uploader("Wybierz plik")
    if uploaded_file:
        st.write(f"Wczytano plik: {uploaded_file.name}")
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
        except:
            st.write("Nie udało się wczytać pliku jako CSV.")

    # Prosta tabelka
    st.subheader("Przykładowa tabela")
    data = {
        "Produkt": ["Jabłka", "Banany", "Gruszki"],
        "Cena": [5.5, 7.2, 6.0],
        "Ilość": [10, 20, 15]
    }
    df = pd.DataFrame(data)
    st.table(df)



