import streamlit as st
from PIL import Image
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page
from utils.cert_utils import get_asset_path  # import helper for absolute paths

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

st.title("Certificate Validation System")
st.write("")
st.subheader("Select Your Role")

col1, col2 = st.columns(2)

# Use absolute paths for images
institute_logo_path = get_asset_path("institute_logo.png")
company_logo_path = get_asset_path("company_logo.jpg")

with col1:
    institite_logo = Image.open(institute_logo_path)
    st.image(institite_logo, output_format="png", width=230)
    clicked_institute = st.button("Institute")

with col2:
    company_logo = Image.open(company_logo_path)
    st.image(company_logo, output_format="jpg", width=230)
    clicked_verifier = st.button("Verifier")

if clicked_institute:
    st.session_state.profile = "Institute"
    switch_page('login')
elif clicked_verifier:
    st.session_state.profile = "Verifier"
    switch_page('login')
