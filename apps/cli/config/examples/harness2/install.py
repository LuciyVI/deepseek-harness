"""Install this optional bridge into an existing dsh profile."""

import sys
from pathlib import Path

from harness2.cli.dsh_install import main

if __name__ == "__main__":
    raise SystemExit(
        main(
            [
                "--plugin-source",
                str(Path(__file__).with_name("bridge.mjs")),
                *sys.argv[1:],
            ]
        )
    )
