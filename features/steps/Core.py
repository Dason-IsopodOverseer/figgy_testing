"""
This module contains core system components:
- class definitions
- plugin architecture

All checker classes and their implementations should be defined in this file
to maintain organized and modular code structure. Please continue using DocStrings.

Author: Dason Wang
"""

from abc import ABC
import os

# import cchardet # speeds up encoding detection
# import re # regular expressions
# from difflib import SequenceMatcher
# from bs4 import BeautifulSoup

def fcrawl(current_working_dir, fullpath:bool = False):
    """
    Crawl the project file system.
    Returns a list of all filenames relative to the "dataset" folder as root

    :param current_working_dir: current directory, relative path
    :param fullpath: set to true to define full path
    """
    # found files
    foundF = []
    # Iterate over files in "dataset" directory
    for dirpath, dirnames, filenames in os.walk(current_working_dir):
        # add the path to allFiles
        for filen in filenames:
            currentFile = filen
            if (fullpath):
                currentFile = os.path.relpath(os.path.join(dirpath, filen), current_working_dir)      
            foundF.append(currentFile)
    return foundF

def SemanticVersionComparator(v1:str, v2:str):
    """
    Performs a check on npm semantic versioning, see https://semver.org/
    returns true only if v2 >= v1
    
    :param v1: expected version, should be less than or equal to v2
    :type v1: str
    :param v2: working version, should be greater than v1
    :type v2: str
    """
    v1s = v1.split(".")
    v2s = v2.split(".")
    for s1,s2 in zip(v1s, v2s):
        # Replaces ~ and x
        s1,s2 = (x.replace("~", "").replace("x", "9999") for x in (s1, s2))
        terminate = False
        # increments version for compatible ^
        if ('^' in s1):
            s1 = str(int(s1.replace("^", ""))+1)
            terminate = True
        if ('^' in s2):
            s2 = str(int(s2.replace("^", ""))+1)
            terminate = True
        if (int(s2) > int(s1)):
            return True
        elif (int(s2) < int(s1)):
            return False
        if(terminate):
            return True
    return True

# All checks that inherit from this must
# implement a "result" method which performs the check
class ADR_Check(ABC):
    """
    Interface for Architectural Decision Record checks
    """
    def __init__(self, project_root:str) -> None:
        # project existence handled here
        if not os.path.exists(project_root):
            raise Exception("No project directory specified.")
        self.root = project_root
        pass
    
    def result(self) -> bool:
        return False

class File_Existence_Check(ADR_Check):
    """ 
    Architectural Decision Record Check for File Existence
    """
    def __init__(self, project_root:str, filename:str, filetype:str, parentdir:str="") -> None:
        self.filename = filename
        self.filetype = filetype
        self.parentdir = project_root if parentdir == "" else parentdir
        super().__init__(project_root)

    def result(self) -> bool:
        considered_files = fcrawl(self.parentdir)
        target_file = self.filename if self.filetype == "" else self.filename + "." + self.filetype
        return target_file in considered_files
    
class Version_Check(ADR_Check):
    """
    Architectural Decision Record to support limited versions
    """
    def __init__(self, project_root:str, current_version:str="", min_version:str="", max_version:str="", versioning_scheme:int=0) -> None:
        self.current_version = current_version
        self.min_version = min_version
        self.max_version = max_version
        self.versioning_scheme = versioning_scheme
        super().__init__(project_root)

    def result(self) -> bool:
        if self.min_version == "" and self.max_version == "":
            return True
        elif self.current_version == "":
            return True
        else:
            match self.versioning_scheme:
                case 0: # semver, for npm
                    at_least_compatible = SemanticVersionComparator(self.min_version, self.current_version) if self.min_version != "" else True
                    at_most_compatible = SemanticVersionComparator(self.current_version, self.max_version) if self.max_version != "" else True
                    #  true only when min <= current_version <= max
                    return at_least_compatible and at_most_compatible
                case _:
                    raise Exception("Incompatible versioning scheme.")
            
class Decorator_Version_Check(Version_Check):
    """
    Decorator
    Architectural Decision Record to support limited versions
    """
    def __init__(self, wrappee:ADR_Check, *args, **kwargs) -> None:
        self.wrappee=wrappee
        super().__init__(*args, **kwargs)
    
    def result(self) -> bool:
        if not super().result():
            print("-> Versioning Check Failed")
        return super().result() and self.wrappee.result()
            
class Dependencies_Check(ADR_Check):
    """
    Architectural Decision Record to support a roster of dependencies, and their versions
    """
    def __init__(self, project_root:str, dependencies, expected_dep) -> None:
        self.dependencies = dependencies
        self.expected_dep = expected_dep
        self.missing_dep = []
        super().__init__(project_root)
    
    def getMissing(self) -> list:
        return self.missing_dep

    def result(self) -> bool:
        set_dep = set(self.dependencies)
        set_exp = set(self.expected_dep)
        if not set_exp.issubset(set_dep):
            self.missing_dep += set_exp.difference(set_dep)
            return False
        return True
        
class Decorator_Dependencies_Check(Dependencies_Check):
    """
    Decorator
    Architectural Decision Record to support a roster of dependencies, and their versions
    """
    def __init__(self, wrappee:ADR_Check, *args, **kwargs) -> None:
        self.wrappee = wrappee
        super().__init__(*args, **kwargs)
    
    def result(self) -> bool:
        if not super().result():
            print(f"-> Dependency Check Failed, missing the following packages: {super().getMissing()}")
        return super().result() and self.wrappee.result()
        
# class File_Contents_Check(ADR_Check):
#     """ 
#     Architectural Decision Record Check for File Contents
#     """
#     def __init__(self,  project_root:str, filepath:str, match:str) -> None:
#         self.filepath = filepath
#         super().__init__(project_root)

#     def result(self) -> bool:
