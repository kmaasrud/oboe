import regex as re
import markdown2
from utils import slug_case, md_link


def format_internal_links(document):
    """Formats Obsidian style links that are neither aliased, nor links to headers"""
    matches = re.finditer("\\[{2}([^|#]*?)\\]{2}", document)

    return obsidian_to_commonmark_links(document, matches, no_groups=1)


def format_internal_aliased_links(document):
    """Formats Obsidian style aliased links"""
    matches = re.finditer("\\[{2}([^|#\\]]*?)\\|(.*?)\\]{2}", document)

    return obsidian_to_commonmark_links(document, matches)


def format_internal_header_links(document):
    """Formats Obsidian style header links"""
    matches = re.finditer("\\[{2}([^|#\\]]*?)#(.*?)\\]{2}", document)

    return obsidian_to_commonmark_links(document, matches)


def format_tags(document):
    """Obsidian style tags. Removes #-icon and adds a span tag."""
    matches = re.finditer(r"#([\p{L}_]+)", document)

    for match in matches:
        document = document.replace(
            match.group(), "<span class=\"tag\">" + match.group(1) + "</span>")

    return document


def obsidian_to_commonmark_links(document, matches, no_groups=2):
    for match in matches:
        text = match.group(no_groups)
        link = slug_case(match.group(1))
        document = document.replace(match.group(), md_link(text, link))

    return document


def htmlify(document):
    # Formatting of Obsidian tags and links.
    document = format_internal_links(
        format_internal_aliased_links(
            format_internal_header_links(
                format_tags(document))))

    markdown2_extras = [
        # Parser should work withouth strict linebreaks.
        "break-on-newline",
        # Support of ```-codeblocks and syntax highlighting.
        "fenced-code-blocks",
        # Make slug IDs for each header. Needed for internal header links.
        "header-ids",
        # Support for strikethrough formatting.
        "strike",
        # GFM tables.
        "tables",
        # Support for lists that start without a newline directly above.
        "cuddled-lists",
        # Have to support Markdown inside html tags
        "markdown-in-html"
    ]

    html = markdown2.markdown(document, extras=markdown2_extras)

    return html