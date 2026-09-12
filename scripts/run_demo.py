from pathlib import Path
import sys


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loreforge.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

