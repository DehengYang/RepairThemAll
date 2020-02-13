FROM tdurieux/astor

RUN apt-get install -y time
# install jdk using PPA. Refer to https://itsfoss.com/ppa-guide/
# repositories are found in /etc/apt/sources.list.d/
RUN add-apt-repository ppa:openjdk-r/ppa

# add and remove repositories (such as PPAs) automatically
RUN apt-get install -y software-properties-common

# update source
RUN apt-get -o Acquire::Check-Valid-Until=false update; exit 0

# 1) fix-missing -> ignore missing; 2) -f --force-yes -> skip interaction with all yes
RUN apt-get install --fix-missing -y -f --force-yes openjdk-7-jdk

# jessie means old stable Debian vesion (i.e., Debian 8)
RUN echo "deb [check-valid-until=no] http://cdn-fastly.deb.debian.org/debian jessie main" > /etc/apt/sources.list.d/jessie.list
RUN sed -i '/deb http:\/\/deb.debian.org\/debian jessie-updates main/d' /etc/apt/sources.list
RUN echo "deb http://ftp.us.debian.org/debian unstable main contrib non-free" >> /etc/apt/sources.list.d/unstable.list

# update
RUN apt-get -o Acquire::Check-Valid-Until=false update; exit 0
RUN apt-get install --fix-missing -y --force-yes -f build-essential

# install runner
COPY .git /.git
COPY repair_tools /repair_tools
COPY libs /libs
RUN rm -rf libs/z3/build
COPY data /data
COPY init.sh /init.sh 
COPY benchmarks /benchmarks
COPY script /script

RUN /init.sh

# Please refer to the following pages for understanding ENTRYPOINT
# Docker ENTRYPOINT 笔记 -> https://blog.csdn.net/oscarun/article/details/96698023
# Docker: 精通ENTRYPOINT指令 -> https://blog.csdn.net/Hdnrnfgf/article/details/84770720
ENTRYPOINT [ "script/repair.py" ]
