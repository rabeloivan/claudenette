"""Count variables using the pinned C parser, after conditional preprocessing."""
import os
import re
import subprocess
from pathlib import Path


def _marker_path(value):
    # Clang escapes UTF-8 bytes, quotes and backslashes in #line filenames.
    # Decode the C escapes as bytes before applying the filesystem encoding.
    def unescape(match):
        escape = match[1]
        return bytes([int(escape, 8)]) if escape[:1].isdigit() else escape

    return Path(os.fsdecode(re.sub(rb'\\([0-7]{1,3}|["\\])', unescape,
                                   os.fsencode(value)))).resolve()


def variable_counts(sources, flags):
    # System headers contain their own globals. Line markers retain only the
    # student's translation units and headers after the compiler expands macros.
    from norminette.context import Context
    from norminette.file import File
    from norminette.lexer import Lexer
    from norminette.registry import Registry

    class Variables(Registry):
        def __init__(self):
            super().__init__()
            self.globals = 0
            self.statics = 0

        def run_rules(self, context, rule):
            if (rule.__name__ == 'CheckIdentifierName' and context.history
                    and context.history[-1].name == 'IsVarDeclaration'):
                count = len(context.scope.vars_name)
                tokens = context.tokens[:context.tkn_scope]
                if context.scope.name == 'GlobalScope':
                    self.globals += count
                if any(token.type == 'STATIC' for token in tokens):
                    self.statics += count
            return super().run_rules(context, rule)

    own_files = {Path(path).resolve() for path in sources}
    globals_count = static_count = 0
    for source in sources:
        if not source.endswith('.c'):
            continue
        result = subprocess.run(['cc', '-E', *flags, source], capture_output=True,
                                text=True, timeout=30)
        if result.returncode:
            raise ValueError(result.stderr.strip())
        active = False
        lines = []
        for line in result.stdout.splitlines(keepends=True):
            marker = re.match(r'^#\s+\d+\s+"((?:\\.|[^"\\])*)"', line)
            if marker:
                active = _marker_path(marker[1]) in own_files
            elif active:
                lines.append(line)
        file = File(source, ''.join(lines))
        variables = Variables()
        variables.run(Context(file, list(Lexer(file)), 0, None))
        globals_count += variables.globals
        static_count += variables.statics
    return globals_count, static_count
