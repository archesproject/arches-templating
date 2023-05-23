import base64
from io import BytesIO
import re
from tempfile import NamedTemporaryFile
from typing import List, Tuple

from arches_templating.template_engine.template_engine_factory import TemplateEngineFactory
from arches_templating.template_engine.template_tag_type import TemplateTagType
from arches_templating.template_engine.template_engine import TemplateEngine
from arches_templating.template_engine.template_tag import TemplateTag
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

@TemplateEngineFactory.register('xlsx')
class XlsxTemplateEngine(TemplateEngine):

    def extract_regex_matches(self, template) -> List[Tuple]:
        self.workbook = load_workbook(filename = template)
        parsed_tags: List[Tuple] = []
        for sheet in self.workbook.worksheets:
            parsed_tags += self.iterate_over_sheet(sheet)
        return parsed_tags

    def column_from_offset(offset):
        """Convert a numeric offset to the corresponding spreadsheet column.

        Args:
            offset (int): Numeric offset of the column, starting from 1.

        Returns:
            str: The corresponding spreadsheet column.
        """
        if offset <= 0:
            raise ValueError("Offset must be greater than 0")

        column = ""
        while offset > 0:
            offset, remainder = divmod(offset - 1, 26)
            column = chr(65 + remainder) + column

        return column

    def offset_from_column(column:str):
        """Convert a spreadsheet column to the corresponding numeric offset.

        Args:
            column (str): The spreadsheet column, represented as a string of uppercase letters.

        Returns:
            int: The corresponding numeric offset.
        """
        offset = 0
        for i, letter in enumerate(column):
            offset = offset * 26 + (ord(letter) - 64)
        return offset
    
    def increment_column(column:str):
        return XlsxTemplateEngine.column_from_offset(XlsxTemplateEngine.offset_from_column(column) + 1)

    def iterate_over_sheet(self, sheet):
        parsed_tags: List[Tuple] = []
        range_regex = re.compile(r'^([A-Z]+)(\d+):([A-Z]+)(\d+)$')
        dimensions = sheet.dimensions
        match = range_regex.match(dimensions)
        if match:
            start_col = match.group(1) 
            start_row = int(match.group(2)) 
            end_col = match.group(3)  
            end_row = int(match.group(4)) 
            current_row = start_row

            start_col_offset = XlsxTemplateEngine.offset_from_column(start_col)

            end_col_offset = XlsxTemplateEngine.offset_from_column(end_col)

            while current_row <= end_row:
                current_col = start_col_offset
                while current_col <= end_col_offset:
                    current_cell = XlsxTemplateEngine.column_from_offset(current_col) + str(current_row)
                    if sheet[current_cell].value:
                        for match in re.findall(self.regex, sheet[current_cell].value):
                            parsed_tags.append((match, {"cell": sheet[current_cell], "sheet": sheet, "row": current_row,  "column": XlsxTemplateEngine.column_from_offset(current_col)}))
                    current_col += 1
                current_row +=1
        else:
            print("Invalid range format")
        return parsed_tags

    def replace_tags(self, tags:List[TemplateTag], rowshift=0):

        for tag in tags:
            cell = tag.optional_keys['cell']
            sheet = tag.optional_keys['sheet']
            row = tag.optional_keys['row'] + rowshift
            column = tag.optional_keys['column']
            if tag.type == TemplateTagType.CONTEXT:
                if tag.has_rows:
                    column = 0
                    # this is ugly, but way more efficient than the alternative
                    current_row = tag.context_children_template[-1].optional_keys["row"] + rowshift

                    for child in tag.children:
                        if child.type == TemplateTagType.ROWEND:
                            current_row += 1
                            sheet.insert_rows(current_row)
                            rowshift += 1
                        elif child.type == TemplateTagType.VALUE:
                            # grab any borders from the original cell copy them to the new cell.
                            #template_block = tag.context_children_template[column].optional_keys["container"]
                            sheet[child.optional_keys['column'] + str(current_row)].value = child.value
                else:
                    rowshift = self.replace_tags(tag.children, rowshift)

            elif tag.type == TemplateTagType.VALUE:
                cell.value = tag.value
            elif tag.type == TemplateTagType.IMAGE:
                file_name = None
                with NamedTemporaryFile(delete=False) as f:
                    image_data = tag.value.split(",")[1]
                    f.write(base64.b64decode(image_data))
                    f.seek(0)
                    file_name = f.name
                    f.close()
                img = Image(file_name)
                img.anchor = column + str(row)
                cell.value = ""
                sheet.add_image(img, column + str(row))
            elif tag.type == TemplateTagType.IF:
                if tag.render:
                    cell.value = cell.value.replace(tag.raw, "")
                    tag.end_tag.optional_keys['cell'].value = tag.end_tag.optional_keys['cell'].value.replace(tag.end_tag.raw, "")
                    rowshift = self.replace_tags(tag.children, rowshift)
                else:
                    #delete rows between tags
                    if row != tag.end_tag.optional_keys['row'] + rowshift:
                        sheet.delete_rows(row, tag.end_tag.optional_keys['row'] + rowshift)
                        rowshift += row - (tag.end_tag.optional_keys['row'] + rowshift)

                    elif row == tag.end_tag.optional_keys['row'] + rowshift and column != tag.end_tag.optional_keys['column']:
                        current_col = column
                        end_col = tag.end_tag.optional_keys['column']
                        while current_col != end_col:
                            sheet[current_col + str(row)].value = ""
                            current_col = XlsxTemplateEngine.increment_column(current_col)
                    else:
                        cell.value = ""
        
        return (rowshift)

    

    def create_file(self, tags:List[TemplateTag], template):
        bytestream = BytesIO()
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        self.replace_tags(tags)
        self.workbook.save(bytestream)
        return (bytestream, mime, "test.xlsx")