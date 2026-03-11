from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_pdf(title, content):

    folder = "generated_books"

    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = f"{folder}/{title}.pdf"

    c = canvas.Canvas(file_path, pagesize=letter)

    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)

    text.textLine(title)
    text.textLine("")

    for line in content.split("\n"):
        text.textLine(line)

    c.drawText(text)
    c.save()

    return file_path