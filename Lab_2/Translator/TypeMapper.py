class TypeMapper:

    @staticmethod
    def map_type(csharp_type: str) -> str:
        TYPE_MAPPING = {
            'string': 'str',
            'int': 'int',
            'double': 'float',
            'float': 'float',
            'bool': 'bool',
            'void': 'None',
            'object': 'Any',
            'List': 'List',
            'Dictionary': 'Dict',
            'Task': 'Awaitable'
        }
        return TYPE_MAPPING[csharp_type]