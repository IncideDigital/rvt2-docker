# Build

Build the docker image from the root of the repository with:

```
cd build
git clone https://github.com/IncideDigital/rvt2.git rvt2
cd rvt2
git submodule init
git submodule update
cd ..
docker build -t incide/rvt2-base:latest -f Dockerfile.base .
docker build -t incide/rvt2-tools:latest -f Dockerfile.tools .
docker build -t incide/rvt2:latest -f Dockerfile .
```

- `rvt2:base` contains most of the dependencies (python, libraries...) and acts as a base system for the rvt2.
- `rvt2:tools` contains external tools that are not in Debian repositories and must be updated and built manually.
- `rvt2:latest` includes the rvt2.

The split allows building new images for rvt2 fast by reusing
the first images and only rebuilding the third one after a change is made to rvt2.

# Usage

A script called `rvt2` is provided to use rvt2 in a docker container.  The script accepts the following parameters:

- `./rvt2 start`: Start the rvt2 docker container.
- `./rvt2 stop`: Stop the rvt2 docker container.  This will delete all unsaved
  data (that is, everything outside of `/mnt/images` and `/mnt/morgue` inside
  the container).
- `./rvt2 shell`: Get a bash shell running on user rvt inside the rvt2 running
  container.  Use this to use rvt2.
- `./rvt2 root`: Get a bash root shell inside the rvt2 running container.  Use
  this for testing.
- `./rvt2 export`: Save the image rvt2:latest in a file named
  rvt2:latest.tar.gz. History and layers are included.  You can import this
  image using: `zcat rvt2:latest.tar.gz | docker import - rvt2:latest`
- `./rvt2 --casename 12345 --source 01 --params arg=2 -- otherpath` (i.e: any
  other thing): run the command in docker.

The script `./rvt2` contains some variables to define paths for the imagedir and morgue, change them as you see fit. Default values:

- *morgue*: a directory `morgue` in the current dir. It will be created if if doesn't exist. Mapped to `/morgue`.
- *images*: a directory `images` in the current dir. It will be created if if doesn't exist. Mapped to `/morgue/images`.
- *addons*: a directory `addons` in the current dir. It will be created if it doesn't exist. Mapped to `/opt/rvt2/addons`.
- *local.cfg*: local configuration. Mapped to `/opt/rvt2/config/local.cfg`.
