"""
This module contains default checks built as compositions of core classes.

Please continue using DocStrings.

Author: Dason Wang
"""

from Core import *
import os
import json

def parseJSON(file):
    """
    Parses and returns json, default settings
    """
    with open(file) as f:
        d = json.load(f)
        return d
    
def getVersionFromJson(file, targetCategory:str, targetName:str):
    """
    Reads a json file and returns the version of the target dependency, engine, or script; returns empty string if no version specified
    """
    packagejson = parseJSON(file)
    if targetCategory in packagejson:
        if (targetName in packagejson[targetCategory].keys()):
            projectV = packagejson[targetCategory][targetName]
            return projectV
    return ''

def getDependenciesFromJson(file):
    """
    Reads a json file and returns a list of all non-dev dependencies
    """
    packagejson = parseJSON(file)
    return packagejson["dependencies"].keys()

# Node.js Check
class NodeJSCheck(File_Existence_Check):
    """
    Node.js Check, can find specific version and dependencies
    Inherits from File_Existence_Check
    """
    def __init__(self, project_root:str, filename:str, filetype:str, 
                 parentdir:str="", min_version:str="", max_version:str="", dependencies=[]) -> None:
        self.project_root = project_root
        self.min_ver = min_version
        self.max_ver = max_version
        self.dep = dependencies
        super().__init__(project_root, filename, filetype, parentdir)
    
    def result(self) -> bool:
        # locate and extract node version, dependencies from package.json
        target_file = self.filename if self.filetype == "" else self.filename + "." + self.filetype
        packageFile = os.path.join(self.parentdir, target_file)
        nodeVer = getVersionFromJson(packageFile, 'engines', 'node')
        listedDep = getDependenciesFromJson(packageFile)
        
        # initiate the concrete base class to be wrapped, which must evaluate to a result (use parent)
        start = super()

        # perform a version check
        checkVersion = Decorator_Version_Check(start, self.project_root, nodeVer, self.min_ver, self.max_ver)

        # perform a dependency check
        checkDependencies = Decorator_Dependencies_Check(checkVersion, self.project_root, listedDep, self.dep)

        return checkDependencies.result()
    
    def checkPrettier(self) -> bool:
        # locate and extract node version, dependencies from package.json
        packageFile = os.path.join(self.parentdir, self.filename + "." + self.filetype)
        nodeVer = getVersionFromJson(packageFile, 'devDependencies', 'prettier')
        listedDep = getDependenciesFromJson(packageFile)

        # initiate the concrete base class to be wrapped, which must evaluate to a result (use parent)
        start = super()

        # perform a version check
        checkVersion = Decorator_Version_Check(start, self.project_root, nodeVer, self.min_ver, self.max_ver)

        # perform a dependency check
        checkDependencies = Decorator_Dependencies_Check(checkVersion, self.project_root, listedDep, self.dep)

        return checkDependencies.result()

