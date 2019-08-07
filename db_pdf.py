#!/usr/bin/env python
# -*- coding:utf-8 -*-

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape, portrait     # letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase import pdfmetrics, ttfonts

myFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
pdfmetrics.registerFont(myFontObject)
 
head = ('Номер', 'Дата время', 'Широта', 'Долгота', 'Глубина м', 'Коментарий')
 
style = TableStyle([#('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.red),
                    #('VALIGN', (0, 0), (0, -1), 'TOP'),
                    ('TEXTCOLOR', (0, 1), (0, -1), colors.blue),
                    ('TEXTCOLOR', (-1, 1), (-1, -1), colors.green),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (-1, 1), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Arial'),])
 
def _go_data(result):
    data = []
    data.append(head)
    for res in result:
        coment = res[-1]
        res = (res[0], res[1], res[2], res[3], res[4], parse_res(coment, 30))
        data.append(res)
    return data

def go_pdf(result):
    doc = SimpleDocTemplate("db_op.pdf", pagesize=A4, rightMargin=15,
                            leftMargin=20, topMargin=15, bottomMargin=18)
    # doc.pagesize = landscape(A4)
    doc.pagesize = portrait(A4)
    elements = []
    data = _go_data(result)
    t=Table(data)
    t.setStyle(style)
    elements.append(t)
    doc.build(elements)

def parse_res(res, max):
    l = []
    for i in res.split('\n'):
        if len(i) <= max:
            l.append(i + '\n')
            continue
        while 1:
            i, j = i[ : max], i[max : ]
            l.append(i + '\n')
            if not j:
                break
            else:
                i = j
    return ''.join(l)
