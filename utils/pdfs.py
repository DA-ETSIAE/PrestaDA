from typing import Optional

from django.db.models import Q
from reportlab.lib import colors
from reportlab.lib.colors import Color, HexColor, black, gray
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from configuracion.models import Configuration
from gestor.models import Petition, Type
from usuarios.models import User
from utils.crypto import generate_hash


def generate_invoice(response, petition: Petition):
    status = petition.status
    date = petition.until
    item_code = petition.item.code if petition.item else ""
    tipo = petition.type.name

    user = petition.user
    full_name = petition.user.username
    dni = user.dni or ""
    email = user.email or ""
    phone = user.phone or ""

    conditions = petition.type.conditions

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    c.setTitle(Configuration.objects.get(node='agreement_title').value)

    # Header background
    c.setFillColor(HexColor('#f0f0f0'))
    c.rect(0, height - 3 * cm, width, 3 * cm, fill=1, stroke=0)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(
        width / 2,
        height - 2 * cm,
        Configuration.objects.get(node='agreement_header').value
    )

    c.setFont("Helvetica", 14)
    c.drawCentredString(
        width / 2,
        height - 2.8 * cm,
        Configuration.objects.get(node='org').value
    )

    y_position = height - 5 * cm

    # Taquilla (Item Code)
    if item_code:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y_position, f"Taquilla: {item_code}")
        y_position -= 1 * cm

    # Object
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y_position, "Objeto:")
    c.setFont("Helvetica", 12)
    c.drawString(4 * cm, y_position, tipo)
    y_position -= 1 * cm

    # Arrendatario Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y_position, "Arrendatario:")
    y_position -= 0.8 * cm

    c.setFont("Helvetica", 12)
    c.drawString(2.5 * cm, y_position, f"D/Dña {full_name}")
    y_position -= 0.8 * cm

    c.drawString(2.5 * cm, y_position, f"con DNI número {dni}")
    y_position -= 0.8 * cm

    c.drawString(2.5 * cm, y_position, f"email {email}")
    y_position -= 0.8 * cm

    c.drawString(2.5 * cm, y_position, f"número de contacto {phone}")
    y_position -= 1.2 * cm

    # End Date
    if date:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y_position, "Hasta:")
        c.setFont("Helvetica", 12)
        c.drawString(4 * cm, y_position, date.strftime("%d-%m-%Y"))
        y_position -= 1 * cm

    # Conditions
    if conditions:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y_position, "Condiciones:")
        y_position -= 0.8 * cm

        c.setFont("Helvetica", 12)
        text_obj = c.beginText(2 * cm, y_position)
        text_obj.setLeading(14)

        for line in conditions.splitlines():
            text_obj.textLine(line)

        c.drawText(text_obj)

    # Signature Section
    if status == Petition.Status.ACTIVE:
        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, 4 * cm, f"Firmado por D/Dña {full_name} con DNI {dni}")

        c.drawString(
            2 * cm,
            3 * cm,
            f"Firmado por {Configuration.objects.get(node='org').value}"
        )

        c.setFont("Courier-Bold", 10)
        c.drawString(
            2 * cm,
            2.5 * cm,
            f"{petition.id}-{generate_hash(dni, petition.id)}"
        )
    else:
        watermark_text = "NO VÁLIDA"
        c.saveState()
        c.setFont("Helvetica-Bold", 60)
        c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.3))
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, watermark_text)
        c.restoreState()

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

