"""Handles all maven related functionality."""

import os
import fnmatch
from subprocess import call


def check_set_cwd(func):
    """Decorator to handle working directory.

    1. Sets the working directory to the maven project folder
    2. Runs the func
    3. Resets the working directory
    """
    def _check_set_cwd(*args):
        orig_path = os.getcwd()
        self = args[0]
        if (orig_path != self.dir):
            os.chdir(self.dir)
        op = func(*args)
        set_cwd(orig_path)
        return op
    return _check_set_cwd


def set_cwd(path):
    """Change working directory to path."""
    os.chdir(path)


class MvnRunner(object):
    """Defines functions to run various maven phases."""

    def __init__(self, project_path, quiet_mode=False):
        """Initialize the object with the path to the mvn project."""
        if (os.path.isabs(project_path)):
            self.dir = project_path
        else:
            self.dir = '/'.join([os.getcwd(), project_path])

        self.quiet_mode = quiet_mode

    def set_quiet_mode(self, toggle):
        """Set whether quiet mode to True or False."""
        if (type(toggle) is bool):
            self.quiet_mode = toggle
        else:
            print "set_quiet_mode: only accepts Boolean"

    @check_set_cwd
    def clean(self):
        """Run the clean phase."""
        cmd_list = ["mvn", "clean"]
        if self.quiet_mode:
            cmd_list += ['-q']

        ret_val = call(cmd_list)
        return ret_val

    @check_set_cwd
    def test(self):
        """Run the test phase."""
        cmd_list = ["mvn", "test"]
        if self.quiet_mode:
            cmd_list += ['-q']
        ret_val = call(cmd_list)
        return ret_val

    @check_set_cwd
    def install(self):
        """Run the install phase."""
        cmd_list = ["mvn", "install"]
        if self.quiet_mode:
            cmd_list += ['-q']
        ret_val = call(cmd_list)
        return ret_val

    @check_set_cwd
    def assemble_with_deps(self):
        """Assemble a jar with dependencies."""
        command_list = ["mvn", "assembly:assembly",
                        "-DdescriptorId=jar-with-dependencies"]
        if self.quiet_mode:
            command_list += ['-q']
        ret_val = call(command_list)
        return ret_val

    @check_set_cwd
    def get_jar_with_deps(self):
        """Return the jar with dependencies if it exists in target."""
        if not os.path.exists('target'):
            self.assemble_with_deps()

        for file in os.listdir('target'):
            if fnmatch.fnmatch(file, '*jar-with-dependencies.jar'):
                return '/'.join([os.getcwd(), 'target', file])

        return None

    @check_set_cwd
    def custom(self, custom_command):
        """Run a custom command."""
        if (type(custom_command) is not str):
            raise TypeError('MvnRunner.custom accepts command as a string')

        command_list = ["mvn"] + custom_command.split(' ')
        if self.quiet_mode:
            command_list += ['-q']
        ret_val = call(command_list)
        return ret_val
