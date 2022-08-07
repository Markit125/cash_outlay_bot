from decimal import Decimal

from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.table.flexible_column_width_table import (
    FlexibleColumnWidthTable,
)
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.font.font import Font
from pathlib import Path


def make_report_in_PDF(id, notes, from_data, to_date):
    doc: Document = Document()
    page: Page = Page()
    doc.add_page(page)
    layout: PageLayout = SingleColumnLayout(page)
    
    font_path: Path = Path(__file__).parent / "Font.ttf"
    custom_font: Font = TrueTypeFont.true_type_font_from_file(font_path)

    text = f'Отчёт с {from_data} до {to_date}.'
    layout.add(Paragraph(text, font=custom_font, horizontal_alignment=Alignment.CENTERED))

    table = FlexibleColumnWidthTable(number_of_columns=6, number_of_rows=len(notes)+3, horizontal_alignment=Alignment.CENTERED)
    table.add(
        TableCell(Paragraph("№", font=custom_font), background_color=X11Color("SlateGray"))
    ).add(
        TableCell(Paragraph("Название", font=custom_font), background_color=X11Color("SlateGray"))
    ).add(
        TableCell(Paragraph("Количество", font=custom_font), background_color=X11Color("SlateGray"))
    ).add(
        TableCell(Paragraph("Цена", font=custom_font), background_color=X11Color("SlateGray"))
    ).add(
        TableCell(Paragraph("Теги", font=custom_font), background_color=X11Color("SlateGray"))
    ).add(
        TableCell(Paragraph("Дата", font=custom_font), background_color=X11Color("SlateGray")
    ))
    all_sum = 0
    for i in range(len(notes)):
        table.add(Paragraph(f"{i + 1}", font=custom_font)
        ).add(Paragraph(f"{notes[i]['name']}", font=custom_font)
        ).add(Paragraph(f"{notes[i]['count']}", font=custom_font)
        ).add(Paragraph(f"{notes[i]['price']}", font=custom_font)
        ).add(Paragraph(f"{notes[i]['tag'].replace('.', ', ')}", font=custom_font)
        ).add(Paragraph(f"{notes[i]['date']}", font=custom_font))
        all_sum += float(notes[i]['price'][:-2].replace(",", "."))
    
    table.add(
        TableCell(
            Paragraph(" "),
            col_span=6,
            border_right=False,
            border_left=False
        )
    )
    table.add(TableCell(
        Paragraph("Итого", font=custom_font, horizontal_alignment=Alignment.RIGHT), col_span=5)
    ).add(Paragraph(f"{all_sum}{notes[0]['price'][-2:]}", font=custom_font))
    
    table.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(4), Decimal(4))
    layout.add(table)
    
    with open(f"{id}.pdf", "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)
