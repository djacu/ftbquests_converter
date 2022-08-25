from pathlib import Path
import re
from typing import List, Tuple

from googletrans import Translator
from pprint import pprint

translator = Translator(service_urls=['translate.google.com'])
test_file = Path("chapters-eng/4b5af78b/1f9e8255.snbt")


def get_title_and_text(snbt: str) -> Tuple[str, List[str]]:
    title_line = re.findall(r'title: "(.*)"', snbt)[0]
    text_lines = re.findall(r'text: \[\n([^]]*)\n\t\]', snbt)[0]
    text_lines = re.findall(r'"(.+)"', text_lines)
    return title_line, text_lines


def translate_line(line: str) -> str:
    return translator.translate(line, src='ja', dest='en').text


def update_quest(snbt: str) -> str:
    title, text_lines = get_title_and_text(snbt=snbt)
    snbt = snbt.replace(title, translate_line(title))
    for line in text_lines:
        snbt = snbt.replace(line, translate_line(line))
    return snbt


'''raw text'''
with open(test_file, 'r') as fin:
    raw_text = fin.read()

# title_line, text_lines = get_title_and_text(raw_text)
# title_line = translate_title_line(title_line)
# text_lines = translate_text_lines(text_lines)
# new_text = update_quest(raw_text, (title_line, text_lines))
# pprint(text_lines)

print(update_quest(raw_text))


# print(raw_text)
# print(re.findall(r'text: \[([^][]*[^][]*)]', raw_text))
# print(re.findall(r'\[(.*)\]', raw_text))

# print(re.findall(r'text: \[\n([^]]*)\n\t\]', raw_text)[0])
# print(re.findall(r'title: (".*")', raw_text)[0])
# print(re.findall(r'title: "(.*)"', raw_text)[0])


