from pathlib import Path
import re
from typing import List, Tuple

from googletrans import Translator
from pprint import pprint

translator = Translator(service_urls=['translate.google.com'])


def get_text_fields(quest: str) -> Tuple[str]:
    title_search = re.search(r'title: "(.*)"', quest)
    title_line = (title_search.group(1),) if title_search else ()

    text_search = re.search(r'text: \[\n([^]]*)\n\t\]', quest)
    text_lines = re.findall(r'"(.+)"', text_search.group(1)) if text_search else ()
    return (*title_line, *text_lines)


def translate_line(line: str) -> str:
    try:
        return translator.translate(line, src='ja', dest='en').text
    except IndexError:
        '''
        If googletrans gets a bad line of text like a url it will throw
        an error like:
            File .../googletrans/client.py", line 222, in translate
            translated_parts = list(map(
                lambda part: TranslatedPart(part[0], part[1] if len(part) >= 2 else []),
                parsed[1][0][0][5]))
            IndexError: list index out of range
        '''
        return line
    except AttributeError:
        '''
        googletrans 4.0.0.rc1 has a bug
        https://github.com/ssut/py-googletrans/issues/350

        can possibly be fixed just by re-calling the function
        '''
        return translate_line(line)
    except KeyError:
        '''
        Don't know why but this happened.
        Traceback (most recent call last):
        File ".../h2/connection.py", line 224, in process_input
        func, target_state = self._transitions[(self.state, input_)]
        KeyError: (<ConnectionState.CLOSED: 3>, <ConnectionInputs.RECV_PING: 14>)
        '''
        return translate_line(line)


def update_quest(quest: str, text_fields: Tuple[str]) -> str:
    for line in text_fields:
        quest = quest.replace(line, translate_line(line))
    return quest


def update_quest_file(input_path: Path, output_path: Path) -> None:
    with open(input_path, 'r') as fin:
        quest = fin.read()
        text_fields = get_text_fields(quest)
        if not text_fields:
            print(f'No text or title found in {input_path}.')
            print(quest)
        else:
            # print(text_fields)
            print(f'Translating {input_path}.')
        new_text = update_quest(quest, text_fields)

    with open(output_path, 'w') as fout:
        fout.write(new_text)


def make_output_path(path: Path) -> Path:
    parts = list(path.parts)
    parts[0] = parts[0] + "-trans"
    output_path = Path(*parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def main():
    quest_path = Path("./chapters")
    for input_path in quest_path.rglob("*.snbt"):
        output_path = make_output_path(input_path)
        update_quest_file(input_path, output_path)

    # with open(Path("chapters/4b5af78b/1f9e8255.snbt"), 'r') as fin:
    # # with open(Path("chapters/4b5af78b/chapter.snbt"), 'r') as fin:
    #     raw_text = fin.read()
    #     pprint(get_text_fields(raw_text))
    #     print(raw_text)


if __name__ == '__main__':
    main()

