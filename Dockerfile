FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# ENV TENSORFLOW_VERSION=2.10.0
# ENV TORCH_VERSION=1.13.0
# ENV TORCHVISION_VERSION=0.14.0

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    git \
    curl \
    ca-certificates \
    openssh-server \
    # libnvidia-compute-460 \
    # pysqlite3-binary \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /var/run/sshd
RUN echo 'root:nopassword' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

# WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["python3", "main.py"]