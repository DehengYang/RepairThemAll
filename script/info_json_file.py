import os
import subprocess
import argparse
import json
import shutil
from xml.etree.ElementTree import parse

from config import WORKING_DIRECTORY
from core.utils import get_benchmark

parser = argparse.ArgumentParser(prog="info_json_file", description='Get info json file')
parser.add_argument("--benchmark", "-b", required=True, default="Defects4J",
                        help="The benchmark to repair")
parser.add_argument("--id", "-i", help="The bug id")

if __name__ == "__main__":
    '''
    This is to write basic information of a benchmark bug into json 
    '''
    # receive parameters
    args = parser.parse_args()
    cmd = "mkdir %s" % os.path.join(WORKING_DIRECTORY, 'testResults')
    # mkdir /mnt/workingDir/testResults
    subprocess.call(cmd, shell=True)
    
    args.benchmark = get_benchmark(args.benchmark)

    # if has id, then only focus on currect id, otherwise using the whole bug set.
    bugs = args.benchmark.get_bugs()
    if args.id is not None:
        bugs = []
        bugs.append(args.benchmark.get_bug(args.id))

    for bug in bugs:
        # bug path: u'/mnt/workingDir/Bears_webfirmframework-wff_453188520-453188718'
        bug_path = os.path.join(WORKING_DIRECTORY, "%s_%s_%s" % (bug.benchmark.name, bug.project, bug.bug_id))
        # checkout bug
        bug.checkout(bug_path)
        # compile bug
        bug.compile()
        # run tests
        bug.run_test()

        reportFiles = []
        # traverse bug_path dir to collect reportFiles
        for root, dirs, files in os.walk(bug_path):
            for file in files:
                filePath = os.path.join(root, file)
                if "target/surefire-reports" in filePath and file.endswith('.xml'):
                    reportFiles.append(filePath)

        passingTests = 0
        failingTests = 0
        erroringTests = 0
        failureDetails = []
        # parse reportFiles 
        for xmlFile in reportFiles:
            print xmlFile
            with open(xmlFile, 'r') as file:
                xmlTree = parse(file)
                # get all test cases
                testCases = xmlTree.findall('testcase')
                for testCase in testCases:
                    failureDetail = {}
                    failureDetail['testClass'] = testCase.attrib['classname']
                    failureDetail['testMethod'] = testCase.attrib['name']
                    
                    # get failure
                    failure = testCase.findall('failure') # return a list
                    if len(failure) > 0:
                        failingTests += 1  # add 1 failed test
                        failureDetail['failureName'] = failure[0].attrib['type']
                        if 'message' in failure[0].attrib:
                            failureDetail['detail'] = failure[0].attrib['message']
                        failureDetail['isError'] = False
                        failureDetails.append(failureDetail)
                    else:
                        error = testCase.findall('error')
                        # is an error
                        if len(error) > 0:
                            erroringTests += 1
                            failureDetail['failureName'] = error[0].attrib['type']
                            if 'message' in error[0].attrib:
                                failureDetail['detail'] = error[0].attrib['message']
                            failureDetail['isError'] = True
                            failureDetails.append(failureDetail)
                        # is a passing test
                        else:
                            passingTests += 1

        jsonFile = {}
        jsonFile['benchmark'] = bug.benchmark.name # 'Bears'
        jsonFile['bugId'] = bug.bug_id # '453188520-453188718'

        repository = {}
        repository['name'] = bug.project # u'webfirmframework-wff'
        jsonFile['repository'] = repository #{ 'name': u'webfirmframework-wff'}

        if bug.benchmark.name == 'Defects4J' or bug.benchmark.name == 'Bugs.jar' or bug.benchmark.name == 'Bears': 
            projectInfo = bug.benchmark._get_project_info(bug)
            projectMetrics = {}
            if projectInfo is not None:
                projectMetrics['numberModules'] = len(projectInfo['modules'])
            jsonFile['projectMetrics'] = projectMetrics

        tests = {}
        overallMetrics = {}
        overallMetrics['numberPassing'] = passingTests # 1922
        overallMetrics['numberRunning'] = passingTests + failingTests + erroringTests # 1924
        overallMetrics['numberFailing'] = failingTests # 2
        overallMetrics['numberErroring'] = erroringTests
        tests['overallMetrics'] = overallMetrics
        tests['failureDetails'] = failureDetails
        jsonFile['tests'] = tests
        
        # write to /mnt/workingDir/testResults/Bears_webfirmframework-wff_453188520-453188718.json
        with open(os.path.join(WORKING_DIRECTORY, 'testResults', "%s_%s_%s" % (bug.benchmark.name, bug.project, bug.bug_id) + '.json'), 'w') as f:
            f.write(json.dumps(jsonFile, indent=2))

        # print to console
        print(json.dumps(jsonFile, indent=1, sort_keys=True))
        
        # rm buggy program dir in /mnt/workingDir
        shutil.rmtree(bug_path)
    