#!/bin/bash
&&&=${1-"no&&&"}
host="127.0.0.1"
if [[ $&&& == "&&&" ]]; then
  export FLASK_ENV=&&&elopment
elif [[ $&&& == "prod" ]]; then
  host="0.0.0.0"
fi

python -m flask run --host="$host" --port=5000
