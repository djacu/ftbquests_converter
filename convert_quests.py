from pathlib import Path
import re
from typing import List, Tuple

from googletrans import Translator
from pprint import pprint

translator = Translator(service_urls=['translate.google.com'])


def get_title_and_text(quest: str) -> Tuple[str, List[str]]:
    title_line = re.findall(r'title: "(.*)"', quest)[0]
    text_lines = re.findall(r'text: \[\n([^]]*)\n\t\]', quest)[0]
    text_lines = re.findall(r'"(.+)"', text_lines)
    return title_line, text_lines


def translate_line(line: str) -> str:
    return translator.translate(line, src='ja', dest='en').text


def update_quest(quest: str) -> str:
    title, text_lines = get_title_and_text(quest=quest)
    quest = quest.replace(title, translate_line(title))
    for line in text_lines:
        quest = quest.replace(line, translate_line(line))
    return quest


def update_quest_file(quest_file: Path) -> None:
    with open(quest_file, 'r+') as fin:
        raw_text = fin.read()
        if raw_text.find('title') == -1 or raw_text.find('text') == -1:
            print(f'No text or title found in {quest_file}')
            print(raw_text)
        else:
            print(f'Translating {quest_file}')
            fin.write(update_quest(raw_text))


def main():
    quest_path = Path("chapters")
    for quest_file in quest_path.rglob("*.snbt"):
        update_quest_file(quest_file=quest_file)


if __name__ == '__main__':
    main()
