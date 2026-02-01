import subprocess, shlex, os

class Executor:
    def __init__(self, config):
        self.config = config

    def run_shell(self, cmd, check=True):
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {"rc": proc.returncode, "out": proc.stdout, "err": proc.stderr}

    def git_commit_and_push(self, branch, msg):
        self.run_shell(f"git checkout -b {branch} || git checkout {branch}")
        self.run_shell("git add -A")
        self.run_shell(f"git commit -m \"{msg}\" || true")
        return self.run_shell(f"git push origin {branch} --set-upstream || true")
