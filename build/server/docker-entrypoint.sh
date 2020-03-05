#!/bin/bash

# This script serves as a docker-entrypoint and seves two purposes:
# - Keep the docker container up by being a process that never ends by itself.
# - Perform clean-up actions when the docker container is stopped.

# RVT2 requires mounting images inside the docker container.  If the docker
# container is stopped while mounts are active, the container will hang and
# mount will never be unmounted unless you reboot the host.  This function
# unmounts the filesystems automatically upon termination of the docker
# container, among other things.
term_handler() {
    echo "Terminate on `date`"
    echo "> Unmounting filesystems ..."
    umount -a -d -r -t notmpfs,nosysfs,nodevtmpfs,noproc,nodevpts >/dev/null
    echo "> Terminating init children processes ..."
    [[ -z "$(jobs -p)" ]] || kill $(jobs -p)
    running=0
}

echo "Init on `date`"
trap 'term_handler' HUP INT QUIT TERM

#$@
#term_handler

running=1

while true; do
    if [ "$running" = "1" ]; then
        python3 /opt/rvt2-server/rvt2-server.py /opt/rvt2-server/rvt2-server.cfg
    else
        break
    fi
done
