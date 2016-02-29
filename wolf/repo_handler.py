"""This module handles all the functionality related to a github repo."""
from git import Repo
from structs.file_desc import FileDesc
import os
import shutil


class RepoHandler(object):
    """
    The main Repository Handler class.

    1. Initializes the folder in which to store the cloned repo
    2. Clones the repo
    3. Gets the list of modified files in the repo_url as a list of
    file descriptor objects
    """

    def __init__(self, repo_url=None, temp_dir_path=None):
        """Find a suitable folder in which to store the cloned repo.

        Default: repository name
        If folder already exists -> Deletes it
        If folder does not exist, but write privileges exist-> creates it
        If no write privileges -> tries creating the dir in cwd
        If none of this works -> throw IOError
        """
        if repo_url is None and temp_dir_path is None:
            return None

        # Use an already clone repo
        if repo_url is None and temp_dir_path is not None:
            self.set_repo(temp_dir_path)
            return

        self.repo_url = repo_url

        # If not defined, by default set folder name to repo name
        if temp_dir_path is None:
            temp_dir_path = repo_url.rsplit('/', 1)[-1]
            if temp_dir_path.endswith('.git'):
                temp_dir_path = temp_dir_path.replace('.git', '')

        # From: http://stackoverflow.com/a/9532586/2021149
        if os.path.exists(temp_dir_path):
            # the file is there
            # throw a prompt for deleting?
            shutil.rmtree(temp_dir_path)
            self.repo_path = temp_dir_path
        elif os.access(os.path.dirname(temp_dir_path), os.W_OK):
            # the file does not exists but write privileges are given
            self.repo_path = temp_dir_path
        else:
            # can not write there
            # Try and create the path in the working dir
            new_path = '/'.join([os.getcwd(), temp_dir_path])

            if os.access(os.path.dirname(new_path), os.W_OK):
                self.repo_path = new_path
            else:
                raise IOError('No permissions for:' + temp_dir_path)

    def get_path(self):
        """Return the full path to the repo."""
        return self.repo_path

    def set_repo(self, path):
        """Set the repo with a new path."""
        self.repo_path = path
        self.repo = Repo(self.repo_path)

    def clone_repo(self):
        """Clone a repo and ensures it isn't bare."""
        Repo.clone_from(self.repo_url, self.repo_path)
        self.repo = Repo(self.repo_path)
        assert not self.repo.bare

    def get_modified_files(self, prev_commits=1):
        """Get list of FileDesc objects about changes in last prev_commits."""
        hcommit = self.repo.head.commit
        results = hcommit.diff('HEAD~' + str(prev_commits))

        # Store the list of modified or newly added files
        # in the last 'prev_commits' commits
        mod_added_files = []

        # This needs to be cleaned up
        for result in results.iter_change_type('M'):
            full_path = '/'.join([self.repo_path, result.a_path])
            file_descriptor = self.get_file_descriptor(full_path=full_path,
                                                       change_type='M')
            mod_added_files += [file_descriptor]
        for result in results.iter_change_type('A'):
            full_path = '/'.join([self.repo_path, result.a_path])
            file_descriptor = self.get_file_descriptor(full_path=full_path,
                                                       change_type='A')
            mod_added_files += [file_descriptor]

        return mod_added_files

    def get_file_descriptor(self, full_path, change_type):
        """Return a FileDesc object with full path, file type, change type."""
        file_ext = os.path.splitext(full_path)[1]
        file_descriptor = FileDesc(path=full_path, ext=file_ext,
                                   change_type=change_type)
        return file_descriptor

    def delete_temp_dir(self):
        """Delete the local copy."""
        shutil.rmtree(self.repo_path)

    def run_cmd(self, cmd):
        pass
        # mvn assembly:assembly -DdescriptorId=jar-with-dependencies
        # "java -classpath randoop-2.1.1.jar:rome/target/rome-1.6.0-SNAPSHOT-jar-with-dependencies.jar randoop.main.Main gentests --testclass=com.rometools.rome.io.impl.BaseWireFeedParser"
        # "java -classpath randoop-2.1.1.jar:temp_dir/target/rome-1.6.0-SNAPSHOT-jar-with-dependencies.jar randoop.main.Main gentests --testclass=com.rometools.rome.io.impl.BaseWireFeedParser"
