#!/bin/bash
# This is a script to run in the background and continously merge
# PGO profile data.

# Author: Konrad Kleine  <kkleine@redhat.com>
# Copyright (c) 2023 Red Hat.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2, or (at your
# option) any later version.

# It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Run this script in the background using.
#
# To gracefully shutdown the background job, write anything to
# <shutdown_file> and wait until <pid_file> is deleted:
#
#     echo "foobar" > $shutdown_file
#     [ -e $pid_file ] && inotifywait -e delete_self $pid_file || true

function show_usage()
{
cat <<EOF
 Usage:
   $0 \\
    -d <observe_dir>
    -r <files_regex>
    -s <min_batch_size>
    -b <batch_file>
    -u <batch_file_in_process>
    -p <pid_file>
    -f <target_merge_file>
    -l <log_file>
    -x <shutdown_file>
    -h;;
EOF
exit 0
}

while getopts "d:r:s:b:u:p:f:l:x:h" flag; do
    case "${flag}"
    in
    d) observe_dir=${OPTARG};;
    r) files_regex=${OPTARG};;
    s) min_batch_size=${OPTARG};;
    b) batch_file=${OPTARG};;
    u) batch_file_in_process=${OPTARG};;
    p) pid_file=${OPTARG};;
    f) target_merge_file=${OPTARG};;
    l) log_file=${OPTARG};;
    x) shutdown_file=${OPTARG};;
    h) show_usage;;
    esac
done

# Handle defaults
# Directory in which raw PGO profiles are stored
# NOTE: Normally PGO raw profiles are stored in the location where the
# instrumented binary is invoked. We make the assumption that all profiles are
# stored in the same directory.
# See %t here:
# https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
observe_dir=${observe_dir:-$PWD}
# Regex for the files to look out for
files_regex=${file_regex:-'.*\.profraw$'}
# Number of files that have to exist before we're processing them.
min_batch_size=${min_batch_size:-10}
# This file acts as to queue up file paths that we want to work on.
batch_file=${batch_file:-$observe_dir/background-merge.batch.txt}
# Once the number of lines in the batch_file reach the min_batch_size we move
# the content of batch_file over to this file and then processing can happen
# while batch_file can collect more files.
batch_file_in_process=${batch_file_in_process:-/tmp/background-merge.batch_in_process.txt}
# File to store the PID of this process. Once this file is deleted, the outer script will 
pid_file=${pid_file:-/tmp/background-merge.pid}
target_merge_file=${target_merge_file:--/tmp/background-merge.target}
log_file=${log_file:-/tmp/background-merge.log}
# Once there's a write event to this file, the program exits gracefully.
shutdown_file=${shutdown_file:-$observe_dir/background-merge.shutdown}

function show_config()
{
cat <<EOF
PGO Background merge starting with this config:

observe_dir             = $observe_dir
files_regex             = $files_regex
min_batch_size          = $min_batch_size
batch_file              = $batch_file
batch_file_in_process   = $batch_file_in_process
pid_file                = $pid_file
target_merge_file       = $target_merge_file
log_file                = $log_file
shutdown_file           = $shutdown_file

EOF
}

# Empty batch_file (if exists) or create batch file.
function empty_batch_file()
{
    truncate -s 0 $batch_file
}

empty_batch_file

# tag::process_batch[]
function process_batch()
{
    # tag::merge[]
    # llvm-profdata itself is instrumented as well so we need to
    # tell it where to write its own profile data.
    # TODO(kwk): Eventually use this in the final merge?
    export TMPDIR=/tmp
    export LLVM_PROFILE_FILE="%t/llvm-profdata.tmp"
    pushd $observe_dir
    llvm-profdata merge \
        --compress-all-sections \
        --sparse \
        `[ -e $target_merge_file ] && echo "$target_merge_file"` \
        $(cat $batch_file_in_process) \
        -o $target_merge_file
    popd
    # IMPORTANT: Free up disk space!
    rm -f $TMPDIR/llvm-profdata.tmp
    # end::merge[]    
}
# end::process_batch[]

function main()
{
    # On every *.profraw file written to in the /tmp directory,
    # write an event line to list of files to process in a batch.
    inotifywait -q -m -o $batch_file -e close_write \
        --format '%f' \
        --include $files_regex \
        $observe_dir > /dev/null 2>&1 &

    # Observe if a new profile was added to the list of the current batch.
    # If the shutdown file was modified, gracefully shutdown.
    inotifywait -q -m -e modify \
        --include "($(basename $batch_file)|$(basename $shutdown_file))" \
        $observe_dir \
    | while read -r directory event filename
    do
        if [ "$filename" = "$(basename $shutdown_file)" ]; then
            echo "Exiting gracefully..."
            rm -f $pid_file
            exit 0
        fi
        batch_size=$(wc -l < $batch_file)
        if [ $batch_size -le 0 ]; then
            # This event happens when we empty the batch file
            continue
        fi
        if [ $batch_size -lt $min_batch_size ]; then
            echo "Batch is still too small: $batch_size must be at least $min_batch_size"
            continue
        fi
        cat $batch_file > $batch_file_in_process
        empty_batch_file
        echo "Processing batch (size: $batch_size) in 5 seconds: "
        cat $batch_file_in_process
        process_batch
        # IMPORTANT: Free up disk space!
        pushd $observe_dir
        rm -fv $(cat $batch_file_in_process)
        popd
    done
}

# tag::setup[]
function setup() {
    # Handle if PID file exists and whether process is still running or not.
    if [ -e $pid_file ]; then
        echo "ERROR: PID file already in use: $pid_file"
        exit 0
    fi

    # Save this PID to a file
    echo $$ > $pid_file

    # Create log backup
    if [ -e $log_file ]; then
        echo "Backing up existing log file: $log_file"
        cp -bv $log_file $log_file.bak
    fi
}
# end::setup[]

show_config
setup

main >> $log_file 2>&1


