from git import Repo
from structs.file_desc import FileDesc
import os
import shutil


class RepoHandler(object):

    def __init__(self, repo_url, temp_dir_path='temp_dir'):

        self.repo_url = repo_url

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

    def clone_repo(self):
        # Repo.clone_from("https://github.com/Netflix/Hystrix.git", "temp_dir")
        Repo.clone_from(self.repo_url, self.repo_path)
        self.repo = Repo(self.repo_path)
        assert not self.repo.bare

    def get_modified_files(self, prev_commits=1):
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

        file_ext = os.path.splitext(full_path)[1]
        file_descriptor = FileDesc(path=full_path, ext=file_ext,
                                   change_type=change_type)
        return file_descriptor

    def delete_temp_dir(self):
        shutil.rmtree(self.repo_path)
