from pathlib import Path

def generate_dockerfile(python_version, pre_install, pip_packages, requirements, install_cmd, sandbox_user='sandbox'):
    return f'''
FROM python:{python_version}-slim

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV PYTHONIOENCODING=utf8

WORKDIR /app

{"RUN " + pre_install if pre_install else ""}

RUN python -m pip install --upgrade pip
{"RUN pip install " + pip_packages if pip_packages else ""}



RUN groupadd --gid 1000 {sandbox_user} && \\
    useradd --uid 1000 --gid 1000 --create-home {sandbox_user} && \\
    chown -R {sandbox_user}:{sandbox_user} /app

USER {sandbox_user}
CMD ["bash"]
'''.strip()


import pexpect
import tempfile
import shutil

dockerfile_str = generate_dockerfile(
    python_version="3.9",
    pre_install="apt-get update && apt-get install -y locales && echo 'en_US UTF-8' > /etc/locale.gen && locale-gen en_US.UTF-8",
    pip_packages="setuptools",
    requirements="requirements.txt",
    install_cmd=""
)

tmpdir = tempfile.mkdtemp()
Path(f"{tmpdir}/Dockerfile").write_text(dockerfile_str)

child = pexpect.spawn(f'docker build -t django-env:4.2 {tmpdir}', encoding='utf-8')
child.logfile = open("build.log", "w")
child.expect(pexpect.EOF, timeout=600)

print(f"Docker image built from: {tmpdir}")

