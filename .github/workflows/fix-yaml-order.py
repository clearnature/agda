"""Move name: and 'on': to the top of a GitHub Actions YAML file.

GitHub requires these fields at the top of the document, but the
yaml2json|json2yaml pipeline sorts keys alphabetically, putting
jobs: before name: and on:.

Usage: python3 fix-yaml-order.py <file>
"""
import re, sys

with open(sys.argv[1]) as f:
    c = f.read()

# Split after the auto-generated header (ends with ---)
header_end = c.index('---\n') + 4 if '---\n' in c else (c.index('\n') + 1 if '\n' in c else len(c))
body = c[header_end:]

# Extract name: block (multi-line, indented continuation)
m_name = re.search(r'^name:.*(?:\n  .*)*', body, re.M)
# Extract 'on': or on: block (multi-line, until next top-level key)
m_on = re.search(r"^'?on'?:.*(?:\n  .+(?:\n  .*)*)*", body, re.M)

if m_name and m_on:
    name_block = m_name.group()
    on_block = m_on.group()
    # Remove name and on from body
    body = re.sub(r'^name:.*(?:\n  .*)*\n?', '', body, count=1, flags=re.M)
    body = re.sub(r"^'?on'?:.*(?:\n  .+(?:\n  .*)*)*\n?", '', body, count=1, flags=re.M)
    # Write: header + name + on + body
    with open(sys.argv[1], 'w') as f:
        f.write(c[:header_end] + name_block + '\n' + on_block + '\n' + body.lstrip())
    print(f"Fixed: {sys.argv[1]}")
else:
    print(f"No change: {sys.argv[1]}")
