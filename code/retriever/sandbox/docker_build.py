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

FROM --platform=linux/x86_64 ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt update && apt install -y --no-install-recommends \
wget \
git \
build-essential \
libffi-dev \
libtiff-dev \
python3 \
python3-pip \
python-is-python3 \
jq \
curl \
locales \
locales-all \
tzdata \
&& rm -rf /var/lib/apt/lists/*

# Download and install conda
RUN wget 'https://repo.anaconda.com/miniconda/Miniconda3-py312_25.3.1-1-Linux-x86_64.sh' -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/miniconda3
# Add conda to PATH
ENV PATH=/opt/miniconda3/bin:$PATH
# Add conda to shell startup scripts like .bashrc (DO NOT REMOVE THIS)
RUN conda init --all
RUN conda config --append channels conda-forge

RUN conda create -y -n py_{python_version} python={python_version}

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
# RUN conda activate py_{python_version}

# RUN python -m pip install --upgrade pip
# {"RUN pip install " + pip_packages if pip_packages else ""}



# RUN groupadd --gid 1000 {sandbox_user} && \\
#     useradd --uid 1000 --gid 1000 --create-home {sandbox_user} && \\
#     chown -R {sandbox_user}:{sandbox_user} /app

# USER {sandbox_user}

# RUN conda activate py_{python_version}

# {"RUN pip install " + pip_packages if pip_packages else ""}
