import streamlit as st
import math

st.title("Konwerter stopni i węzłów na ludzkie miary 🛥️")

with st.form("conversion_form"):
    deg = st.number_input("Podaj kąt w stopniach:", value=30.0)
    knots = st.number_input("Podaj prędkość w węzłach:", value=10.0)
    submitted = st.form_submit_button("Konwertuj")

def deg_to_rad(d):
    return d * math.pi / 180

def deg_to_percent(d):
    return math.tan(math.radians(d)) * 100

def knots_to_kmh(k):
    return k * 1.852

def knots_to_ms(k):
    return k * 0.514444

if submitted:
    rad = deg_to_rad(deg)
    percent = deg_to_percent(deg)
    kmh = knots_to_kmh(knots)
    ms = knots_to_ms(knots)

    st.subheader("Wyniki konwersji")
    st.write(f"**Kąt:** {deg:.2f}° = {rad:.2f} rad ≈ pochylenie {percent:.2f}%")
    st.write(f"**Prędkość:** {knots:.2f} węzłów = {kmh:.2f} km/h = {ms:.2f} m/s")
