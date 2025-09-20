import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import hashlib
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from utils.cert_utils import get_asset_path
from utils.streamlit_utils import view_certificate, hide_icons, hide_sidebar, remove_whitespaces
from connection import contract, w3

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")

# -------------------- Pinata Upload -------------------- #
def upload_to_pinata(file_path, api_key, api_secret):
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }
    with open(file_path, "rb") as file:
        files = {"file": (file.name, file)}
        response = requests.post(pinata_api_url, headers=headers, files=files)
        result = json.loads(response.text)
        if "IpfsHash" in result:
            return result["IpfsHash"]
        else:
            st.error(f"Error uploading to Pinata: {result.get('error', 'Unknown error')}")
            return None

# -------------------- Certificate Generation -------------------- #
def generate_certificate_with_qr(file_path, uid, candidate_name, course_name, org_name, logo_filename, certificate_id):
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(certificate_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_path = "qr.png"
    qr_img.save(qr_path)

    # Create PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 50

    # Title
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - margin - 50, "Certificate of Completion")

    # Candidate details
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - margin - 120, f"Presented to: {candidate_name}")
    c.drawCentredString(width/2, height - margin - 160, f"For successfully completing: {course_name}")
    c.drawCentredString(width/2, height - margin - 200, f"Issued by: {org_name}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, height - margin - 240, f"UID: {uid}")

    # Logo at top-left
    logo_path = get_asset_path(logo_filename)
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, margin, height - margin - 100, width=100, preserveAspectRatio=True, mask="auto")

    # QR code at bottom-right
    qr_size = 1.5 * inch
    c.drawImage(qr_path, width - margin - qr_size, margin, qr_size, qr_size)
    # Optional QR border
    c.rect(width - margin - qr_size - 5, margin - 5, qr_size + 10, qr_size + 10)

    c.save()
    os.remove(qr_path)  # cleanup

# -------------------- Streamlit UI -------------------- #
options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("", options, label_visibility="hidden")

if selected == options[0]:
    form = st.form("Generate-Certificate")
    uid = form.text_input(label="UID")
    candidate_name = form.text_input(label="Name")
    course_name = form.text_input(label="Course Name")
    org_name = form.text_input(label="Org Name")
    submit = form.form_submit_button("Submit")

    if submit:
        pdf_file_path = "certificate.pdf"
        institute_logo_filename = "logo.jpg"

        # Generate unique certificate ID
        data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
        certificate_id = hashlib.sha256(data_to_hash).hexdigest()

        # Create certificate with QR
        generate_certificate_with_qr(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_filename, certificate_id)

        # Upload to Pinata
        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
        os.remove(pdf_file_path)

        if ipfs_hash:
            # Store in smart contract
            contract.functions.generateCertificate(
                certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash
            ).transact({'from': w3.eth.accounts[0]})

            st.success(f"Certificate successfully generated with Certificate ID: {certificate_id}")

else:
    form = st.form("View-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Submit")
    if submit:
        try:
            view_certificate(certificate_id)
        except Exception:
            st.error("Invalid Certificate ID!")
