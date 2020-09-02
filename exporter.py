from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime


class CrimpInstructionPDF():
    def __init__(self, outname="test.pdf"):
        self.canvas = canvas.Canvas(outname, pagesize=A4)
        self.canvas.setLineWidth(.3)
        (self.pdf_width, self.pdf_height) = A4
        self.default_font = 'Helvetica'
        self.default_bold = 'Helvetica-Bold'
        self.default_size = 12
        self.border = 40

    def addHeader(self):
        fontsize = 16
        self.canvas.setFont(self.default_bold, fontsize)

        header = 'Crimp-Abzugprobe'
        header_width = stringWidth(header, self.default_font, fontsize)
        self.canvas.drawString((self.pdf_width - header_width) / 2.0,
                               775, header)

        self.canvas.line(self.border, 745,
                         self.pdf_width - self.border, 745)

        self.canvas.drawImage("ewolf.png", self.pdf_width - 150 - self.border,
                              753, height=55, width=160)

    def addCustomer(self):
        fontsize = 11
        start = 700
        self.canvas.setFont(self.default_bold, fontsize)
        line1 = "Knorr-Bremse GmbH"
        line2 = "Division IFE Automatic Door Systems"
        self.canvas.drawString(self.border, start, line1)
        self.canvas.drawString(self.border,
                               start - self.heightOffset(fontsize), line2)

        fontsize = fontsize - 1
        start = start - 2.5 * self.heightOffset(fontsize)
        self.canvas.setFont(self.default_font, fontsize)
        line1 = "33a Straße 1"
        line2 = "A-3331 Kematen/Ybbs"
        line2_date = "Datum: {0}".format(datetime.now().strftime("%d.%m.%Y"))
        self.canvas.drawString(self.border, start, line1)
        self.canvas.drawString(self.border,
                               start - self.heightOffset(fontsize), line2)

        text_width = stringWidth(line2_date, self.default_font, fontsize)
        self.canvas.drawString(self.pdf_width - self.border - text_width,
                               start - self.heightOffset(fontsize), line2_date)

        start = start - 1.5 * self.heightOffset(fontsize)
        self.canvas.line(self.border, start,
                         self.pdf_width - self.border, start)

        description = "KUNDE"
        fontsize = fontsize - 1
        self.canvas.setFont(self.default_font, fontsize)
        self.canvas.drawString(self.border,
                               start - self.heightOffset(fontsize),
                               description)

    def drawInformation(self, order=[]):
        start = 530
        data = [['Bestellnummer:', '5000017911-I78'],
                ["Auftragsnummer:", "46207764"],
                ["Belegnummer:", "1862020"],
                ["Protokollnummer:", "CA1862020"],
                ["Zeichnungsnummer:", "ED002020R15"]]
        f = Table(data, None, 16)
        f.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                               ('ALIGN', (1, 0), (1, -1), 'RIGHT')]))

        f.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        f.drawOn(self.canvas, self.border, start)

    def drawHeader(self, start):
        header = [["Draht", "Pos.", "Gehäuse", "Crimpung",
                   "Quersch.", "Einsatz", "Zange", "Wert"]]

        colspacing = [35, 32, 55, 100, 50, 85, 85, 65]
        h = Table(header, colspacing, 16)

        style = [('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
                 ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, 1), 1.5, colors.black),
                 ('LINEAFTER', (0, 0), (-1, 1), 0.5, colors.black),
                 ('LINEAFTER', (-1, 0), (-1, 1), 1.5, colors.black),
                 ('ALIGN', (0, 0), (-1, 0), 'CENTER')]
        h.setStyle(TableStyle(style))

        h.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        h.drawOn(self.canvas, self.border, start)

    def drawSubHeader(self, start):
        start = start - 16

        subheader = [["", "", "Bezeichnung", "Type", u"mm²", u"mm²",
                      "AWG", "Fabrikat", "Nummer", "Soll", "Ist"]]

        colspacing = [35, 32, 55, 100, 50, 42.5, 42.5, 42.5, 42.5, 32.5, 32.5]
        sh = Table(subheader, colspacing, 16)

        style = [('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
                 ('FONTSIZE', (0, 0), (-1, 0), 8),
                 ('LINEAFTER', (-1, 0), (-1, 1), 1.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, 1), 1.5, colors.black),
                 ('ALIGN', (0, 0), (-1, 0), 'CENTER')]
        for col in [0, 1, 2, 3, 4, 6, 8, 10]:
            style.append(('LINEAFTER', (col, 0), (col, 1), 0.5, colors.black))

        sh.setStyle(TableStyle(style))

        sh.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        sh.drawOn(self.canvas, self.border, start)

    def drawInstruction(self, start, rows=20):
        start = start - (rows + 1) * 16

        data = []
        for i in range(rows):
            data.append([""] * 11)
        data[0] = ["1"] * 11

        colspacing = [35, 32, 55, 100, 50, 42.5, 42.5, 42.5, 42.5, 32.5, 32.5]
        t = Table(data, colspacing, 16)

        style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                 ('FONTSIZE', (0, 0), (-1, 0), 8),
                 ('LINEAFTER', (-1, 0), (-1, -1), 1.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, -1), 1.5, colors.black),
                 ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
                 ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                 ('VALIGN', (0, 0), (-1, 0), 'MIDDLE')]

        t.setStyle(TableStyle(style))

        t.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        t.drawOn(self.canvas, self.border, start)

    def heightOffset(self, fontsize):
        return fontsize + fontsize * 0.2

    def createPDF(self, order=[]):
        self.addHeader()
        self.addCustomer()
        self.drawInformation(order=order)

        start = 500
        self.drawHeader(start)
        self.drawSubHeader(start)
        self.drawInstruction(start)
        self.canvas.save()


def main():
    pdf = CrimpInstructionPDF()
    pdf.createPDF()


if __name__ == '__main__':
    main()
