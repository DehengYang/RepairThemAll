import collections
import json
import os
import re
import subprocess
from sets import Set

from config import DATA_PATH, JAVA7_HOME
from config import REPAIR_ROOT
from core.Benchmark import Benchmark
from core.Bug import Bug
from core.utils import add_benchmark

FNULL = open(os.devnull, 'w')


class Defects4J(Benchmark):
    """Defects4j Benchmark"""

    def __init__(self):
        super(Defects4J, self).__init__("Defects4J")
        self.path = os.path.join(REPAIR_ROOT, "benchmarks", "defects4j")
        self.project_data = {}
        self.bugs = None
        self.get_bugs()

    def get_data_path(self):
        return os.path.join(DATA_PATH, "benchmarks", "defects4j")

    def get_bug(self, bug_id):
        separator = "-"
        if "_" in bug_id:
            separator = "_"
        (project, id) = bug_id.split(separator)
        for bug in self.get_bugs():
            if bug.project.lower() == project.lower():
                if int(bug.bug_id) == int(id):
                    return bug
        return None

    def get_bugs(self):
        if self.bugs is not None:
            return self.bugs
        self.bugs = []
        data_defects4j_path = self.get_data_path()
        for project_data in os.listdir(data_defects4j_path):
            project_data_path = os.path.join(data_defects4j_path, project_data)
            if not os.path.isfile(project_data_path):
                continue
            with open(project_data_path) as fd:
                data = json.load(fd)
                self.project_data[data['project']] = data
                for i in range(1, data['nbBugs'] + 1):
                    bug = Bug(self, data['project'], i)
                    bug.project_data = data
                    self.bugs += [bug]
        return self.bugs

    def _get_benchmark_path(self):
        return os.path.join(self.path, "framework", "bin")

    def checkout(self, bug, working_directory):
        # u'export PATH="/home/apr/env/jdk1.7.0_80/bin/
        # :/mnt/recursive-repairthemall/RepairThemAll/script/../benchmarks/defects4j/framework/bin
        # :$PATH";
        # export JAVA_HOME="/home/apr/env/jdk1.7.0_80/bin/..";
        # \ndefects4j checkout -p Mockito -v 35b -w /mnt/workingDir/Defects4J_Mockito_35;\n'
        cmd = """export PATH="%s:%s:$PATH";export JAVA_HOME="%s";
defects4j checkout -p %s -v %sb -w %s;
""" % (JAVA7_HOME,
       self._get_benchmark_path(),
       os.path.join(JAVA7_HOME, '..'),
       bug.project,
       bug.bug_id,
       working_directory)
        subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        pass

    def compile(self, bug, working_directory):
        cmd = """export PATH="%s:%s:$PATH";export JAVA_HOME="%s";
export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
cd %s;
defects4j compile;
""" % (JAVA7_HOME,
       self._get_benchmark_path(),
       os.path.join(JAVA7_HOME, '..'),
       working_directory)
        subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        pass

    def run_test(self, bug, working_directory):
        cmd = """export PATH="%s:%s:$PATH";export JAVA_HOME="%s";
export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; 
cd %s;
defects4j test;
""" % (JAVA7_HOME,
       self._get_benchmark_path(),
       os.path.join(JAVA7_HOME, '..'),
       working_directory)
        subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        pass

    def failing_tests(self, bug):
        # u'export PATH="/home/apr/env/jdk1.7.0_80/bin/:
        # /mnt/recursive-repairthemall/RepairThemAll/script/../benchmarks/defects4j/framework/bin:$PATH";
        # export JAVA_HOME="/home/apr/env/jdk1.7.0_80/bin/..";
        # \nexport _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
        # \ndefects4j info -p Mockito -b 35;\n'
        cmd = """export PATH="%s:%s:$PATH";export JAVA_HOME="%s";
export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
defects4j info -p %s -b %s;
""" % (JAVA7_HOME,
       self._get_benchmark_path(), 
       os.path.join(JAVA7_HOME, '..'),
       bug.project, 
       bug.bug_id)
        info = subprocess.check_output(cmd, shell=True, stderr=FNULL)

        # filter test cases in same test.java, e.g., Mockito 35 has 4 failed cases, 
        # but only 1 failing test
        tests = Set()
        reg = re.compile('- (.*)::(.*)')
        m = reg.findall(info)
        for i in m:
            tests.add(i[0])
        return list(tests)

    def source_folders(self, bug):
        sources = self.project_data[bug.project]["src"]
        sources = collections.OrderedDict(sorted(sources.items(), key=lambda t: int(t[0])))

        source = None
        for index, src in sources.iteritems():
            if bug.bug_id <= int(index):
                source = src['srcjava']
                break
        return [source]

    def test_folders(self, bug):
        sources = self.project_data[bug.project]["src"]
        sources = collections.OrderedDict(sorted(sources.items(), key=lambda t: int(t[0])))

        source = None
        for index, src in sources.iteritems():
            if bug.bug_id <= int(index):
                source = src['srctest']
                break
        return [source]

    def bin_folders(self, bug):
        sources = self.project_data[bug.project]["src"]
        sources = collections.OrderedDict(sorted(sources.items(), key=lambda t: int(t[0])))
        source = None
        for index, src in sources.iteritems():
            if bug.bug_id <= int(index):
                source = src['binjava']
                break
        return [source]

    def test_bin_folders(self, bug):
        sources = self.project_data[bug.project]["src"]
        sources = collections.OrderedDict(sorted(sources.items(), key=lambda t: int(t[0])))

        source = None
        for index, src in sources.iteritems():
            if bug.bug_id <= int(index):
                source = src['bintest']
                break
        return [source]

    def classpath(self, bug):
        classpath = ""
        workdir = bug.working_directory

        sources = self.project_data[bug.project]["classpath"]
        sources = collections.OrderedDict(sorted(sources.items(), key=lambda t: int(t[0])))
        # add classpath in buggy dir, e.g., target/ in Mokcito-35
        for index, cp in sources.iteritems():
            if bug.bug_id <= int(index):
                for c in cp.split(":"):
                    if classpath != "":
                        classpath += ":"
                    classpath += os.path.join(workdir, c)
                break
        for (root, _, files) in os.walk(os.path.join(workdir, "lib")):
            for f in files:
                if f[-4:] == ".jar":
                    classpath += ":" + (os.path.join(root, f))
        libs = []
        cmd = """export PATH="%s:%s:$PATH";export JAVA_HOME="%s";
        cd %s;
        defects4j export -p cp.test 2> /dev/null;
        """ % (JAVA7_HOME, 
        self._get_benchmark_path(), 
        os.path.join(JAVA7_HOME, '..'),
        bug.working_directory)
        libs_split = subprocess.check_output(cmd, shell=True, stderr=FNULL).split(":")
        for lib_str in libs_split:
            lib = os.path.basename(lib_str)
            if lib[-4:] == ".jar":
                libs.append(lib)
        libs_path = os.path.join(self.path, "framework", "projects", bug.project, "lib")
        for (root, _, files) in os.walk(libs_path):
            for f in files:
                if f in libs:
                    classpath += ":" + (os.path.join(root, f))
        libs_path = os.path.join(self.path, "framework", "projects", "lib")
        for (root, _, files) in os.walk(libs_path):
            for f in files:
                if f in libs:
                    classpath += ":" + (os.path.join(root, f))

        return classpath


    def compliance_level(self, bug):
        return self.project_data[bug.project]["complianceLevel"][str(bug.bug_id)]["source"]

add_benchmark("Defects4J", Defects4J)