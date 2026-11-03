import sys
from pathlib import Path

# リポジトリ直下の buzz_relay.py を import できるようにする
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
