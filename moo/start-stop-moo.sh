#!/bin/sh
#
# start-stop-moo 
# Ken Fox
# A script to handle starting and stopping the MOO server.
# When stopping, it will wait for the moo process to exit before continuing.
#

#
# INSTALLATION 
#    Modify the variables below to fit your setup.
#    
# USAGE
#    start-stop-moo [start|stop]
#


# the user the MOO runs as; OR modify the paths below
USER=wp

#
# Directory databases are kept in.  Script will cd into here before contining.
#

MOODIR=/home/$USER/run

# directory for archived log files
LOGDIR=/home/$USER/logs
# directory for checkpoints
DBDIR=/home/$USER/dbs

#
# Location of your MOO binary.
#

MOO=/home/wp/bin/moo

#
# Base name of your database (without the .db)
#

DBNAME=Waterpoint

#
# Name of the log file for the currently running MOO process.
#

LOG=${DBNAME}.log.current

#
# The port your MOO runs on.
#

PORT=8301

#
# umask for the MOO process.  077 means "only let this user read or write it"
#

UMASK=077

#
# Program to gzip the database.
#

COMPRESS=gzip

#
# Suffix for files compressed with above program.
#

COMPRESS_SUFFIX=gz

#
# It will wait up to this many seconds for the server to exit
# after sending the shutdown signal before deciding something is wrong.
# (default) 60 seconds = 1 minute

SHUTDOWN_TIMEOUT=60

#
# This sets the timezone to Eastern time, since that's where WP lives
#
#TZ=US/Eastern
TZ=America/Los_Angeles; export TZ

#
# You shouldn't have to modify anything under here.
#

if [ "${DBNAME}" = "Unconfigured" ]; then
  echo "$0 has not been configured."
  echo "Please edit it and set the variables for your setup."
  exit 1
fi

cd ${MOODIR}

mkdir -p ${LOGDIR}
mkdir -p ${DBDIR}

umask ${UMASK}
DB=${DBNAME}.db
DBCHECK=${DB}.new
PIDFILE=${DBNAME}.pid

if [ "$1" = "-h" -o "$#" -ne 1 ]; then
   echo "Usage: $0 [start|stop]"
   exit 1
fi


if [ "$1" = "stop" ]; then
   if [ -f ${PIDFILE} ]; then
      PID=`cat ${PIDFILE}`  
      echo "Sending SIGUSR1 (shutdown) to ${PID}..."
      if ! /bin/kill -USR1 ${PID}; then
         echo No moo process found.
         exit 1
      fi 
      TIMER=${SHUTDOWN_TIMEOUT}
      echo -n "Waiting for ${DBNAME} to finish exiting.."
      while [ ${TIMER} -gt 1 -a -f ${PIDFILE} ]; do
         echo -n .
         sleep 5
         TIMER=`expr ${TIMER} - 5`
      done 
      if [ -f ${PIDFILE} ]; then
         echo timeout.
         exit 1
      else
         echo done.
         exit 0
      fi
  else  
     echo No ${PIDFILE} file, perhaps the moo is not running?
  fi
  exit 1
elif [ ! "$1" = "start" ]; then
  echo "Usage: $0 [start|stop]"
  exit 1
fi

#
# Check for already running...
#
if [ -s ${PIDFILE} ]; then
   PID=`cat ${PIDFILE}`
	echo "Warning! PID file already exists ($PID)."
   echo "MOO might already be running."
   echo 
   echo "Continuing anyway in 10 seconds...."
   sleep 10
fi


#
# Check for partial checkpoints
#
DBSAVED=`echo ${DBCHECK}.\#*\#`
if [ "${DBSAVED}" != "${DBCHECK}.#*#" ]; then
  echo "Warning!  Partial checkpoint files exist:"
  ls -l ${DBSAVED}
  echo "Continuing anyway in 20 seconds."
  echo "Kill this now if you want to do something about the partial checkpoints."
  sleep 20
fi

if [ -s ${DBCHECK} ]; then
  echo "Moving ${DB} to ${DB}.2 and ${COMPRESS}ing it"
  mv ${DB} ${DB}.2
  ${COMPRESS} ${DB}.2 &
  echo "Moving ${DBCHECK} to ${DB}"
  mv ${DBCHECK} ${DB}
else
  echo "No checkpoint file: ${DBCHECK}"
  echo "This is probably bad unless this is the first time you've brought"
  echo "up this db."
  sleep 5
fi

if [ -f ${LOG} ]; then
   NOW=`date +%b%d%Y-%H%M`   
   BIGLOG=${LOGDIR}/${DBNAME}-${NOW}.log
   echo "Moving ${LOG} to ${BIGLOG}.."
   mv ${LOG} ${BIGLOG}
   bzip2 ${BIGLOG} &
fi

echo -n > ${LOG}

rm -f ${PIDFILE}
echo "Starting ${DB} on ${PORT}..."
( 
  ${MOO} -l ${LOG} ${DB} ${DBCHECK} +O ${PORT}  2> ${LOG}.errors &
  PID="$!"
  echo ${PID} > ${PIDFILE}
  ${WATCH_CHECKPOINTS} --log ${LOG} --db ${DBCHECK} --run ${DBNEW} --pattern "${DBNAME}-%b%d%Y-%H%M.db.bz2" ${DBDIR} 2> ${LOG}.watch.errors &
  WPID="$!"
  wait ${PID}
  rm -f ${PIDFILE}
  kill ${WPID}
  wait ${WPID}
) &




USER=unconfigured

MOODIR=.

#
# Location of your MOO binary.
#

MOO=./moo

#
# Base name of your database (without the .db)
#

DBNAME=Unconfigured

#
# Name of the log file for the currently running MOO process.
#

LOG=${DBNAME}.log.current

#
# Persistant log file -- this will contain the entire log.
#

BIGLOG=${DBNAME}.log

#
# The port your MOO runs on.
#

PORT=8888

#
# umask for the MOO process.  077 means "only let this user read or write it"
#

UMASK=077

#
# Number of rotations to keep of the database.
#

BACKUPS=4

#
# Program to gzip the database.
#

COMPRESS=gzip

#
# Suffix for files compressed with above program.
#

COMPRESS_SUFFIX=gz

#
# It will wait up to this many seconds for the server to exit
# after sending the shutdown signal before deciding something is wrong.
# (default) 600 seconds = 10 minutes

SHUTDOWN_TIMEOUT=600


#
# You shouldn't have to modify anything under here.
#

cd ${MOODIR}

umask ${UMASK}
DB=${DBNAME}.db
DBCHECK=${DB}.checkpoint
PIDFILE=${DBNAME}.pid

if [ "$1" = "-h" -o "$#" -ne 1 ]; then
   echo "Usage: $0 [start|stop]"
   exit 1
fi

if [ "${DBNAME}" = "Unconfigured" ]; then
  echo "$0 has not been configured."
  echo "Please edit it and set the variables for your setup."
  exit 1
fi

if [ "$1" = "stop" ]; then
   if [ -f ${PIDFILE} ]; then
      PID=`cat ${PIDFILE}`  
      echo "Sending SIGUSR1 (shutdown) to ${PID}..."
      if ! /bin/kill -USR1 ${PID}; then
         echo No moo process found.
         exit 1
      fi 
      TIMER=${SHUTDOWN_TIMEOUT}
      echo -n "Waiting for ${DBNAME} to finish exiting.."
      while [ ${TIMER} -gt 1 -a -f ${PIDFILE} ]; do
         echo -n .
         sleep 5
         TIMER=`expr ${TIMER} - 5`
      done 
      if [ -f ${PIDFILE} ]; then
         echo timeout.
         exit 1
      else
         echo done.
         exit 0
      fi
  else  
     echo No ${PIDFILE} file, perhaps the moo is not running?
  fi
  exit 1
elif [ ! "$1" = "start" ]; then
  echo "Usage: $0 [start|stop]"
  exit 1
fi



#
# Check for already running...
#
if [ -s ${PIDFILE} ]; then
   PID=`cat ${PIDFILE}`
	echo "Warning! PID file already exists ($PID)."
   echo "MOO might already be running."
   echo 
   echo "Continuing anyway in 10 seconds...."
   sleep 10
fi


#
# Check for partial checkpoints
#
DBSAVED=`echo ${DBCHECK}.\#*\#`
if [ "${DBSAVED}" != "${DBCHECK}.#*#" ]; then
  echo "Warning!  Partial checkpoint files exist:"
  ls -l ${DBSAVED}
  echo "Continuing anyway in 20 seconds."
  echo "Kill this now if you want to do something about the partial checkpoints."
  sleep 20
fi

if [ -s ${DB} -a -s ${DBCHECK} ]; then
  # rotate count prefix suffix
  B=`expr ${BACKUPS} - 1`
  CS=${COMPRESS_SUFFIX}
  while [ ${B} -gt 1 ]; do
    if [ -s ${DB}.${B}.${CS} ]; then
      NEW=`expr $B + 1`
      echo "Moving ${DB}.${B}.${CS} to ${DB}.${NEW}.${CS}"
      mv ${DB}.${B}.${CS} ${DB}.${NEW}.${CS}
    fi
    B=`expr ${B} - 1`
  done
fi

if [ -s ${DBCHECK} ]; then
  echo "Moving ${DB} to ${DB}.2 and ${COMPRESS}ing it"
  mv ${DB} ${DB}.2
  ${COMPRESS} ${DB}.2 &
  echo "Moving ${DBCHECK} to ${DB}"
  mv ${DBCHECK} ${DB}
else
  echo "No checkpoint file: ${DBCHECK}"
  echo "This is probably bad unless this is the first time you've brought"
  echo "up this db."
  sleep 5
fi

if [ -f ${LOG} ]; then
  echo "Appending ${LOG} to ${BIGLOG}"
  cat ${LOG} >> ${BIGLOG}
fi

echo -n > ${LOG}

rm -f ${PIDFILE}
echo "Starting ${DB} on ${PORT}..."
( 
  ${MOO} -l ${LOG} ${DB} ${DBCHECK} ${PORT}  2> ${LOG}.errors &
  PID="$!"
  echo ${PID} > ${PIDFILE}
  wait ${PID}
  rm -f ${PIDFILE}
) &
