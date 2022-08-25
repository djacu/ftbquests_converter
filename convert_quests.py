from pathlib import Path
import re
from typing import List, Tuple

from googletrans import Translator
from pprint import pprint

translator = Translator()
test_file = Path("chapters-eng/4b5af78b/1f9e8255.snbt")


def get_title_and_text(snbt: str) -> Tuple[str, List[str]]:
    text_lines = []
    text_found = False
    for line in snbt.split('\n'):

        if line.find('title') != -1:
            title_line = line

        if line.find('],') != -1 and text_found:
            text_found = False

        if text_found:
            text_lines.append(line)

        if line.find('text: [') != -1:
            text_found = True

    return title_line, text_lines


def combine_lines(lines: List[str]) -> List[str]:
    combined_lines = []
    for line in lines:
        clean_line = line.strip('\t')

        if not combined_lines:
            combined_lines.append(clean_line)

        if clean_line.find('"",') != -1:
            combined_lines.append(clean_line)
        else:
            combined_lines[-1] = combined_lines[-1] + clean_line
    return combined_lines


def translate_text_lines(lines: List[str]) -> List[str]:
    cleaned = [line.strip('\t') for line in lines]
    translated = [translator.translate(line).text for line in cleaned]
    tabbed = ['\t\t' + line for line in translated]
    return tabbed


def translate_title_line(title: str) -> str:
    title_text = re.findall(r'"([^"]*)"', title)[0]
    title_trans = translator.translate(title_text).text
    return title.replace(title_text, title_trans)


def update_quest(snbt: str, new_text: Tuple[str, List[str]]) -> str:
    title_line, text_lines = new_text
    snbt = '\n'.join([update_title(line, title_line) for line in snbt.split('\n')])

    return snbt


def update_title(line, title_line):
    if line.find('title') != -1:
        return title_line
    return line


# def delete_text_lines(line):



'''raw text'''
with open(test_file, 'r') as fin:
    raw_text = fin.read()

title_line, text_lines = get_title_and_text(raw_text)
print(text_lines)
# title_line = translate_title_line(title_line)
# text_lines = translate_text_lines(text_lines)
# new_text = update_quest(raw_text, (title_line, text_lines))
# print(new_text)


# print(raw_text)
# print(re.findall(r'text: \[([^][]*[^][]*)]', raw_text))
# print(re.findall(r'\[(.*)\]', raw_text))
print(re.findall(r'text: \[\n([^]]*)\n\t\]', raw_text)[0])





# print(rawText)

# for line in text_lines:
#     if line == "":
#         print("")
#     else:
#         print(translator.translate(line).text)

