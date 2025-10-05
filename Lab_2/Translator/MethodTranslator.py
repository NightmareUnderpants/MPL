import re
from .TypeMapper import TypeMapper

class MethodTranslator:
    def translate_method(self, line: str) -> str:
        match = re.search(r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)', line)
        if match:
            return_type, method_name, params = match.groups()

            python_return = self._map_return_type(return_type)
            python_params = self._translate_parameters(params)

            return f"def {method_name}(self, {python_params}) -> {python_return}:"

        return f"# Method: {line}"

    def translate_return(self, line: str) -> str:
        expr = line.strip().removeprefix("return").rstrip(";").strip()

        # if is: return $"...";
        if expr.startswith('$"') or expr.startswith("$'"):
            expr = "f" + expr[1:]

            expr = re.sub(r"\{([A-Z]\w*)\}", r"{self.\1}", expr).lower()

            return f"return {expr}"

        # if is: return x;
        if re.fullmatch(r"[A-Za-z_]\w*", expr):
            return f"return self.{expr}"

        return f"return {expr}"

    def _map_return_type(self, cs_type: str) -> str:
        map_type = TypeMapper.map_type(cs_type)
        return map_type

    def _translate_parameters(self, params: str) -> str:
        if not params.strip():
            return ""

        python_params = []
        for param in params.split(','):
            param = param.strip()
            if ' ' in param:
                param_type, param_name = param.rsplit(' ', 1)
                python_type = map_type = TypeMapper.map_type(param_type)
                python_params.append(f"{param_name}, {python_type}")

        return ", ".join(python_params)