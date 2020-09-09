import subprocess
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from datetime import datetime


class CrimpInstructionPDF():
    def __init__(self, basedir, outfile="test.pdf"):
        self.outfile = outfile
        outpath = os.path.join(self.getOutdir(basedir), outfile)
        self.canvas = canvas.Canvas(outpath, pagesize=A4)
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

    def drawInformation(self, order_information=[]):
        start = 530
        data = [['Bestellnummer:', ''],
                ["Auftragsnummer:", ""],
                ["Belegnummer:", ""],
                ["Protokollnummer:", ""],
                ["Zeichnungsnummer:", "ED002020R15"]]
        if order_information:
            for i, entry in enumerate(order_information):
                data[i][1] = entry

        f = Table(data, None, 16)
        f.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                               ('ALIGN', (1, 0), (1, -1), 'RIGHT')]))

        f.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        f.drawOn(self.canvas, self.border, start)

    def drawHeader(self, start):
        header = [["Draht", "Pos.", "Gehäuse", "Crimpung",
                   "Quersch.", "Einsatz", "Zange", "Wert"]]

        colspacing = [35, 32, 55, 100, 50, 75, 105, 55]
        h = Table(header, colspacing, 16)

        style = [('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
                 ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, 1), 1.5, colors.black),
                 ('LINEAFTER', (0, 0), (-1, 1), 0.5, colors.black),
                 ('LINEAFTER', (-1, 0), (-1, 1), 1.5, colors.black),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER')]
        h.setStyle(TableStyle(style))

        h.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        h.drawOn(self.canvas, self.border, start)

    def drawSubHeader(self, start):
        start = start - 16

        subheader = [["", "", "Bezeichnung", "Type", u"mm²", "AWG",
                     u"mm²", "Fabrikat", "Nummer", "Soll", "Ist"]]

        colspacing = [35, 32, 55, 100, 50, 37.5, 37.5, 47.5, 57.5, 27.5, 27.5]
        sh = Table(subheader, colspacing, 16)

        style = [('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
                 ('FONTSIZE', (0, 0), (-1, 0), 8),
                 ('LINEAFTER', (-1, 0), (-1, 1), 1.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, 1), 1.5, colors.black),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER')]
        for col in [0, 1, 2, 3, 4, 6, 8, 10]:
            style.append(('LINEAFTER', (col, 0), (col, 1), 0.5, colors.black))

        sh.setStyle(TableStyle(style))

        sh.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        sh.drawOn(self.canvas, self.border, start)

    def drawInstruction(self, start, instructions=[], rows=20):
        start = start - (rows * 19) - 16

        colspacing = [35, 32, 55, 100, 50, 37.5, 37.5, 47.5, 57.5, 27.5, 27.5]
        data = self.unrollInstructions(instructions, colspacing)

        for i in range(rows - len(instructions)):
            data.append([""] * 11)

        t = Table(data, colspacing, 19)

        style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('LINEAFTER', (-1, 0), (-1, -1), 1.5, colors.black),
                 ('LINEBEFORE', (0, 0), (0, -1), 1.5, colors.black),
                 ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0)]

        t.setStyle(TableStyle(style))

        t.wrapOn(self.canvas, self.pdf_width, self.pdf_height)
        t.drawOn(self.canvas, self.border, start)

    def unrollInstructions(self, instructions, colspacing):
        table = []

        for i, instruction in enumerate(instructions.keys()):
            xs, contact = instruction.split("#")
            pos = instructions[instruction]["pos"]
            name = instructions[instruction]["name"]
            IDs = ", ".join(instructions[instruction]["IDs"])
            slot = instructions[instruction]["slot"]
            soll = instructions[instruction]["soll"]
            producer = instructions[instruction]["producer"]
            tmpRow = [i, pos, name, contact, xs,
                      slot[0], slot[1],
                      producer, IDs, soll, ""]
            table.append(applyStyle(tmpRow, self.default_font, colspacing))
        return table

    def heightOffset(self, fontsize):
        return fontsize + fontsize * 0.2

    def createPDF(self, order_information=[], instructions=[]):
        self.addHeader()
        self.addCustomer()
        self.drawInformation(order_information=order_information)

        start = 500
        self.drawHeader(start)
        self.drawSubHeader(start)
        self.drawInstruction(start, instructions=instructions)
        self.canvas.save()

        startpath = os.path.join("data", "tmp", self.outfile)
        if sys.platform.startswith("win32"):
            subprocess.call('start ' + startpath, shell=True)
        else:
            subprocess.run(['open', startpath], check=True)

    def getOutdir(self, basedir):
        outdir = os.path.join(basedir, "data", "tmp")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return outdir


def applyStyle(row, font, colspacing):
    tmpRow = []
    for i, cell in enumerate(row):
        for fontsize in [8, 7, 6, 5]:
            lines = simpleSplit(str(cell), font, fontsize, colspacing[i])

            if len(lines) < 3 and ((len(lines) * fontsize * 1.2)) < 19:
                style = ParagraphStyle(name='normal',
                                       alignment=1,
                                       leading=fontsize,
                                       # leftIndent=0,
                                       # borderPadding=0,
                                       # rightIndent=0,
                                       # spaceBefore=0,
                                       # spaceAfter=0,
                                       wordWrap=None,
                                       fontSize=fontsize)
                break
        tmpRow.append(Paragraph(str(cell), style))
    return tmpRow


def main():
    pdf = CrimpInstructionPDF()
    instructions = {"1#ML / 3ED10025234R51":{"pos":"3","name":"4","IDs":["Z123456","Z789012","Z987654","Z456987"],"slot":["","10-16"],"soll":"8"},
                    "1#3ED10025234R51 / 3ED10025234R51":{"pos":"3","name":"4","IDs":["Z123456","Z789012","Z987654"],"slot":["22-20",""],"soll":"8"},
                    "1#MNL / 3ED10025234R53":{"pos":"3","name":"4","IDs":["Z123456","Z789012"],"slot":["22-20","10-16"],"soll":"8"},
                    "1#3ED10025234R54":{"pos":"3","name":"4","IDs":["Z123456"],"slot":["22-20","1.50 - 1.60"],"soll":"8"}}
    pdf.createPDF(instructions=instructions)


if __name__ == '__main__':
    main()
