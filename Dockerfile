FROM jupyter/tensorflow-notebook

USER root

# Install Tensorflow
RUN conda install --quiet --yes \
    'graphviz' \
    'pydot' \
    'opencv' && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

USER $NB_USER

RUN pip install --upgrade pip
RUN pip install --proxy=${http_proxy} \
    psycopg2-binary \
    minio \
    opencv-python \
    graphviz \
    pydotplus \
    ipympl
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN jupyter nbextension enable --py --sys-prefix ipympl


# USER $NB_USER

# COPY requirements.txt /
# RUN pip install --no-cache-dir -r /requirements.txt

# USER jovyan

# COPY requirements.txt requirements.txt
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
