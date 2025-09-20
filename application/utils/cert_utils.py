from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pdfplumber
from pathlib import Path

def get_asset_path(filename: str) -> str:
    """Return the absolute path to an asset in the assets folder."""
    base_dir = Path(__file__).parent.parent  # points to 'application/' folder
    asset_path = base_dir / "assets" / filename
    if not asset_path.exists():
        raise FileNotFoundError(f"Asset not found: {asset_path}")
    return str(asset_path)

def generate_certificate(output_path, uid, candidate_name, course_name, org_name, institute_logo_filename):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    # Add institute logo
    if institute_logo_filename:
        abs_logo_path = get_asset_path(institute_logo_filename)
        logo = RLImage(abs_logo_path, width=150, height=150)
        elements.append(logo)

    # Institute name
    institute_style = ParagraphStyle(
        "InstituteStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        spaceAfter=40,
    )
    institute = Paragraph(org_name, institute_style)
    elements.extend([institute, Spacer(1, 12)])

    # Title
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        spaceAfter=20,
    )
    title1 = Paragraph("Certificate of Completion", title_style)
    elements.extend([title1, Spacer(1, 6)])

    # Recipient
    recipient_style = ParagraphStyle(
        "RecipientStyle",
        parent=getSampleStyleSheet()["BodyText"],
        fontSize=14,
        spaceAfter=6,
        leading=18,
        alignment=1
    )
    recipient_text = f"""
    This is to certify that<br/><br/>
    <font color='red'>{candidate_name}</font><br/>
    with UID<br/>
    <font color='red'>{uid}</font><br/><br/>
    has successfully completed the course:<br/>
    <font color='blue'>{course_name}</font>
    """
    recipient = Paragraph(recipient_text, recipient_style)
    elements.extend([recipient, Spacer(1, 12)])

    # Build PDF
    doc.build(elements)
    print(f"Certificate generated and saved at: {output_path}")

def extract_certificate(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        lines = text.splitlines()

        org_name = lines[0]
        candidate_name = lines[3]
        uid = lines[5]
        course_name = lines[-1]

        return (uid, candidate_name, course_name, org_name)
