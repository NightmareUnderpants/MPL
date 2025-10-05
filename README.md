# Modern Programming Language (MPL)

## Lab 1
['main.py'](/Lab_1/main.py)


## Translator from C# code to Python code (Lab 2) 
entry point of program: ['lab_2.py'](/Lab_2/lab_2.py)

### Explanation
this programm converts base C# code into Python code. Base i mean that can converts func, classes and main func.

all the functionality of the program is stored in direction `/Lab_2/Translator/`

### C# code recommendations:
- __the C# code must be error-free!__
- C# code can consist of several simple classes
- The entry point of the program must look like this: `public static void Main(string[] args)`
- Support for simple assignment and typing operations var
- Available output support `Console.WriteLine();`
- An example of translator functionality is provided in the ['example.cs'](/Lab_2/example.cs) file

### Hot to Use
['Example'](/Lab_2/lab_2.py)

The program has 5 main func:
```
translator = Translator.Translator()
csharp_code = translator.convert_cs_to_str(file_path)
code = translator.translate(csharp_code)
code = translator.delete_comments(code)
translator.save_translation(code, file_path)
```
- `translator.convert_cs_to_str(file_path)` convert cs file to string and return `str`
- `translator.translate(csharp_code)` convert cs code in string to python code in string and return `List(str)`
- `translator.delete_comments(code)` this func delete all comments (#) and return `List(str)`
- `translator.save_translation(code, file_path)` this func save python code into file
