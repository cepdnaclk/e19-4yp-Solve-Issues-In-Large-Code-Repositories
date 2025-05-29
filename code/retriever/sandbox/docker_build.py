"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 27 2025

"""

from pathlib import Path

def generate_dockerfile_env(python_version):
    return f'''
FROM swe-ubuntu-base 
RUN conda create -y -n py_{python_version} python={python_version}

'''.strip()

def generate_dockerfile_packages(python_version, pre_install, sandbox_user='sandbox'):
    return f'''
FROM swe_py_{python_version} 
{"RUN " + pre_install if pre_install else ""}
WORKDIR /testbed

RUN groupadd --gid 1000 {sandbox_user} && \\
    useradd --uid 1000 --gid 1000 --create-home {sandbox_user} && \\
    chown -R {sandbox_user}:{sandbox_user} /testbed

USER {sandbox_user}

WORKDIR /testbed
CMD ["bash"]
'''.strip()


# {"RUN " + pre_install if pre_install else ""}
# {"RUN " + pre_install if pre_install else ""}

# RUN python -m pip install --upgrade pip
# {"RUN pip install " + pip_packages if pip_packages else ""}



# RUN groupadd --gid 1000 {sandbox_user} && \\
#     useradd --uid 1000 --gid 1000 --create-home {sandbox_user} && \\
#     chown -R {sandbox_user}:{sandbox_user} /app

# USER {sandbox_user}

# RUN conda activate py_{python_version}

# {"RUN pip install " + pip_packages if pip_packages else ""}
