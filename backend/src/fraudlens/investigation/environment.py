"""Private local configuration; never executes shell syntax or mutates the process."""
import os
import re
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[4] / '.env'


def read_environment():
    """Read root .env literals, then overlay process values (even empty strings).

    Supports KEY=value, optional export, single/double quotes and comments.
    Values are single-line literals: no interpolation, escape or shell expansion.
    Missing files are optional; malformed/unreadable files fail closed.
    """
    values = {}
    try:
        lines = ENV_FILE.read_text(encoding='utf-8-sig').splitlines()
    except FileNotFoundError:
        lines = []
    except (OSError, UnicodeError):
        raise ValueError('Local backend configuration unavailable') from None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
        if not match:
            raise ValueError('Invalid local backend configuration')
        name, raw = match.groups()
        if raw.startswith(('"', "'")):
            quoted = re.fullmatch(r"(['\"])(.*?)\1\s*(?:#.*)?", raw)
            if not quoted:
                raise ValueError('Invalid local backend configuration')
            value = quoted[2]
        else:
            value = re.split(r'\s+#', raw, maxsplit=1)[0].strip()
            if value.startswith('#'):
                value = ''
        values[name] = value
    return {**values, **os.environ}
