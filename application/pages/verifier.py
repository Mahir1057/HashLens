import streamlit as st
import os
import hashlib
import tempfile
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate, displayPDF, hide_icons, hide_sidebar, remove_whitespaces
from connection import contract

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# Capture query parameters (for QR auto-fill)
params = st.experimental_get_query_params()
method = params.get("method", [None])[0]
prefill_cert_id = params.get("cert_id", [None])[0]

options = ("Verify Certificate using PDF", "View/Verify Certificate using Certificate ID")
default_index = 1 if method == "id" else 0
selected = st.selectbox("", options, index=default_index, label_visibility="hidden")

# ------------------- Option 0: Verify using PDF ------------------- #
if selected == options[0]:
    uploaded_file = st.file_uploader("Upload the PDF version of the certificate", type=['pdf'])
    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File size too large. Please upload a file smaller than 10MB.")
        else:
            bytes_data = uploaded_file.getvalue()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(bytes_data)
                temp_file_path = temp_file.name
            
            try:
                # Extract data from PDF
                uid, candidate_name, course_name, org_name = extract_certificate(temp_file_path)
                displayPDF(temp_file_path)

                # Use the SAME hashing method as in institute.py
                data_to_hash = f"{uid.strip()}{candidate_name.strip()}{course_name.strip()}{org_name.strip()}".encode('utf-8')
                certificate_id = hashlib.sha256(data_to_hash).hexdigest()

                # Smart Contract Call
                result = contract.functions.isVerified(certificate_id).call()
                if result:
                    st.success("Certificate validated successfully!")
                else:
                    st.error("Invalid Certificate! Certificate might be tampered")
                    
            except FileNotFoundError:
                st.error("Certificate file not found!")
            except ValueError as e:
                st.error(f"Certificate format error: {str(e)}")
            except Exception as e:
                st.error("Invalid Certificate! Certificate might be tampered")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

# ------------------- Option 1: Verify using Certificate ID ------------------- #
elif selected == options[1]:
    certificate_id = st.text_input("Enter the Certificate ID", value=prefill_cert_id if prefill_cert_id else "")
    
    auto_trigger = bool(prefill_cert_id)  # True if coming from QR link
    
    if st.button("Validate") or auto_trigger:
        if not certificate_id or not certificate_id.strip():
            st.error("Please enter a valid Certificate ID!")
        else:
            try:
                view_certificate(certificate_id.strip())
                result = contract.functions.isVerified(certificate_id.strip()).call()
                if result:
                    st.success("Certificate validated successfully!")
                else:
                    st.error("Invalid Certificate ID!")
            except ValueError as e:
                st.error(f"Invalid Certificate ID format: {str(e)}")
            except Exception as e:
                st.error("Invalid Certificate ID!")
