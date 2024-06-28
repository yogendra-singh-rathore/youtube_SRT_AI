"""
This Script Translate Hindi to English and then into other like Chinese, German, etc
"""
from deep_translator import GoogleTranslator

def translate_text(text, source_language, target_language):
    translator = GoogleTranslator(source=source_language, target=target_language)
    return translator.translate(text)

def translate_srt(file_path, intermediate_language, target_languages):
    # Read the original SRT file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Translate the text to the intermediate language (English)
    translated_lines_to_intermediate = []
    for line in lines:
        if not line.strip() or line[0].isdigit() or '-->' in line:
            translated_lines_to_intermediate.append(line)
        else:
            translated_text = translate_text(line, 'auto', intermediate_language)
            translated_lines_to_intermediate.append(translated_text + '\n')

    # Save the intermediate language file
    intermediate_file_path = f'translated_{intermediate_language}.srt'
    with open(intermediate_file_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines_to_intermediate)

    print(f"Subtitles translated to {intermediate_language} saved to {intermediate_file_path}")

    # Translate the intermediate language file to other target languages
    for target_language in target_languages:
        translated_lines_to_target = []
        for line in translated_lines_to_intermediate:
            if not line.strip() or line[0].isdigit() or '-->' in line:
                translated_lines_to_target.append(line)
            else:
                translated_text = translate_text(line, intermediate_language, target_language)
                translated_lines_to_target.append(translated_text + '\n')

        output_file_path = f'translated_{target_language}.srt'
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.writelines(translated_lines_to_target)

        print(f"Subtitles translated to {target_language} saved to {output_file_path}")

# Example usage
translate_srt('output.srt', 'en', ['de', 'zh-CN', 'ja'])  # Translate to English first, then to German, Chinese, and Japanese
