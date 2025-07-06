"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 27 2025

"""

import pexpect
import time, os
import uuid
import re
# class BashSession:
#     def __init__(self, command="bash", prompt=r"__PEXPECT_PROMPT__" , encoding="utf-8", timeout=600):
#         # self.prompt = prompt
#         self.prompt = "__PEXPECT_PROMPT__"

#         # self.child = pexpect.spawn(command, encoding=encoding)
#         self.child = pexpect.spawn(command, encoding=encoding, env={"PS1": self.prompt, "VIRTUAL_ENV_DISABLE_PROMPT": "1"})
#         self.child.logfile = open("docker_output.log", "w", encoding='utf-8')
        
#         self.child.expect(r"[#\$]")  # Wait for default prompt
#         self.child.sendline(f'export PS1="{self.prompt}"')
#         self.child.expect(self.prompt)

#     def run_command(self, cmd, timeout=500):
#         """
#         Run a command in the bash session with an optional timeout.
#         Returns command output or '[Interrupted due to timeout]'.
#         """
#         timeout = timeout
#         self.child.sendline(cmd)

#         try:
#             self.child.expect(self.prompt, timeout=timeout)
#             output = self.child.before
#             # output = output[len(cmd)+1:].lstrip()  # Remove the command itself from the output
#             # output = output.strip()  # Clean up any leading/trailing whitespace
#         except pexpect.TIMEOUT:
#             print(f"Timeout reached for: {cmd}. Sending Ctrl+C...")
#             output = self.child.before
#             self.child.sendcontrol('c')  # Interrupt command
#             self.child.expect_exact(self.prompt, timeout=10)
    

#         return output

#!!!!!!!!!!!!!WOrking One
class BashSession:
    def __init__(self, command="bash", prompt="\\$", encoding="utf-8", timeout=600):
        # self.prompt = prompt
        self.prompt = "PEXPECT_PROMPT"

        self.child = pexpect.spawn(command, encoding=encoding)
        self.child.expect("\\$")
        self.child.logfile = open("docker_output.log", "w", encoding='utf-8')
        # self.child.expect("\\$")
        

        self.child.sendline(f'export PS1="{self.prompt}"')
        self.child.expect(self.prompt)

    def run_command(self, cmd, timeout=600, new_env = False):
        """
        Run a command in the bash session with an optional timeout.
        Returns command output or '[Interrupted due to timeout]'.
        """
        timeout = timeout
        self.child.sendline(cmd)

        try:
            if new_env:
                self.child.expect("\\$", timeout=timeout)
                output = self.child.before
                self.child.sendline(f'export PS1="{self.prompt}"')
                self.child.expect(self.prompt)
            else:
                self.child.expect(self.prompt, timeout=timeout)
                output = self.child.before
            # output = output[len(cmd)+1:].lstrip()  # Remove the command itself from the output
            # output = output.strip()  # Clean up any leading/trailing whitespace
        except pexpect.TIMEOUT:
            print(f"Timeout reached for: {cmd}. Sending Ctrl+C...")
            self.child.sendcontrol('c')  # Interrupt command
            self.child.expect(self.prompt, timeout=10)
            output = "[Interrupted due to timeout]"

        return output

    def close(self):
        """
        Close the session cleanly.
        """
        self.child.sendline("exit")
        # self.child.expect(pexpect.EOF, timeout=10)
        self.child.close()



# import pexpect
# import os
# from pathlib import Path

# import pexpect
# import time

# import pexpect, re, uuid, os

# # ---------- helpers ----------------------------------------------------------
# _ansi_escape  = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')     # SGR etc.
# _bracket_2004 = re.compile(r'\x1B\[\?2004[hl]')            # bracket‑paste
# _osc8_link    = re.compile(r'\x1B\][^\x07]*\x07')          # OSC hyperlinks

# def _clean(text, marker, prompt):
#     """Remove marker, prompt‑echo, ANSI colour, bracket‑paste & OSC junk."""
#     text = text.replace(marker, '')
#     # remove the "CUSTOM_PROMPT_>>> cmd …" line if it slipped in
#     text = re.sub(re.escape(prompt) + r'.*', '', text)
#     text = _ansi_escape.sub('', text)
#     text = _bracket_2004.sub('', text)
#     text = _osc8_link.sub('', text)
#     return text.strip()

# # ---------- main class -------------------------------------------------------
# class BashSession:
#     def __init__(self, command="/bin/bash", encoding="utf-8", timeout=600):
#         self.timeout = timeout
#         self.prompt  = "__PEXPECT_PROMPT__>>> "
#         # start an *interactive* shell with no user rc files
#         self.child = pexpect.spawn(
#             command, ["--noprofile", "--norc", "-i"],
#             encoding=encoding, echo=False
#         )
#         self.child.logfile = open("docker_output.log", "w", encoding="utf-8")

#         # minimal prompt, bracket‑paste off, and propagate to child shells
#         init = (
#             f'export PS1="{self.prompt}" ; '
#             'bind "set enable-bracketed-paste off" ; '
#             'export PROMPT_COMMAND="bind \'set enable-bracketed-paste off\'"'
#         )
#         self.child.sendline(init)
#         self.child.expect_exact(self.prompt, timeout=self.timeout)

#     def run_command(self, cmd, timeout=None):
#         if timeout is None: timeout = self.timeout
#         marker = f"__CMD_DONE__{uuid.uuid4().hex}__"
#         raw_cmd = f"{cmd} ; echo {marker} 2>&1"
#         self.child.sendline(raw_cmd)

#         try:
#             self.child.expect_exact(marker, timeout=timeout)
#             out = self.child.before           # everything *before* marker
#             self.child.expect_exact(self.prompt)  # eat prompt
#         except pexpect.TIMEOUT:
#             self.child.sendcontrol('c')
#             self.child.expect_exact(self.prompt, timeout=10)
#             return "[Interrupted due to timeout]"

#         return _clean(out, marker, self.prompt)

#     def close(self):
#         self.child.sendline("exit")
#         self.child.close()


    