"""
This module allows you to analyse OCaml source code, autocomplete,
and infer types while writing.
"""

import functools
import sublime
import sublime_plugin
import re
import os
import sys
import subprocess

supported_syntaxes = ['Packages/OCaml/OCaml.sublime-syntax']

class OcpIndentBuffer(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):
        settings = view.settings()
        if not settings.get('syntax') in supported_syntaxes:
            return None
        if command_name == "insert" and args['characters'] == '\n':
            settings.set("auto_indent", False)
            sel = view.sel()[0]
            line = view.rowcol(sel.begin())[0] + 2
            process = subprocess.Popen(
                    ["ocp-indent", "--numeric", "--line", str(line)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    )
            prefix = view.substr(sublime.Region(0, sel.begin()))
            suffix = view.substr(sublime.Region(sel.end(), view.size()))
            (result, _) = process.communicate(input = prefix + '\n' + suffix)
            result = int(result)
            if result > 0:
                indented = '\n' + (result * ' ')
                return (command_name, {'characters': indented})
        return None
