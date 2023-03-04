import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))
"""try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass"""