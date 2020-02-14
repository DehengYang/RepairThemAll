import os
from os.path import expanduser
from core.Support import getGridTime

# root dir: /mnt/repairthemall/script/..
REPAIR_ROOT = os.path.join(os.path.dirname(__file__), '..')

# data path: /mnt/repairthemall/script/../data
DATA_PATH = os.path.join(REPAIR_ROOT, "data")

# repair tool dir: repair_tools
REPAIR_TOOL_FOLDER = os.path.join(REPAIR_ROOT, "repair_tools")

# work dir: /mnt/workingDir/
WORKING_DIRECTORY = os.path.join("/mnt/workingDir/")

# result dir: results/ (seems it will be created later)
OUTPUT_PATH = os.path.join(REPAIR_ROOT, "results/")

# z3 for nopol: libs/z3/build
Z3_PATH = os.path.join(REPAIR_ROOT, "libs", "z3", "build")

# jdk 7 and 8
# JAVA7_HOME = expanduser("/usr/lib/jvm/java-1.7.0-openjdk-amd64/bin/")
# JAVA8_HOME = expanduser("/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/")
JAVA7_HOME = expanduser("/home/apr/env/jdk1.7.0_80/bin/")
JAVA8_HOME = expanduser("/home/apr/env/jdk1.8.0_202/bin/")
JAVA_ARGS = "-Xmx4g -Xms1g"

# thread number
LOCAL_THREAD = 1
GRID5K_MAX_NODE = 50

##In minutes
TOOL_TIMEOUT = "120"

#Format: HH:MM ## the fuction getGridTime calculates the timeout of the grid taking into account an overhead (expressed as percentage)
GRID5K_TIME_OUT = getGridTime(TOOL_TIMEOUT, overhead=0.33)

