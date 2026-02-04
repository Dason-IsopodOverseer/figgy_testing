"""
This module contains default checks built as compositions of core classes.

Please continue using DocStrings.

Author: Dason Wang
"""

from Core import *
import os
from gemfileparser import GemfileParser

def parseGEMDep(file):
    """
    Parses and returns gemfile as dict, using gemfileparser
    """
    parser = GemfileParser(file)
    dependency_dictionary = parser.parse()
    return dependency_dictionary
    
def getVersionFromRuby(file):
    """
    Reads a .ruby_version file and returns the version
    """
    with open(file) as f:
        contents = f.read().strip()
        return contents

def getDependenciesFromGemfile(file):
    """
    Reads a Gemfile and returns a list of all dependencies
    """
    gemfile_data = parseGEMDep(file)
    # Extract gem names from GemInfo objects in the 'runtime' section
    if 'runtime' in gemfile_data:
        # Each item in the list is a GemInfo object, we need the name attribute
        return [gem_info.name for gem_info in gemfile_data['runtime']]
    return []

# Ruby Check
class RubyCheck(File_Existence_Check):
    """
    Ruby Check, can find specific ruby version and dependencies
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
        # locate and extract ruby version, dependencies from .ruby-version and Gemfile
        rubyVersionFile = os.path.join(self.parentdir, ".ruby-version")
        gemfile = os.path.join(self.parentdir, "Gemfile")
        
        # Get Ruby version if .ruby-version file exists
        rubyVer = ""
        if os.path.exists(rubyVersionFile):
            rubyVer = getVersionFromRuby(rubyVersionFile)
        
        # Get dependencies
        listedDep = []
        if os.path.exists(gemfile):
            listedDep = getDependenciesFromGemfile(gemfile)
        
        # initiate the concrete base class to be wrapped, which must evaluate to a result (use parent)
        start = super()

        # perform a version check
        checkVersion = Decorator_Version_Check(start, self.project_root, rubyVer, self.min_ver, self.max_ver)

        # perform a dependency check
        checkDependencies = Decorator_Dependencies_Check(checkVersion, self.project_root, listedDep, self.dep)

        return checkDependencies.result()
