#!/usr/bin/bash
# This is a script to run in the background and continously merge
# PGO profile data.
#
# Usage:
#   background-merge \
#    -d <profile_dir> \
#    -p <pid_file> \
#    -f <target_merge_file> \
#    -l <log_file> \
#    -s <sleep_interval>
#
# Then kill with: kill -s TERM $(cat <pid_file>)

LANG=C

set -x

function show_usage()
{
cat <<EOF
 Usage:
   $0 \\
    -d <profile_dir> \\
    -p <pid_file> \\
    -f <target_merge_file> \\
    -l <log_file> \\
    -s <sleep_interval>
EOF
exit 0
}

while getopts "d:p:f:l:s:h" flag; do
    case "${flag}"
    in
    # Directory in which raw PGO profiles are stored
    # NOTE: Normally PGO raw profiles are stored in the location where the
    # instrumented binary is invoked. We make the assumption that all profiles are
    # stored in the same directory.
    # See %t here:
    # https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
    d) profile_dir=${OPTARG};;
    # Process ID file where this background job stores its PID
    p) pid_file=${OPTARG};;
    # The final merge target
    f) target_merge_file=${OPTARG};;
    # Log file for this program
    l) log_file=${OPTARG};;
    # Sleep for this amound of seconds whenever there's nothing to do.
    s) sleep_interval=${OPTARG};;
    h) show_usage;;
    esac
done

# Handle defaults
profile_dir=${profile_dir:-$PWD}
pid_file=${pid_file:-/tmp/background-merge.pid}
target_merge_file=${target_merge_file:-/tmp/background-merge.target}
log_file=${log_file:-/tmp/background-merge.log}
sleep_interval=${sleep_interval:-1}

function show_config()
{
# Print settings
cat <<EOF
PGO Background merge starting with this config:

profile_dir       = ${profile_dir}
pid_file          = ${pid_file}
target_merge_file = ${target_merge_file}
log_file          = ${log_file}
sleep_interval    = ${sleep_interval}

EOF
}

# Temporary files to store a sorted list of PGO profiles
profiles=$PWD/profiles.txt
profiles_in_use=$PWD/profiles_in_use.txt

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
        find $profile_dir -type f 2>/dev/null > $profiles.tmp
        sort -o $profiles $profiles.tmp
        rm -f $profiles.tmp
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
        profiles_not_in_use=$(comm -13 $profiles_in_use $profiles | grep --regexp ".*\.profraw")
        # end::get_ready_profiles[]
        if [[ "$profiles_not_in_use" != "" ]]; then
            # tag::merge[]
            # llvm-profdata itself is instrumented as well so we need to
            # tell it where to write its own profile data.
            # TODO(kwk): Eventually use this in the final merge?
            export TMPDIR=/tmp
            export LLVM_PROFILE_FILE="%t/llvm-profdata.tmp"
            llvm-profdata merge \
                --compress-all-sections \
                --sparse \
                 $profiles_not_in_use \
                -o $target_merge_file
            # IMPORTANT: Free up disk space!
            rm -f $tmp_profile
            rm -f $profiles_not_in_use
            # end::merge[]
        else
            # only wait when no profile was ready yet
            echo "Sleeping for $sleep_interval second(s)."
            sleep $sleep_interval
        fi
    done
}
# end::main[]

# tag::setup[]
function setup() {
    # Handle if PID file exists and whether process is still running or not.
    if [ -e $pid_file ]; then
        echo "ERROR: PID file already in use: $pid_file"
        echo "Once you're done, kill job with: kill -s TERM \$(cat $pid_file)" 
        exit 0
    fi

    signal_caught=0
    trap 'signal_caught=1' SIGTERM

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
main > $log_file 2>&1