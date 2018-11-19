ps aux | grep 1.watch_dog.sh | awk '{print $2}' | xargs kill -9
ps aux | grep start_service.py | awk '{print $2}' | xargs kill -9
rm -f pid/*
