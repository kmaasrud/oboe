import regex as re
import os


def slug_case(text):
    text = text.replace(".", "dot")
    text = text.replace("_", "-")
    return re.sub(r'[^\w\-/]+', '-', text).lower()


def md_link(text, link):
    return "[" + text + "](" + link + ".html)"


def extract_links_from_file(document):
    matches = re.finditer(r"\[{2}([^\]]*?)[|#\]]([^\]]*?)\]+", document)

    links = []
    for match in matches:
        link = match.group(1)
        links.append(link)

    return links


def find_backlinks(target_note_name, all_notes):
    backlinks = []
    for note in all_notes:
        links = extract_links_from_file(note["content"])
        if target_note_name in links:
            backlinks.append({"text": note["filename"].replace(".md", ""),
                              "link": slug_case(note["filename"].replace(".md", ""))})

    backlinks = sorted(backlinks, key=lambda x: x['text'])

    return backlinks
