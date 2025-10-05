import re
from typing import List

class ConstructorTranslator:
    def translate_constructor(self, class_name: str, python_lines: List[str], constructor_line: str):
        field_lines = []
        for i, line in enumerate(python_lines):
            if re.match(r'\s*self\.\w+:.*= None', line):
                field_lines.append((i, line.strip()))

        if not field_lines:
            return

        class_index = next((i for i, l in enumerate(python_lines) if l.strip().startswith("class " + class_name)), -1)
        if class_index == -1:
            return

        # delete old fields
        for idx, _ in sorted(field_lines, reverse=True):
            del python_lines[idx]

        # create constructor and add params
        fields_list = []
        init_line = self._translate_constructor_line(constructor_line, fields_list)
        python_lines.insert(class_index + 1, init_line)
        init_index = class_index

        # insert fields into constructor
        insert_pos = init_index + 2
        for _, field in field_lines:
            index = next((i for i, name_field in enumerate(fields_list) if name_field in field), -1)
            if index != -1:
                field = field.replace('None', fields_list[index])
            python_lines.insert(insert_pos, "        " + field)
            insert_pos += 1

    def _translate_constructor_line(self, line:str, fields_list: List[str]) -> str:
        match = re.search(r'\((.*?)\)', line)
        params = match.group(1).strip() if match else ""

        if params:
            parts = []
            for p in params.split(','):
                p = p.strip()
                if not p:
                    continue
                p = p.replace("string", "str")
                p = p.replace("int", "int")
                p = p.replace("float", "float")
                p = p.replace("double", "float")
                p = p.replace("bool", "bool")
                p = p.replace("char", "str")
                parts.append(p.split()[-1])
                fields_list.append(p.split()[-1])
            python_params = "self, " + ", ".join(parts)
        else:
            python_params = "self"

        return f"    def __init__({python_params}):"
