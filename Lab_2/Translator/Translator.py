import re
from typing import Optional, Union, List
from .UsingTranslator import UsingTranslator
from .NamespaceTranslator import NamespaceTranslator
from .ClassTranslator import ClassTranslator
from .PropertyTranslator import PropertyTranslator
from .MethodTranslator import MethodTranslator
from .FieldTranslator import FieldTranslator
from .MainClassTranslator import MainClassTranslator

class Translator:
    def __init__(self):
        self.imports = set()
        self.current_class = None
        self.current_method = None
        self.context = 'global'  # 'global', 'namespace', 'class', 'method', 'main'

        self.context_stack: List[str] = []
        self.nested_block_count: int = 0

        self.pending_open: bool = False
        self.pending_prev_context: Optional[str] = None

        # translators
        self.Using = UsingTranslator()
        self.Namespace = NamespaceTranslator()
        self.Class = ClassTranslator()
        self.Property = PropertyTranslator()
        self.Method = MethodTranslator()
        self.Field = FieldTranslator()
        self.Main = MainClassTranslator()

        self.collecting_main: bool = False
        self.main_body_lines: List[str] = []

    def translate(self, code: str) -> list:
        self.imports.clear()
        self.context_stack = []
        self.nested_block_count = 0
        self.context = 'global'
        self.pending_open = False
        self.pending_prev_context = None

        self.collecting_main = False
        self.main_body_lines = []
        self.Main.uses_args = False

        # import required imports
        required_imports = self.Using.get_required_imports()
        for s in required_imports:
            self.imports.add(s)

        lines = code.split('\n')
        python_lines = []
        i = 0

        while i < len(lines):
            raw_line = lines[i].rstrip('\n')
            line = raw_line.strip()

            prev_context = self.context

            translated_line = self.translate_line(line)

            if translated_line:
                if self.collecting_main:
                    # store translated main body (no top-level indent here)
                    self.main_body_lines.append(translated_line)
                else:
                    python_lines.append(self._get_indent() + translated_line)

            self._handle_braces(line, prev_context)

            if self.collecting_main and prev_context == 'main' and self.context != 'main':
                if self.Main.uses_args:
                    self.imports.add('import sys')

                python_lines.append('if __name__ == "__main__":')
                for ml in self.main_body_lines:
                    python_lines.append('    ' + ml)

                self.collecting_main = False
                self.main_body_lines = []
                self.Main.uses_args = False

            i += 1

        return python_lines

    def _handle_braces(self, line: str, prev_context: str):
        if not line:
            return

        if '{' in line and '}' in line and (('get;' in line) or ('set;' in line) or '=>' in line):
            return

        open_count = line.count('{')
        close_count = line.count('}')

        if self.pending_open:
            if open_count > 0:
                self.context_stack.append(self.pending_prev_context)
                self.pending_open = False
                self.pending_prev_context = None
                open_count -= 1
            else:
                return

        if self.context != prev_context:
            if open_count > 0:
                self.context_stack.append(prev_context)
                open_count -= 1
            else:
                self.pending_open = True
                self.pending_prev_context = prev_context
                return

        if open_count > 0:
            self.nested_block_count += open_count

        if close_count > 0:
            if close_count <= self.nested_block_count:
                self.nested_block_count -= close_count
                close_count = 0
            else:
                close_count -= self.nested_block_count
                self.nested_block_count = 0

            last_popped = None
            pop_times = min(close_count, len(self.context_stack))
            for _ in range(pop_times):
                last_popped = self.context_stack.pop()
            if last_popped is not None:
                self.context = last_popped

    def _get_indent(self) -> str:
        total_levels = len(self.context_stack) + self.nested_block_count
        return '    ' * total_levels

    def translate_line(self, line: str) -> str:
        if not line or line.startswith('//'):
            return ""

        if self.context == 'global':
            return self._translate_global_scope(line)
        elif self.context == 'namespace':
            return self._translate_namespace_scope(line)
        elif self.context == 'class':
            return self._translate_class_scope(line)
        elif self.context == 'method':
            return self._translate_method_scope(line)
        elif self.context == 'main':
            return self._translate_main_scope(line)

        return ""

    def _translate_global_scope(self, line: str) -> str:
        if line.startswith('using ') and line.endswith(';'):
            return self.Using.translate_using(line)
        elif line.startswith('namespace '):
            self.context = 'namespace'
            return self.Namespace.translate_namespace(line)
        return ""

    def _translate_namespace_scope(self, line: str) -> str:
        # namespace сам по себе не содержит main — main внутри класса
        if ' class ' in line:
            self.context = 'class'
            class_name = self._extract_class_name(line)
            self.current_class = class_name
            return self.Class.translate_class(line)
        elif line.startswith('using '):
            return self.Using.translate_using(line)
        return ""

    def _translate_class_scope(self, line: str) -> str:
        # если это объявление метода Main — переключаемся в collecting_main режим
        if self.Main.is_main_declaration(line):
            # пометим, если передан args
            if self.Main.has_args(line):
                self.Main.uses_args = True
            # перевод заголовка main не выводим сейчас — соберём тело и вставим позже
            self.context = 'main'
            self.current_method = 'Main'
            self.collecting_main = True
            return ""  # не выводим саму сигнатуру

        # стандартная логика для других методов/свойств
        if line.startswith('public ') or line.startswith('private ') or line.startswith('protected '):
            if '(' in line and ')' in line and not line.endswith(';'):
                if self._is_constructor(line):
                    return ""
                else:
                    self.context = 'method'
                    method_name = self._extract_method_name(line)
                    self.current_method = method_name
                    return self.Method.translate_method(line)
            elif ' get; ' in line or ' set; ' in line or '=>' in line or '{ get;' in line:
                return self.Property.translate_property(line)
        elif line.startswith('['):
            return f"# Attribute: {line}"
        return ""

    def _translate_method_scope(self, line: str) -> str:
        # возвращение обрабатываем через Method translator
        if 'return' in line:
            return self.Method.translate_return(line)

        # обычные замены в методах
        if 'Console.WriteLine' in line:
            return line.replace('Console.WriteLine', 'print')
        elif 'Console.Write' in line:
            return line.replace('Console.Write', 'print')

        return f"# {line}"

    def _translate_main_scope(self, line: str) -> str:
        if line.strip() in ("{", "}"):
            return ""
        if 'Console.WriteLine' in line:
            return line.replace("Console.WriteLine", "print")
        if 'Console.Write' in line:
            return line.replace("Console.Write", "print")
        if 'var' in line:
            return self.Field.translate_using(line)
        if 'return ' in line:
            return self.Method.translate_return(line)
        return line

    def _extract_class_name(self, line: str) -> str:
        match = re.search(r'class\s+([A-Za-z_]\w*)', line)
        return match.group(1) if match else "UnknownClass"

    def _extract_method_name(self, line: str) -> str:
        idx = line.find('(')
        if idx == -1:
            return "unknown_method"
        before = line[:idx].strip()
        parts = before.split()
        return parts[-1] if parts else "unknown_method"

    def _is_constructor(self, line: str) -> bool:
        if not self.current_class:
            return False
        name = self._extract_method_name(line)
        return name == self.current_class

    def save_translation(self, python_lines: List[str], output_path: str):
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                for imp in sorted(self.imports):
                    file.write(imp + '\n')
                file.write('\n')

                for line in python_lines:
                    file.write(line + '\n')

            print(f"Translation saved to: {output_path}")
        except Exception as e:
            print(f"Error saving translation: {e}")

    def delete_comments(self, python_lines: List[str]) -> List[str]:
        cleaned = []
        for line in python_lines:
            stripped = line.strip()

            if stripped.startswith("#"):
                continue

            new_line = ""
            in_string = False
            for i, ch in enumerate(line):
                if ch in ('"', "'"):
                    in_string = not in_string
                if ch == "#" and not in_string:
                    new_line = line[:i].rstrip()
                    break
            else:
                new_line = line.rstrip()

            if new_line:
                cleaned.append(new_line)

        return cleaned

    @staticmethod
    def convert_cs_to_str(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"Convert: File converted in dir: {file_path}")
            return content
        except FileNotFoundError:
            print(f"Error: File {file_path} not found!")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""
