from typing import Optional

from django.db.models import Q
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

from configuracion.models import Configuration
from utils.crypto import generate_hash


def generate_invoice(response, petition):
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # =========================
    # PAGE SETUP
    # =========================
    left_margin = 2.8 * cm
    right_margin = 2.8 * cm
    center_x = width / 2
    y = height - 3 * cm

    c.setTitle("ACUERDO DE CESIÓN DE USO DE TAQUILLAS")

    # =========================
    # TAQUILLA NUMBER (Centered small box style)
    # =========================
    if petition.item:
        c.setFont("Helvetica", 11)
        c.drawCentredString(center_x, y, f"Taquilla: {petition.item.code}")
        y -= 1.5 * cm

    # =========================
    # MAIN TITLE
    # =========================
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(
        center_x,
        y,
        "ACUERDO DE CESIÓN DE USO DE TAQUILLAS 2025 / 2026"
    )
    y -= 1.2 * cm

    # Subtitle
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(
        center_x,
        y,
        "Delegación de Alumnos de la ETSIAE"
    )
    y -= 2 * cm

    # =========================
    # BODY INTRO
    # =========================
    c.setFont("Helvetica", 11)
    c.drawString(
        left_margin,
        y,
        "Por el presente documento los/as alumnos/as de la ETSI Aeronáutica y del Espacio:"
    )
    y -= 1.2 * cm

    # =========================
    # TITULAR BLOCK (only 1 active, but layout supports 4)
    # =========================
    user = petition.user
    dni = user.dni or ""
    email = user.email or ""
    phone = user.phone or ""

    def titular_block(number, name="", dni="", phone="", email=""):
        nonlocal y
        c.setFont("Helvetica", 11)
        c.drawString(left_margin, y, f"Titular {number}:")
        y -= 0.8 * cm

        c.drawString(left_margin, y, f"D./Dña {name}")
        y -= 0.7 * cm

        c.drawString(left_margin, y, f"con DNI número {dni}")
        y -= 0.7 * cm

        c.drawString(left_margin, y, f"número de Teléfono de contacto {phone}")
        y -= 0.7 * cm

        c.drawString(left_margin, y, f"email {email}")
        y -= 1.2 * cm

    # Fill first titular
    titular_block(1, user.username, dni, phone, email)

    # Empty placeholders for visual match
    for i in range(2, 5):
        titular_block(i)

    # =========================
    # PETITION TEXT
    # =========================
    item_code = petition.item.code if petition.item else ""
    c.drawString(
        left_margin,
        y,
        f"solicitan el uso de la taquilla {item_code} durante el período de un año académico"
        " por el importe total de 5 euros."
    )
    y -= 1.2 * cm

    c.drawString(
        left_margin,
        y,
        "Al firmar el presente documento aceptas la última Normativa de Taquillas aprobada "
        "por la Junta de Delegados de la ETSI Aeronáutica y del Espacio."
    )
    y -= 1.2 * cm

    # =========================
    # SIGNATURE AREA
    # =========================
    signature_y = 5 * cm

    c.setFont("Helvetica", 11)

    # Left signature
    c.drawString(left_margin, signature_y, "Fdo.: ___________________________")
    c.drawString(left_margin, signature_y - 0.8 * cm, "El / La Titular 1")

    # Right signature (Delegación)
    right_sig_x = width - right_margin - 7 * cm
    c.drawString(right_sig_x, signature_y, "Fdo.: ___________________________")
    c.drawString(
        right_sig_x,
        signature_y - 0.8 * cm,
        "Delegación de Alumnos ETSI Aeronáutica y del Espacio"
    )

    # =========================
    # DATE (Centered Bottom)
    # =========================
    date = petition.until or timezone.now()
    c.drawCentredString(
        center_x,
        3.2 * cm,
        f"Madrid, a {date.strftime('%d de %B de %Y')}"
    )

    # =========================
    # VALIDATION CODE
    # =========================
    if petition.status == petition.Status.ACTIVE:
        c.setFont("Courier", 8)
        c.drawCentredString(
            center_x,
            2.5 * cm,
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

