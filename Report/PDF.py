from ctypes import alignment
from decimal import Decimal
from math import remainder
import re

from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.table.flexible_column_width_table import (
    FlexibleColumnWidthTable,
)
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable

from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.font.font import Font
from pathlib import Path


def table_header(custom_font, count_of_notes):
    table = FlexibleColumnWidthTable(number_of_columns=6, number_of_rows=count_of_notes+1, horizontal_alignment=Alignment.CENTERED)
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
    return table


def count_of_next_list_notes(notes_on_a_page, remaind_notes):
    if notes_on_a_page < remaind_notes + 2:
        return min(notes_on_a_page, remaind_notes)
    
    if remaind_notes < notes_on_a_page - 1:
        return remaind_notes + 2
    print(remaind_notes, notes_on_a_page)


def make_report_in_PDF(id, notes, from_data, to_date):
    notes_on_a_page = 17

    doc: Document = Document()
    
    font_path: Path = Path(__file__).parent / "Font.ttf"
    custom_font: Font = TrueTypeFont.true_type_font_from_file(font_path)


    page_number = 1
    all_sum = 0
    remaind_notes = len(notes)

    if remaind_notes > 15:
        text = f'Report from {from_data} to {to_date}. Page {page_number}.\n'
    else:
        text = f'Report from {from_data} to {to_date}.\n'

    page: Page = Page()
    doc.add_page(page)
    layout: PageLayout = SingleColumnLayout(page)

    layout.add(Paragraph(text, font=custom_font, horizontal_alignment=Alignment.CENTERED))

    # table = table_header(custom_font, len(notes))
    table = table_header(custom_font, count_of_next_list_notes(notes_on_a_page, remaind_notes))
    
    i = 0
    remainder = 0
    while remaind_notes > 0:

        remainder = notes_on_a_page - remaind_notes
        for _ in range(min(notes_on_a_page, remaind_notes)):
            table.add(Paragraph(f"{i + 1}", font=custom_font)
            ).add(Paragraph(f"{notes[i]['name']}", font=custom_font)
            ).add(Paragraph(f"{notes[i]['count']}", font=custom_font)
            ).add(Paragraph(f"{notes[i]['price']}", font=custom_font)
            ).add(Paragraph(f"{notes[i]['tag'].replace('.', ', ')}", font=custom_font)
            ).add(Paragraph(f"{notes[i]['date']}", font=custom_font))
            all_sum += float(notes[i]['price'][:-2].replace(",", "."))
        
            print(f"{notes[i]['name']} {notes[i]['count']} {notes[i]['price']} {notes[i]['tag'].replace('.', ', ')}")
            print(remaind_notes)
            remaind_notes -= 1
            i += 1

        if remainder < 2:
            page_number += 1

            table.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(4), Decimal(4))
            layout.add(table)
            page: Page = Page()
            doc.add_page(page)
            layout: PageLayout = SingleColumnLayout(page)
            text = f'Report from {from_data} to {to_date}. Page {page_number}\n'
            layout.add(Paragraph(text, font=custom_font, horizontal_alignment=Alignment.CENTERED))
            if remaind_notes == 0:
                table = FlexibleColumnWidthTable(number_of_columns=6, number_of_rows=2, horizontal_alignment=Alignment.CENTERED)
            else:
                table = table_header(custom_font, count_of_next_list_notes(notes_on_a_page, remaind_notes))


    table.add(
        TableCell(
            Paragraph(" "),
            col_span=6,
            border_right=False,
            border_left=False,
            border_top=False
        )
    )

    table.add(TableCell(
        Paragraph("Итого", font=custom_font, horizontal_alignment=Alignment.RIGHT), col_span=5)
    ).add(Paragraph(f"{all_sum}{notes[0]['price'][-2:]}", font=custom_font))
    
    table.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(4), Decimal(4))
    layout.add(table)


    with open(f"{id}.pdf", "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)


def main():
    
    counts = [15, 16, 17, 18, 29, 33, 34, 35]
    for j in counts:
        notes = [
        {
            'name': 'giant',
            'count': f'{i}',
            'price': f'{float(i * 10)} P',
            'tag': f'aaa{10 * ".dcdc"}', 
            'date': '22.07.22'
        } for i in range(1, j + 1)
    ]
        make_report_in_PDF(f'{j}', notes, '21.07.22', '23.07.22')


if __name__ == '__main__':
    main()