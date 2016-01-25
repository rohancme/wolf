from repo_handler import RepoHandler


rh = RepoHandler("https://github.com/Netflix/Hystrix.git",
                 temp_dir_path='temp_dir')
rh.clone_repo()
for file_desc in rh.get_modified_files():
    print file_desc

rh.delete_temp_dir()
