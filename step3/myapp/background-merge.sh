#!/bin/bash

LANG=C

set -e

# tag::config[] Directory in which raw PGO profiles are stored
# NOTE: Normally PGO raw profiles are stored in the location where the
# instrumented binary is invoked. We make the assumption that all profiles are
# stored in the same directory.
# See %t here:
# https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
profile_dir=$1

# The final merge target
target_merge_file=$2

# Process ID file where this background job stores its PID
pid_file=/tmp/background-merge.pid

# Log file for this program
log_file=/tmp/background-merge.log

# Sleep for this amound of seconds whenever there's nothing to do.
sleep_interval=0.1
# end::config[]

# Temporary files to store a sorted list of PGO profiles
profiles=/tmp/profiles.txt
profiles_in_use=/tmp/profiles_in_use.txt

# tag::catch_sigterm[]
signal_caught=0
function catch_sigterm() {
    echo "Caught signal!"
    signal_caught=1
}
# end::catch_sigterm[]

# tag::do_sleep[]
function do_sleep() {
    echo "Sleeping for $sleep_interval second(s)."
    sleep $sleep_interval
}
# end::do_sleep[]

# tag::main[]
function main()
{
    while true; do
        # Graceful shutdown
        if [ $signal_caught -gt 0 ]; then
            echo "Exiting background merge..."
            echo "Deleting PID file $pid_file."
            rm -fv $pid_file
            exit 0
        fi

        # tag::gather_profiles[]
        # Gather profiles
        find $profile_dir -type f 2>/dev/null > $profiles
        sort -o $profiles $profiles
        # end::gather_profiles[]

        # Get profiles in use in the profiles directory. Anything listed here is
        # potentially being written to by clang, clang++ or ldd. Hence, we'll
        # leave those files alone.
        # tag::get_profiles_in_use[]
        lsof -Fn +d $profile_dir | grep ^n/ | sort > $profiles_in_use
        # Remove n/ prefix
        sed -i -s 's/^n\//\//g' $profiles_in_use
        # end::get_profiles_in_use[]

        # tag::get_ready_profiles[]
        # Get distinct profiles that are not overlapping with the ones in use
        profiles_not_in_use=$(comm -13 $profiles_in_use $profiles)
        # end::get_ready_profiles[]
        if [[ "$profiles_not_in_use" != "" ]]; then
            # tag::merge[]
            echo "Merging and then deleting these profiles: $profiles_not_in_use"
            # llvm-profdata itself is instrumented as well so we need to
            # tell it where to write its own profile data.
            export TMPDIR=$profile_dir
            export LLVM_PROFILE_FILE="%t/llvm-profdata.clang.%m.%p.profraw"
            llvm-profdata merge \
                --compress-all-sections \
                --sparse \
                 $profiles_not_in_use \
                -o $target_merge_file
            # IMPORTANT: Free up disk space!
            rm -f $profiles_not_in_use
            # end::merge[]
        fi
        
        do_sleep
    done
}
# end::main[]

# tag::setup[]
function setup() {
    # It is important that the trap is set up in main because main is send to
    # the background. To trigger the trap, run: kill -s TERM <PID>, where <PID>
    # is the process ID of the background job in which "main" is running.
    trap catch_sigterm SIGTERM

    # Handle if PID file exists and whether process is still running or not.
    if [ -e $pid_file ]; then
        if [ `ps -q $(cat $pid_file)` ]; then
            echo "ERROR: PID file already in use: $pid_file"
            echo "Once you're done, kill job with: kill -s SIGTERM \$(cat $pid_file)"
            exit 1
        else
            echo "Process is no longer running: $(cat $pid_file). Removing file $pid_file."
            rm -f $pid_file
        fi
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

setup

main > $log_file 2>&1