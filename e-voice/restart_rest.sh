#bin/bash
kill -9 $(ps ax | grep -i 'rest:app' | grep -v grep | awk '{print $1}')
sh start_rest.sh