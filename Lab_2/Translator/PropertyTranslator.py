import re
from .TypeMapper import TypeMapper


class PropertyTranslator:
    def translate_property(self, line: str) -> str:
        if 'get;' in line and 'set;' in line:
            return self._translate_fully_property(line)

    def _translate_fully_property(self, line: str) -> str:
        match = re.search(r'public\s+(\w+)\s+(\w+)\s*{\s*get;\s*set;\s*}', line)
        if match:
            type_name, prop_name = match.groups()
            python_type = TypeMapper.map_type(type_name)
            return f"self.{prop_name.lower()}: {python_type} = None"