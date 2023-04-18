#!/bin/bash
# conda env update -f env.ym
# conda activate v5onv1
. /opt/conda/etc/profile.d/conda.sh
conda activate v5onv1
# conda run -n v5onv1 /bin/bash -c
# pip install attrdict
# pip install -e src/api/model
echo "Running gunicorn"
gunicorn --config gunicorn.py app:app
