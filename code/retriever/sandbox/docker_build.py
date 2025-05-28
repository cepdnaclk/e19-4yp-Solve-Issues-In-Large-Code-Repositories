"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 27 2025

"""

from pathlib import Path

def generate_dockerfile(python_version, pre_install, pip_packages, sandbox_user='sandbox'):
    return f'''
FROM swe-ubuntnu-base 

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
