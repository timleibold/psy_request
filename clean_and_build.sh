# clean_and_build.sh
#!/usr/bin/env bash
set -e

# 1) Remove old eggs and builds
rm -rf functions/.eggs build dist

# 2) Invoke py2app
python setup.py py2app