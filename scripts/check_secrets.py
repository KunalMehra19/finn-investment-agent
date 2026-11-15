"""Check the user-supplied secret is absent from public source, history and assets."""
import os,subprocess
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
secret=os.environ['GEMINI_API_KEY'].encode()
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
checked=0
for name in files:
    p=Path(name)
    if p.is_file():
        if secret in p.read_bytes():raise SystemExit('Secret found in public source; publishing stopped.')
        checked+=1
for sha in subprocess.check_output(['git','rev-list','--all'],text=True).splitlines():
    if secret in subprocess.check_output(['git','archive','--format=tar',sha]):raise SystemExit('Secret found in repository history; publishing stopped.')
for folder in ['dist/assets','dist/server']:
    for p in Path(folder).glob('*'):
        if p.is_file() and secret in p.read_bytes():raise SystemExit('Secret found in built asset; publishing stopped.')
print(f'Secret scan passed: {checked} public files, all Git history and built assets. Credential value was not logged.')
