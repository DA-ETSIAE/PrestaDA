from typing import Optional

from django.db.models import Q
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import KeepInFrame
from reportlab.platypus import Spacer
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import PageTemplate
from reportlab.platypus import Frame
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from configuracion.models import Configuration
from utils.crypto import generate_hash


def generate_invoice(response, petition):
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    c.setTitle(Configuration.objects.get(node='agreement_title').value)

    # Margins
    left_margin = 2.5 * cm
    right_margin = 2.5 * cm
    usable_width = width - left_margin - right_margin

    y = height - 2.5 * cm

    # =========================
    # TAQUILLA (Centered small box style)
    # =========================
    if petition.item:
        c.setFont("Helvetica", 11)
        c.drawCentredString(width / 2, y, f"Ítem: {petition.item.code}")
        y -= 1.2 * cm

    # =========================
    # MAIN TITLE (Centered, uppercase)
    # =========================
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(
        width / 2,
        y,
        Configuration.objects.get(node='agreement_header').value.upper()
    )
    y -= 1.2 * cm

    # Subtitle
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(
        width / 2,
        y,
        Configuration.objects.get(node='org').value
    )
    y -= 1.8 * cm

    # =========================
    # BODY TEXT (Formal paragraph style)
    # =========================
    c.setFont("Helvetica", 11)

    user = petition.user
    dni = user.dni or ""
    email = user.email or ""
    phone = user.phone or ""
    tipo = petition.type.name
    date = petition.until

    text = c.beginText(left_margin, y)
    text.setLeading(16)

    text.textLine("Por el presente documento el/la alumno/a:")
    text.textLine("")
    text.textLine(f"D./Dña {user.username}, con DNI número {dni},")
    text.textLine(f"email {email} y número de teléfono {phone},")
    text.textLine("")
    text.textLine(
        f"solicita el uso de la {tipo}"
        f"{' ' + petition.item.code if petition.item else ''}"
        f" durante el período de un año académico."
    )
    text.textLine("")
    text.textLine(
        "Al firmar el presente documento acepta la normativa vigente "
        "y las condiciones establecidas para el uso."
    )

    if petition.type.conditions:
        text.textLine("")
        for line in petition.type.conditions.splitlines():
            text.textLine(line)

    c.drawText(text)

    # =========================
    # SIGNATURE AREA
    # =========================
    signature_y = 5 * cm

    c.setFont("Helvetica", 11)
    c.drawString(left_margin, signature_y, "Fdo.: ___________________________")
    c.drawString(left_margin, signature_y - 0.8 * cm, "El / La Titular")

    c.drawString(width - right_margin - 7 * cm, signature_y,
                 "Fdo.: ___________________________")
    c.drawString(width - right_margin - 7 * cm,
                 signature_y - 0.8 * cm,
                 Configuration.objects.get(node='org').value)

    # =========================
    # DATE (Centered bottom)
    # =========================
    if date:
        c.setFont("Helvetica", 11)
        c.drawCentredString(
            width / 2,
            3 * cm,
            f"Madrid, a {date.strftime('%d de %B de %Y')}"
        )

    # =========================
    # VALIDATION CODE (small footer text)
    # =========================
    if petition.status == petition.Status.ACTIVE:
        c.setFont("Courier", 8)
        c.drawCentredString(
            width / 2,
            2.3 * cm,
            f"{petition.id}-{generate_hash(dni, petition.id)}"
        )

    c.showPage()
    c.save()

def generate_registry(response, start_date, end_date, type: Optional[Type]):
    if type:
        petitions = Petition.objects.filter(until__date__range=(start_date, end_date), type=type)
    else:
        petitions = Petition.objects.filter(until__date__range=(start_date, end_date))


    petitions.filter(Q(status=Petition.Status.ACTIVE) | Q(status=Petition.Status.EXPIRED) | Q(status=Petition.Status.COLLECTED))
    c = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * cm, y, "Nombre")
    c.drawString(10 * cm, y, "Tipo")
    c.drawString(18 * cm, y, "Código")
    c.drawString(22 * cm, y, "Fecha (Desde / Hasta)")

    c.setFont("Helvetica", 11)
    y -= 1 * cm
    for petition in petitions:
        name = petition.user.first_name
        tipo = petition.type.name
        item = petition.item.code if petition.item else ""
        date_reserved = petition.date_reserved.strftime("%Y-%m-%d") if petition.date_reserved else ""
        until = petition.until.strftime("%Y-%m-%d") if petition.until else ""

        c.drawString(1 * cm, y, str(petition.id) + "-" + name)
        c.drawString(10 * cm, y, tipo)
        c.drawString(18 * cm, y, item)
        c.drawString(22 * cm, y, date_reserved + " a " + until)

        c.setStrokeColor(gray)
        c.setLineWidth(0.3)
        c.line(2 * cm, y - 2, width - 2 * cm, y - 2)

        y -= 0.8 * cm

        if y < 2 * cm:
            c.showPage()
            y = height - 3 * cm

    c.save()

