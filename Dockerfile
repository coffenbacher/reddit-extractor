FROM python:3.4

# Set up Conda
RUN apt-get update && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda-3.10.1-Linux-x86_64.sh && \
    /bin/bash /Miniconda-3.10.1-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda-3.10.1-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.14.1
ENV PATH /opt/conda/bin:$PATH

# Install Conda requirements
RUN conda install cffi --yes
RUN conda install cryptography --yes
RUN conda install notebook --yes 
RUN conda install jupyter --yes


ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ADD . /worker
WORKDIR /worker

VOLUME ["/notebooks", "/root/.jupyter"]

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini