from typing import Optional

from django.db.models import Q
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from configuracion.models import Configuration
from utils.crypto import generate_hash


def generate_invoice(response, petition):
    months_es = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    left_margin = 1.8 * cm
    right_margin = 1.8 * cm
    center_x = width / 2
    y = height - 3 * cm

    c.setTitle("ACUERDO PRÉSTAMO")

    # =========================
    # TITLE
    # =========================
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(
        center_x,
        y,
        "ACUERDO DE PRÉSTAMO 2025 / 2026"
    )
    y -= 1.2 * cm

    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(
        center_x,
        y,
        "Delegación de Alumnos de la ETSIAE"
    )
    y -= 2 * cm

    # =========================
    # INTRO
    # =========================
    user = petition.user
    c.setFont("Helvetica", 11)
    c.drawString(
        left_margin,
        y,
        f"Por el presente documento el/la alumno/a {user.first_name} {user.last_name}"
    )
    y -= 1.2 * cm

    # =========================
    # TITULAR
    # =========================
    dni = user.dni or ""
    email = user.email or ""
    phone = user.phone or ""

    # DNI
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_margin, y, "Con DNI/NIE: ")
    c.setFont("Helvetica", 11)
    c.drawString(left_margin + 3 * cm, y, dni)
    y -= 0.8 * cm

    # Teléfono
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_margin, y, "Número de teléfono:")
    c.setFont("Helvetica", 11)
    c.drawString(left_margin + 3.8 * cm, y, phone)
    y -= 0.8 * cm

    # Email
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_margin, y, "E-mail ")
    c.setFont("Helvetica", 11)
    c.drawString(left_margin + 1.3 * cm, y, email)
    y -= 1.5 * cm

    # =========================
    # FECHA FORMATEADA
    # =========================
    if petition.until:
        until_date = petition.until
        formatted_date = (
            f"{until_date.day} de "
            f"{months_es[until_date.month - 1]} de "
            f"{until_date.year}"
        )
    else:
        formatted_date = "N/A"

    # =========================
    # REQUEST TEXT
    # =========================
    item_code = petition.item.code if petition.item else "N/A"
    item_type = petition.type.name if petition.type else "N/A"

    c.setFont("Helvetica", 11)
    c.drawString(left_margin, y, f"Acuerda el uso de:")
    y -= 1 * cm
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, f"{item_code} ({item_type})")
    y -= 1 * cm

    c.setFont("Helvetica", 11)
    c.drawString(left_margin, y, f"hasta {formatted_date}.")
    
    
    y -= 1.5 * cm

    # =========================
    # CONDITIONS
    # =========================
    c.drawString(
        left_margin,
        y,
        "Al firmar el documento se acepta la normativa vigente, y las siguientes condiciones:"
    )
    y -= 0.8 * cm

    if petition.type and petition.type.conditions:
        for line in petition.type.conditions.splitlines():
            c.drawString(left_margin + 0.5 * cm, y, f"- {line}")
            y -= 0.4 * cm

    # =========================
    # SIGNATURES
    # =========================
    signature_y = 5 * cm

    c.setFont("Helvetica", 11)
    c.drawString(left_margin, signature_y, "Fdo.: ___________________________")
    c.drawString(left_margin, signature_y - 0.8 * cm, f"{user.first_name} {user.last_name}")

    right_sig_x = width - right_margin - 7 * cm
    c.drawString(right_sig_x, signature_y, "Fdo.: ___________________________")
    c.drawString(
        right_sig_x,
        signature_y - 0.8 * cm,
        "DA - ETSIAE"
    )

    # =========================
    # DATE (LUGAR Y FECHA)
    # =========================
    today = petition.until or timezone.now()

    formatted_today = (
        f"{today.day} de "
        f"{months_es[today.month - 1]} de "
        f"{today.year}"
    )

    c.drawCentredString(
        center_x,
        3.2 * cm,
        f"Madrid, a {formatted_today}"
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

