from typing import Optional

from django.db.models import Q


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

