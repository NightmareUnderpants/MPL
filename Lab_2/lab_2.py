from Lab_2.Translator import Translator
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "example.cs")

    translator = Translator.Translator()

    csharp_code = translator.convert_cs_to_str(file_path)
    code = translator.translate(csharp_code)

    print(f'\n\nPYTHON CODE:\n')
    for l in code:
        print(f"{l}")

    print(f'\n\nPYTHON CODE WITHOUT COMMENTS:\n')
    code = translator.delete_comments(code)
    for l in code:
        print(f"{l}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "example.py")

    translator.save_translation(code, file_path)
