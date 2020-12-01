# Obsidian to HTML converter

This is a short Python script to convert an [Obsidian](https://obsidian.md/) vault into a vault of HTML files, with the goal of publishing them as static files. It is heavily dependent on the excellent [markdown2](https://github.com/trentm/python-markdown2) by [trentm](https://github.com/trentm), but also deals with some parsing and file handling that makes it compatible with Obsidian's flavor of Markdown.

## Installation

Install `obsidian-html` by running:

    sudo pip install git+https://github.com/kmaasrud/obsidian-html.git

Or doing the same (without the `sudo`) as an administrator on Windows.

> Admin privileges is needed to ensure that the script is in the PATH. You can easily clone this repo and install the package locally with `pip install .` or `python setup.py develop`, if you do not want to install as admin.

## Usage

`obsidian-html` will by default convert all the Markdown documents in the folder you're running it in, and place the HTML files in a directory called `html`. You might not want to run it directly in your vault or place the converted files in another directory. This is specified by this syntax:

    obsidian-html <path to vault> -o <path to html files>

The script will only convert the files located directly in the directory specified and never work recursively. To specify subfolders, these must be supplied to the `-d` flag, like in this example:

    obsidian-html <vault> -d "Daily notes" "Zettels"

### Templates

The output is not very exiting from the get-go. It needs some style and structure. This is done by using a HTML template. A template must have the formatters `{title}` and `{content}` present. Their value should be obvious. The template should use the `{backlinks}` formatter for the links to notes that reference this note. The template file is supplied to `obsidian-html` by the `-t` flag, like this:

    obsidian-html <vault> -t template.html

Here you can add metadata, link to CSS-files and add unified headers/footers to all the pages. [Here's](https://github.com/kmaasrud/brain/blob/master/template.html) an example of how I use the template function on my own hosted vault.

### Local browsing

Most web-servers do not need the `.html` file extension in URLs to find the correct file. However, that might be needed when browsing the converted vault locally. If you experience issues with this or want all links to have a `.html` extension, just add this option:

    obsidian-html <vault> -e

### TeX support via KaTeX

By loading KaTeX in the HTML template and initializing it with `$` and `$$` as delimiters, you will have TeX support on the exported documents.

Just add this to the bottom of you template's body:

```html
<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.css"
  integrity="sha384-zB1R0rpPzHqg7Kpt0Aljp8JPLqbXI3bhnPWROx27a9N0Ll6ZP/+DiW/UqRcLbRjq" crossorigin="anonymous">

<!-- The loading of KaTeX is deferred to speed up page rendering -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.js"
  integrity="sha384-y23I5Q6l+B6vatafAwxRu/0oK/79VlbSz7Q9aiSZUvyWYIYsd+qj+o24G5ZU2zJz"
  crossorigin="anonymous"></script>

<!-- To automatically render math in text elements, include the auto-render extension: -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/contrib/auto-render.min.js"
  integrity="sha384-kWPLUVMOks5AQFrykwIup5lo0m3iMkkHrD0uJ4H5cjeGihAutqP0yW0J6dpFiVkI"
  crossorigin="anonymous"></script>

<!-- Parsing single dollar signs -->
<script>
  document.addEventListener("DOMContentLoaded", function () {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{left: "$$", right: "$$", display: true}},
        {{left: "\\[", right: "\\]", display: true}},
    {{left: "$", right: "$", display: false}},
    {{left: "\\(", right: "\\)", display: false}}
      ]
  }});
  }});
</script>
```

> Note the double `{`'s. This is to work around how Python formatting works, and will be correct in the outputted HTML.

### Syntax highlighting of code blocks

Using [highlight.js](https://highlightjs.org/), syntax highlighting is easily achieved.

Just add this to the bottom of you template's body:

```html
<!-- Syntax highlighting through highlight.js -->
<link rel="stylesheet" href="https://unpkg.com/@highlightjs/cdn-assets@10.4.0/styles/default.min.css">
<script src="https://unpkg.com/@highlightjs/cdn-assets@10.4.0/highlight.min.js"></script>

<script>
  // Ignore highlighting of mermaid
  hljs.configure({{noHighlightRe: /^mermaid$/}});
  hljs.initHighlightingOnLoad();
</script>
```

> Note the double `{`'s. This is to work around how Python formatting works, and will be correct in the outputted HTML.

---

## Deploying vault with GitHub Actions

Make a GitHub Actions workflow using the YAML below, and your vault will be published to GitHub Pages every time you push to the repository.

1. Make sure you have GitHub Pages set up in the vault, and that it has `gh-pages` `/root` as its source.
2. Modify the following YAML job to match your repository.

    ```yaml
    name: Deploy to GitHub Pages

    on:
      push:
        branches: [ master ]
      
    jobs:
      deploy:
        runs-on: ubuntu-latest

        steps:
        - uses: actions/checkout@v2

        - name: Set up Python 3.8
          uses: actions/setup-python@v2
          with:
            python-version: 3.8

      - name: Install obsidian-html
        run: |
          python -m pip install --upgrade pip
          pip install git+https://github.com/kmaasrud/obsidian-html.git
          
      - name: Generate HTML through obsidian-html
        run: obsidian-html ./vault -o ./out -t ./template.html -d daily

      - name: Deploy
        uses: s0/git-publish-subdir-action@develop
        env:
          REPO: self
          BRANCH: gh-pages
          FOLDER: out
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```

## To do


- [ ] Support local attachments
- [ ] Support the `![[]]` embedding syntax (perhaps using iframe or some similar method)
- [ ] Option to generate JSON-file that can be used by a search engine of choice.
- [x] Support for the `==text==` highlighting syntax.

## Known issues

- Links in headers lead to weird header ids, and thus malfunctioning header links from other pages.
- There might be issues related to emoji in filenames/directory names. This seems to be an issue with how `setuptools` handles command line arguments. Refer to [this comment](https://github.com/kmaasrud/obsidian-html/issues/3#issuecomment-705512714) for a workaround.
