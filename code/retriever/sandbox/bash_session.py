"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 27 2025

"""

import pexpect
import time, os

class BashSession:
    def __init__(self, command="bash", prompt="#|\\$", encoding="utf-8", timeout=600):
        self.prompt = prompt

        self.child = pexpect.spawn(command, encoding=encoding)
        self.child.logfile = open("docker_output.log", "w", encoding='utf-8')
        self.child.expect("#|\\$")

    def run_command(self, cmd, timeout=600):
        """
        Run a command in the bash session with an optional timeout.
        Returns command output or '[Interrupted due to timeout]'.
        """
        timeout = timeout or self.timeout
        self.child.sendline(cmd)

        try:
            self.child.expect("#|\\$", timeout=timeout)
            output = self.child.before
            # output = output[len(cmd)+1:].lstrip()  # Remove the command itself from the output
            # output = output.strip()  # Clean up any leading/trailing whitespace
        except pexpect.TIMEOUT:
            print(f"Timeout reached for: {cmd}. Sending Ctrl+C...")
            self.child.sendcontrol('c')  # Interrupt command
            self.child.expect_exact(self.prompt, timeout=10)
            output = "[Interrupted due to timeout]"

        return output

    def close(self):
        """
        Close the session cleanly.
        """
        self.child.sendline("exit")
        # self.child.expect(pexpect.EOF, timeout=10)
        self.child.close()

