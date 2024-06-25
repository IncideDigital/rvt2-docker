FROM incide/rvt2-tools:latest

# Copy rvt2
USER root
COPY rvt2/ /opt/rvt2
COPY ./server /opt/rvt2-server
COPY rvt2/setup.sh /tmp

# setup the bash shell for user rvt
# install server dependencies
# configure the last bits of rvt2
RUN echo "PS1='\u@\h [rvt2] \w\\n \$ '" >> /home/rvt/.bashrc && \
    echo "export LC_ALL=C.UTF-8" >> /home/rvt/.bashrc && \
    echo "export LANG=C.UTF-8" >> /home/rvt/.bashrc && \
    ln -s /opt/rvt2/rvt2 /usr/bin/rvt2 && \
    rm -rf /opt/rvt2/.git

RUN . /tmp/setup.sh && install_pip_deps

WORKDIR /morgue

# Set an entrypoint that will do a clean-up when the container is stopped
ENTRYPOINT ["/opt/rvt2-server/docker-entrypoint.sh"]
