#!/bin/bash

source activate tfgpu

pid_master=pid/master.pid
pid_iden=pid/iden.pid
pid_detect_1=pid/detect.1.pid
pid_client_1=pid/client.1.pid
pid_detect_2=pid/detect.2.pid
pid_client_2=pid/client.2.pid
pid_detect_3=pid/detect.3.pid
pid_client_3=pid/client.3.pid
pid_detect_4=pid/detect.4.pid
pid_client_4=pid/client.4.pid
pid_detect_5=pid/detect.5.pid
pid_client_5=pid/client.5.pid

log_master=logs/master.log
log_iden=logs/iden.log
log_detect_1=logs/detect.1.log
log_client_1=logs/client.1.log
log_detect_2=logs/detect.2.log
log_client_2=logs/client.2.log
log_detect_3=logs/detect.3.log
log_client_3=logs/client.3.log
log_detect_4=logs/detect.4.log
log_client_4=logs/client.4.log
log_detect_5=logs/detect.5.log
log_client_5=logs/client.5.log
beginning=1

logging() {
	echo "[$(date '+%d/%m/%Y %H:%M:%S')] $1"
}

run_master() {
	if [ -f $pid_master ]; then
		kill -9 $(cat $pid_master) &> /dev/null
		rm $pid_master
	fi
	nohup python start_service.py -master &> $log_master &
	echo $! > $pid_master
}

run_detect_1() {
	if [ -f $pid_detect_1 ]; then
		kill -9 $(cat $pid_detect_1) &> /dev/null
		rm $pid_detect_1
	fi
	nohup python start_service.py -detect &> $log_detect_1 &
	echo $! > $pid_detect_1
}

run_detect_2() {
	if [ -f $pid_detect_2 ]; then
		kill -9 $(cat $pid_detect_2) &> /dev/null
		rm $pid_detect_2
	fi
	nohup python start_service.py -detect &> $log_detect_2 &
	echo $! > $pid_detect_2
}

run_detect_3() {
	if [ -f $pid_detect_3 ]; then
		kill -9 $(cat $pid_detect_3) &> /dev/null
		rm $pid_detect_3
	fi
	nohup python start_service.py -detect &> $log_detect_3 &
	echo $! > $pid_detect_3
}

run_detect_4() {
	if [ -f $pid_detect_4 ]; then
		kill -9 $(cat $pid_detect_4) &> /dev/null
		rm $pid_detect_4
	fi
	nohup python start_service.py -detect &> $log_detect_4 &
	echo $! > $pid_detect_4
}

run_detect_5() {
	if [ -f $pid_detect_5 ]; then
		kill -9 $(cat $pid_detect_5) &> /dev/null
		rm $pid_detect_5
	fi
	nohup python start_service.py -detect &> $log_detect_5 &
	echo $! > $pid_detect_5
}

run_iden() {
	if [ -f $pid_iden ]; then
		kill -9 $(cat $pid_iden) &> /dev/null
		rm $pid_iden
	fi
	nohup python start_service.py -iden &> $log_iden &
	echo $! > $pid_iden
}

run_client_1() {
	sleep 5s
	if [ -f $pid_client_1 ]; then
		kill -9 $(cat $pid_client_1) &> /dev/null
		rm $pid_client_1
	fi
	nohup python start_service.py -client -camid=1 -port=8888 -graphic &> $log_client_1 &
	echo $! > $pid_client_1
}

run_client_2() {
	sleep 5s
	if [ -f $pid_client_2 ]; then
		kill -9 $(cat $pid_client_2) &> /dev/null
		rm $pid_client_2
	fi
	nohup python start_service.py -client -camid=2 -port=8889 &> $log_client_2 &
	echo $! > $pid_client_2
}

run_client_3() {
	sleep 5s
	if [ -f $pid_client_3 ]; then
		kill -9 $(cat $pid_client_3) &> /dev/null
		rm $pid_client_3
	fi
	nohup python start_service.py -client -camid=3 -port=8890 &> $log_client_3 &
	echo $! > $pid_client_3
}

run_client_4() {
	sleep 5s
	if [ -f $pid_client_4 ]; then
		kill -9 $(cat $pid_client_4) &> /dev/null
		rm $pid_client_4
	fi
	nohup python start_service.py -client -camid=4 -port=8891 &> $log_client_4 &
	echo $! > $pid_client_4
}

run_client_5() {
	sleep 5s
	if [ -f $pid_client_5 ]; then
		kill -9 $(cat $pid_client_5) &> /dev/null
		rm $pid_client_5
	fi
	nohup python start_service.py -client -camid=5 -port=8892 &> $log_client_5 &
	echo $! > $pid_client_5
}

echo "========== Running watch-dog =========="

while $true; do
	if [ -f $pid_master ] && $(ps -p $(cat $pid_master) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Master service already running - PID $(cat $pid_master)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting master service..."
			run_master
		else
			timestamp=$(date +%s)
			logging "ERROR catched in master service!"

			logging "Backup $log_master to ${log_master}.$timestamp"
			mv $log_master ${log_master}.$timestamp
			logging "Restart master service..."; run_master

			logging "Backup $log_detect_1 to ${log_detect_1}.$timestamp"
			mv $log_detect_1 ${log_detect_1}.$timestamp
			logging "Restart detect-1 service..."; run_detect_1

			logging "Backup $log_detect_2 to ${log_detect_2}.$timestamp"
			mv $log_detect_2 ${log_detect_2}.$timestamp
			logging "Restart detect-2 service..."; run_detect_2

			logging "Backup $log_detect_3 to ${log_detect_3}.$timestamp"
			mv $log_detect_3 ${log_detect_3}.$timestamp
			logging "Restart detect-3 service..."; run_detect_3

			logging "Backup $log_detect_4 to ${log_detect_4}.$timestamp"
			mv $log_detect_4 ${log_detect_4}.$timestamp
			logging "Restart detect-4 service..."; run_detect_4

			logging "Backup $log_detect_5 to ${log_detect_5}.$timestamp"
			mv $log_detect_5 ${log_detect_5}.$timestamp
			logging "Restart detect-5 service..."; run_detect_5

			logging "Backup $log_client_1 to ${log_client_1}.$timestamp"
			mv $log_client_1 ${log_client_1}.$timestamp
			logging "Restart client-1..."; run_client_1
		fi
	fi

	if [ -f $pid_detect_1 ] && $(ps -p $(cat $pid_detect_1) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Detect-1 service already running - PID $(cat $pid_detect_1)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting detect-1 service..."
			run_detect_1
		else
			timestamp=$(date +%s)
			logging "ERROR catched in detect-1 service!"

			logging "Backup $log_detect_1 to ${log_detect_1}.$timestamp"
			mv $log_detect_1 ${log_detect_1}.$timestamp
			logging "Restart detect-1 service..."; run_detect_1

			logging "Backup $log_client_1 to ${log_client_1}.$timestamp"
			mv $log_client_1 ${log_client_1}.$timestamp
			logging "Restart client-1..."; run_client_1
		fi
	fi

	if [ -f $pid_detect_2 ] && $(ps -p $(cat $pid_detect_2) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Detect-2 service already running - PID $(cat $pid_detect_2)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting detect-2 service..."
			run_detect_2
		else
			timestamp=$(date +%s)
			logging "ERROR catched in detect-2 service!"

			logging "Backup $log_detect_2 to ${log_detect_2}.$timestamp"
			mv $log_detect_2 ${log_detect_2}.$timestamp
			logging "Restart detect-2 service..."; run_detect_2

			logging "Backup $log_client_2 to ${log_client_2}.$timestamp"
			mv $log_client_2 ${log_client_2}.$timestamp
			logging "Restart client-2..."; run_client_2
		fi
	fi

	if [ -f $pid_detect_3 ] && $(ps -p $(cat $pid_detect_3) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Detect-3 service already running - PID $(cat $pid_detect_3)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting detect-3 service..."
			run_detect_3
		else
			timestamp=$(date +%s)
			logging "ERROR catched in detect-3 service!"

			logging "Backup $log_detect_3 to ${log_detect_3}.$timestamp"
			mv $log_detect_3 ${log_detect_3}.$timestamp
			logging "Restart detect-3 service..."; run_detect_3

			logging "Backup $log_client_3 to ${log_client_3}.$timestamp"
			mv $log_client_3 ${log_client_3}.$timestamp
			logging "Restart client-3..."; run_client_3
		fi
	fi

	if [ -f $pid_detect_4 ] && $(ps -p $(cat $pid_detect_4) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Detect-4 service already running - PID $(cat $pid_detect_4)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting detect-4 service..."
			run_detect_4
		else
			timestamp=$(date +%s)
			logging "ERROR catched in detect-4 service!"

			logging "Backup $log_detect_4 to ${log_detect_4}.$timestamp"
			mv $log_detect_4 ${log_detect_4}.$timestamp
			logging "Restart detect-4 service..."; run_detect_4

			logging "Backup $log_client_4 to ${log_client_4}.$timestamp"
			mv $log_client_4 ${log_client_4}.$timestamp
			logging "Restart client-4..."; run_client_4
		fi
	fi

	if [ -f $pid_detect_5 ] && $(ps -p $(cat $pid_detect_5) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Detect-5 service already running - PID $(cat $pid_detect_5)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting detect-5 service..."
			run_detect_5
		else
			timestamp=$(date +%s)
			logging "ERROR catched in detect-5 service!"

			logging "Backup $log_detect_5 to ${log_detect_5}.$timestamp"
			mv $log_detect_5 ${log_detect_5}.$timestamp
			logging "Restart detect-5 service..."; run_detect_5

			logging "Backup $log_client_5 to ${log_client_5}.$timestamp"
			mv $log_client_5 ${log_client_5}.$timestamp
			logging "Restart client-5..."; run_client_5
		fi
	fi

	if [ -f $pid_iden ] && $(ps -p $(cat $pid_iden) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Identify service already running - PID $(cat $pid_iden)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting identify service..."
			run_iden
		else
			timestamp=$(date +%s)
			logging "ERROR catched in identify service!"

			logging "Backup $log_iden to ${log_iden}.$timestamp"
			mv $log_iden ${log_iden}.$timestamp
			logging "Rerun identify service"; run_iden

			logging "Backup $log_client_1 to ${log_client_1}.$timestamp"
			mv $log_client_1 ${log_client_1}.$timestamp
			logging "Restart client-1..."; run_client_1
		fi
	fi

	if [ -f $pid_client_1 ] && $(ps -p $(cat $pid_client_1) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Client-1 service already running - PID $(cat $pid_client_1)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting client-1..."
			run_client_1
		else
			timestamp=$(date +%s)
			logging "ERROR catched in client service!"

			logging "Backup $log_client_1 to ${log_client_1}.$timestamp"
			mv $log_client_1 ${log_client_1}.$timestamp
			logging "Restart client-1..."; run_client_1
		fi
	fi

	if [ -f $pid_client_2 ] && $(ps -p $(cat $pid_client_2) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Client-2 service already running - PID $(cat $pid_client_2)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting client-2..."
			run_client_2
		else
			timestamp=$(date +%s)
			logging "ERROR catched in client service!"

			logging "Backup $log_client_2 to ${log_client_2}.$timestamp"
			mv $log_client_2 ${log_client_2}.$timestamp
			logging "Restart client-2..."; run_client_2
		fi
	fi

	if [ -f $pid_client_3 ] && $(ps -p $(cat $pid_client_3) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Client-3 service already running - PID $(cat $pid_client_3)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting client-3..."
			run_client_3
		else
			timestamp=$(date +%s)
			logging "ERROR catched in client service!"

			logging "Backup $log_client_3 to ${log_client_3}.$timestamp"
			mv $log_client_3 ${log_client_3}.$timestamp
			logging "Restart client-3..."; run_client_3
		fi
	fi

	if [ -f $pid_client_4 ] && $(ps -p $(cat $pid_client_4) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Client-4 service already running - PID $(cat $pid_client_4)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting client-4..."
			run_client_4
		else
			timestamp=$(date +%s)
			logging "ERROR catched in client service!"

			logging "Backup $log_client_4 to ${log_client_4}.$timestamp"
			mv $log_client_4 ${log_client_4}.$timestamp
			logging "Restart client-4..."; run_client_4
		fi
	fi

	if [ -f $pid_client_5 ] && $(ps -p $(cat $pid_client_5) > /dev/null); then
		if [ $beginning -eq 1 ]; then
			logging "Client-5 service already running - PID $(cat $pid_client_5)"
		fi
	else
		if [ $beginning -eq 1 ]; then
			logging "Starting client-5..."
			run_client_5
		else
			timestamp=$(date +%s)
			logging "ERROR catched in client service!"

			logging "Backup $log_client_5 to ${log_client_5}.$timestamp"
			mv $log_client_5 ${log_client_5}.$timestamp
			logging "Restart client-5..."; run_client_5
		fi
	fi

	beginning=0
	sleep 5s
done
