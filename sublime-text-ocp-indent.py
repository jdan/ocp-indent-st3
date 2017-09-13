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
import platform

supported_syntaxes = ['Packages/OCaml/OCaml.sublime-syntax', 'Packages/OCaml/OCaml.tmLanguage']

IS_WINDOWS = platform.system() == 'Windows'

def do_replace(edit, view, region, replacement):
    encoding = view.encoding() if view.encoding() != 'Undefined' else 'utf-8'
    view.replace(edit, region, replacement.decode(encoding))

def ocp_indent_code(edit, view, region):
    command = ['ocp-indent']
    code = view.substr(region)
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=IS_WINDOWS
    )
    ocp_indent_output, err = proc.communicate(str.encode(code))

    if err or proc.returncode != 0:
        report_error(proc.returncode, err)
    else:
        do_replace(edit, view, region, ocp_indent_output)

class OcpIndentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = self.view.settings()
        if not settings.get('syntax') in supported_syntaxes:
            return None

        region = sublime.Region(0, self.view.size())
        ocp_indent_code(edit, self.view, region)

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

    def on_pre_save(self, view):
        view.run_command("ocp_indent")
