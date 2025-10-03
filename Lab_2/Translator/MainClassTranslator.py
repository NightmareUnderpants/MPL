import re

class MainClassTranslator:
    def __init__(self):
        self.uses_args = False

    def is_main_declaration(self, line: str) -> bool:
        return bool(re.search(r'\bstatic\s+(?:void|int)\s+Main\s*\(', line))

    def has_args(self, line: str) -> bool:
        return bool(re.search(r'\bstring\s*\[\]\s*\w+', line))

    def translate_declaration(self, line: str) -> str:
        if self.has_args(line):
            self.uses_args = True
        return ""