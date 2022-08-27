from collections import ChainMap
import json
import logging
import os
from pathlib import Path
from pprint import pprint, pformat
import re
from typing import Dict, List, Tuple

from google.cloud import translate_v2



def get_text_fields(quest: str) -> Tuple[str]:
    title_search = re.findall(r'title: "(.*)"', quest)
    title_line = title_search if title_search else ()

    desc_search = re.findall(r'description: "(.*)"', quest)
    desc_line = desc_search if desc_search else ()

    text_search = re.search(r'text: \[\n([^]]*)\n\t\]', quest)
    text_lines = re.findall(r'"(.+)"', text_search.group(1)) if text_search else ()
    return (*title_line, *desc_line, *text_lines)


def read_text_from_file(input_path: Path) -> List[str]:
    with open(input_path, 'r') as fin:
        return fin.read()


def get_input_strings(quest_path: Path) -> List[str]:
    nested_list = [get_text_fields(read_text_from_file(input_path))
                   for input_path in quest_path.rglob("*.snbt")]
    return [elem for sublist in nested_list for elem in sublist]


def translate_text(input_strings: List[str]) -> List[Dict[str, str]]:
    cred_path = str(Path('./gcloud-translation-credentials.json').resolve())
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
    chunk_size = 100
    translator = translate_v2.Client()
    trans_chunks = [
        translator.translate(
            values=chunk,
            target_language='en',
            source_language='ja',
            model='nmt')
        for chunk in chunks(input_strings, chunk_size)]
    return [queries for chunk in trans_chunks for queries in chunk]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def prep_translations(translations: List[Dict[str, str]]) -> Tuple[Dict[str, str], List[str]]:
    replacements = {query['input']: query['translatedText'] for query in translations}

    # Place longer ones first to keep shorter substrings from matching
    # where the longer ones should take place For instance given the
    # replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey
    # abc', it should produce 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    return replacements, rep_sorted


def multi_replace(string: str, replacements: Dict[str, str], rep_sorted: List[str]) -> str:
    '''
    Partially taken from
    https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729

    '''
    # Edge case that'd produce a funny regex and cause a KeyError
    if not replacements:
        return string

    rep_escaped = map(re.escape, rep_sorted)

    # Create a big OR regex that matches any of the substrings to replace
    re_mode = 0
    pattern = re.compile("|".join(rep_escaped), re_mode)

    # For each match, look up the new string in the replacements, being
    # the key the normalized old string
    return pattern.sub(lambda match: replacements[match.group(0)], string)


def make_output_path(path: Path) -> Path:
    parts = list(path.parts)
    parts[0] = parts[0] + "-trans"
    output_path = Path(*parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def update_quest_file(input_path: Path, string: str) -> None:
    output_path = make_output_path(path=input_path)
    with open(output_path, 'w') as file_out:
        file_out.write(string)


def log_translations(input_path: Path, input_string: str, trans_string: str) -> None:
    if input_string is trans_string:
        logging.info(f'Nothing translated in {input_path}')
    else:
        logging.info(f'Translating {input_path}')

    logging.debug(trans_string)


def make_translated_quests(quest_path: Path, replacements: Dict[str, str], rep_sorted: List[str]) -> None:
    for input_path in quest_path.rglob("*.snbt"):
        input_string = read_text_from_file(input_path=input_path)
        trans_string = multi_replace(string=input_string, replacements=replacements, rep_sorted=rep_sorted)
        log_translations(input_path=input_path, input_string=input_string, trans_string=trans_string)
        update_quest_file(input_path=input_path, string=trans_string)


def main():
    logging.basicConfig(filename='batch-translation.log', encoding='utf-8', level=logging.DEBUG)

    quest_path = Path("./chapters")
    input_strings = get_input_strings(quest_path)
    translations = translate_text(input_strings)
    replacements, rep_sorted = prep_translations(translations=translations)
    logging.debug(f"Replacements = {json.dumps(replacements, indent=4, ensure_ascii=False)}")
    make_translated_quests(quest_path=quest_path, replacements=replacements, rep_sorted=rep_sorted)


if __name__ == '__main__':
    main()
