import os
import regex as re
from obsidian_html.utils import slug_case, md_link, render_markdown
from obsidian_html.Note import Note
from obsidian_html import GLOBAL


class Vault:
    def __init__(self, vault_root, extra_folders=[], html_template=None, filter=[], out_dir=""):
        self.vault_root = vault_root
        self.out_dir = out_dir
        self.filter = filter
        self.notes = self._find_files(vault_root, extra_folders)
        self.extra_folders = extra_folders
        self._add_backlinks()
        self.stylesheet_path = ""

        self.html_template = html_template
        if html_template:
            with open(html_template, "r", encoding="utf8") as f:
                self.html_template = f.read()

        # Ensure out_dir exists, as well as its sub-folders. (must be done now to copy imgs(future) and stylesheet)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(os.path.join(out_dir, folder)):
                os.makedirs(os.path.join(out_dir, folder))

        # Find if any stylesheets are linked, and if they are local
        if GLOBAL.IGNORE_STYLESHEET == False: # Don't check if user specified ignore
            try:
                self.stylesheet_path = re.search('<link+.*rel="stylesheet"+.*href="(.+?)"', self.html_template).group(1)
            except AttributeError:
                #Then <link, rel="stylesheet", href="" wasn't found.
                GLOBAL.IGNORE_STYLESHEET = True
                print("Attributeerror")

            if not os.path.isfile(self.stylesheet_path):
                #Then the file referred to in the href does not exist. May be online hosted, and should be ignored.
                GLOBAL.IGNORE_STYLESHEET = True
                print("FileNotFoundError")
            else:
                #So it exists, and is local. Let's copy it to the output dir.
                #Probably a better copy method could have been used..
                
                style = open(self.stylesheet_path, "r") #open file
                self.stylesheet_outpath = os.path.join(out_dir, os.path.basename(self.stylesheet_path)) #set out path
                print("Copying " + self.stylesheet_path + " to: " + self.stylesheet_outpath)
                savestyle = open(self.stylesheet_outpath, 'w') #open out file
                savestyle.write(style.read())   #write out file
                style.close()
                savestyle.close()



    def _add_backlinks(self):
        for i, note in enumerate(self.notes):
            # Make temporary list of all notes except current note in loop
            others = [other for other in self.notes if other != note]
            backlinks = self.notes[i].find_backlinks(others)
            if backlinks:
                self.notes[i].backlinks += "\n<div class=\"backlinks\" markdown=\"1\">\n"
                for backlink in backlinks:
                    self.notes[i].backlinks += f"- {backlink.md_link()}\n"
                self.notes[i].backlinks += "</div>"

                self.notes[i].backlinks = render_markdown(self.notes[i].backlinks)

    def export_html(self):
        

        for note in self.notes:
            if self.html_template:
                html = self.html_template.format(title=note.title, content=note.html(), backlinks=note.backlinks)
                
                # Replace stylesheet href with correct relative path
                if GLOBAL.IGNORE_STYLESHEET == False:
                    relative_stylesheet_path = os.path.relpath(self.stylesheet_outpath, start = self.out_dir)
                    #Scanning to find the match and replace with new file
                    match = re.search('<link+.*rel="stylesheet"+.*href="(.+?)"', html)
                    if match:
                        replacement = re.sub(match.group(1), relative_stylesheet_path, match.group())
                        html = re.sub(match.group(), replacement, html)
                        
            else:
                html = note.html()
            with open(os.path.join(self.out_dir, note.filename_html), "w", encoding="utf8") as f:
                f.write(html)


    def _find_files(self, vault_root, extra_folders):
        # Find all markdown-files in vault root.
        md_files = self._find_md_files(vault_root)

        # Find all markdown-files in each extra folder.
        for folder in extra_folders:
            md_files += self._find_md_files(os.path.join(vault_root, folder), is_extra_dir=True)

        return md_files


    def _find_md_files(self, root, is_extra_dir=False):
        md_files = []
        for md_file in os.listdir(root):
            # Check if the element in 'root' has the extension .md and is indeeed a file
            if not (md_file.endswith(".md") and os.path.isfile(os.path.join(root, md_file))):
                continue
            
            note = Note(os.path.join(root, md_file), is_extra_dir=is_extra_dir)
            
            # Filter tags
            if self.filter:
                for tag in self.filter:
                    if tag in note.tags:
                        md_files.append(note)
                        break
            else:
                md_files.append(note)

        return md_files