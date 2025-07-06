import pexpect
import re

import pexpect, re

class BashSession:
    def __init__(self, command="bash", encoding="utf-8", timeout=600):
        self.prompt = "__PEXPECT_PROMPT__"
        self.child  = pexpect.spawn(command, encoding=encoding)
        self.child.logfile = open("docker_output.log", "w", encoding="utf-8")

        # 1) Wait for the native prompt once
        self.child.expect(r"[#$]")

        # 2) Turn off bracketed‑paste noise (optional but nice)
        self.child.sendline('bind "set enable-bracketed-paste off"')
        self.child.expect(r"[#$]")

        # 3) Install a rock‑simple, unique prompt
        self.child.sendline(f'export PS1="{self.prompt}"')
        self.child.expect_exact(self.prompt, timeout=timeout)

        # 4) Disable command echo so only *real* output is captured
        self.child.setecho(False)

    # ------------------------------------------------------------
    def _flush(self):
        """Consume everything up to the current prompt."""
        try:
            self.child.expect_exact(self.prompt, timeout=0.1)
        except pexpect.TIMEOUT:
            pass                  # nothing waiting

    def run_command(self, cmd, timeout=600, new_env= False):
        self._flush()             # clear leftovers from previous call
        self.child.sendline(cmd)
        try: 
            if new_env:
                self.child.expect(r"[#$]", timeout=timeout)
                output = self.child.before
                self.child.sendline(f'export PS1="{self.prompt}"')
                self.child.expect_exact(self.prompt, timeout=timeout)
            else:
                self.child.expect_exact(self.prompt, timeout=timeout)
                output = self.child.before.lstrip("\r\n")  # strip leading newline(s)
        except:
            print(f"Timeout reached for: {cmd}. Sending Ctrl+C...")
            output = "TimeOut Reached"+self.child.before
            self.child.sendcontrol('c')
        return output

    def close(self):
        self.child.sendline("exit")
        self.child.close()


 
if __name__ == "__main__":
    print("Testing BashSession...")
    session = BashSession()
    
    # Give it a moment to settle
    
    
    print("\n=== Basic Tests ===")
    
    # Test 1: Simple echo
    result = session.run_command("echo 'Hello World'")
    print(f"Echo test: {repr(result)}")
    
    # Test 2: PWD
    result = session.run_command("pwd")
    print(f"PWD test: {repr(result)}")
    
    # Test 3: Simple ls
    result = session.run_command("ls -1 | head -5")
    print(f"LS test: {repr(result)}")
    
    # Test 4: Whoami
    result = session.run_command("whoami")
    print(f"Whoami test: {repr(result)}")
    
    print("\n=== Validation Method Tests ===")
    

    
    session.close()
    print("Tests completed.")