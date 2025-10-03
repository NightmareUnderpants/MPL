import re

class ClassTranslator:

    def __init__(self):
        self.current_class = ''

    def translate_class(self, line: str) -> str:
        if ' class ' in line:
            class_info = self._parse_class_declaration(line)

            class_name = class_info['name']
            self.current_class = class_name

            if class_name == "Program":
                return ""

            python_code = self._generate_python_code(class_info);
            return python_code

    def _parse_main_class(self, line: str) -> str:
        return "if __name__ == \"__main__\":"

    def _parse_class_declaration(self, line: str) -> dict:
        class_info = {
            'name' : '',
            'modifiers': [],
            'base_class': '',
            'is_public': False
        }

        if 'public ' in line:
            class_info['is_public'] = True
            class_info['modifiers'].append('public')

        class_match = re.search(r'class\s+(\w+)', line)
        if class_match:
            class_info['name'] = class_match.group(1)

        return class_info

    def _generate_python_code(self, class_info: dict) -> str:
        lines = []

        lines.append(f"class {class_info['name']}:")

        if class_info['base_class']:
            inheritance = []
            if class_info['base_class']:
                inheritance.append(class_info['base_class'])

            lines.append(f'    """Inherits from: {", ".join(inheritance)}"""')
        else:
            lines.append('    """C# class translated to Python"""')

        lines.append("")
        return "\n".join(lines)