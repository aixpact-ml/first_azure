FROM jupyter/tensorflow-notebook

USER root

RUN apt-get update && apt-get install -y curl
# RUN apt-get install -yq --no-install-recommends \
#     curl

# Install Tensorflow
RUN conda install --quiet --yes \
    'graphviz' \
    'pydot' \
    'opencv' && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

USER $NB_USER

RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
RUN pip install --proxy=${http_proxy} \
    psycopg2-binary \
    minio \
    opencv-python \
    graphviz \
    pydotplus \
    ipympl
COPY requirements.txt requirements.txt
RUN pip install -r --no-cache-dir requirements.txt

RUN jupyter nbextension enable --py --sys-prefix ipympl


# USER $NB_USER

# COPY requirements.txt /
# RUN pip install --no-cache-dir -r /requirements.txt

# USER jovyan

# COPY requirements.txt requirements.txt
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
