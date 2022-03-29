import sys
import subprocess
import pkg_resources

required = {'matplotlib', 'Pillow', 'pandas', 'mplfinance', 'tensorflow', 'keras'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
