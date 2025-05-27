import os
import pexpect


host_dir = os.path.abspath(".")
container_dir = "/app"
image_name = "django-env:4.2"

env = {"TERM": "dumb", "PS1": "$ "}


docker_command = f'docker run --mount type=bind,src={host_dir},dst={container_dir},ro -it {image_name} bash'

child = pexpect.spawn(docker_command, encoding='utf-8')

child.logfile = open("docker_output.log", "w", encoding='utf-8')


child.expect("#|\\$")  
child.sendline("ls -la")
child.expect("#|\\$") 
print(child.before)  
child.sendline("python gg.py")
child.expect("#|\\$")
print(child.before)  # Print output of the command

child.sendline("python --version")
child.expect("#|\\$")

