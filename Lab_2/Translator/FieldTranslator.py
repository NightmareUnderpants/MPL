class FieldTranslator:
    def translate_using(self, line: str) -> str:
        line = line.strip()

        if not line:
            return ""

        if line.startswith("var "):
            line = line.replace("var ", "", 1)

        if 'new' in line:
            line = line.replace('new ', "", 1)

        if line.endswith(";"):
            line = line[:-1]

        return line