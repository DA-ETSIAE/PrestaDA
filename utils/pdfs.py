from typing import Optional

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
    pending = petition.is_pending
    active = petition.is_active
    date = petition.until
    item = petition.item.code if petition.item else None
    tipo = petition.type.name
    name = petition.user.username
    dni = petition.user.dni
    conditions = petition.type.conditions


    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    c.setTitle(Configuration.objects.get(node='agreement_title').value)

    c.setFillColor(HexColor('#f0f0f0'))
    c.rect(0, height - 3 * cm, width, 3 * cm, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 2*cm, Configuration.objects.get(node='agreement_header').value)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 2.8*cm, Configuration.objects.get(node='org').value)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 5 * cm, "Nombre: ")
    c.setFont("Helvetica", 12)
    c.drawString(5 * cm, height - 5 * cm, name)


    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 6.5 * cm, "Objeto:")
    c.setFont("Helvetica", 12)
    c.drawString(5 * cm, height - 6.5 * cm, tipo)

    if item:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 7 * cm, "Código:")
        c.setFont("Helvetica", 12)
        c.drawString(5 * cm, height - 7 * cm, item)

    if date:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 8 * cm, "Hasta:")
        c.setFont("Helvetica", 12)
        c.drawString(5 * cm, height - 8 * cm, date.strftime("%d-%m-%Y"))

    if conditions:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, height - 9.5*cm, "Condiciones:")
        c.setFont("Helvetica", 12)
        text_obj = c.beginText(2*cm, height - 10.5*cm)
        text_obj.setLeading(12)
        for line in conditions.splitlines():
            text_obj.textLine(line)
        c.drawText(text_obj)

    if not pending and active:
        c.setFont("Helvetica", 12)
        c.drawString(1.2*cm, 5*cm, "Firmado por " + name + " con DNI " + dni + ":")

        c.setFont("Helvetica", 12)
        c.drawString(1.2 * cm, 2 * cm + 1 * cm, "Firmado por " + Configuration.objects.get(node='org').value + ":")
        c.setFont("Courier-Bold", 12)
        c.drawString(1.2 * cm, 2 * cm - 1 * cm, str(petition.id) + "-" + generate_hash(dni, petition.id))
        c.setFont("Courier-Bold", 12)

    if pending or not active:
        watermark_text = "PENDIENTE" if pending else "NO VÁLIDA"
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
        name = petition.user.username
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

