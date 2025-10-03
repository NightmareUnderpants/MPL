class NamespaceTranslator:

    def translate_namespace(self, line: str) -> str:
        if line.startswith('namespace '):
            namespace = line[10:].replace('{', '').strip()

            return f"# Namespace: {namespace}"