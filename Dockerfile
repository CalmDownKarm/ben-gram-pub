FROM nvcr.io/nvidia/pytorch:19.10-py3

RUN apt-get update && apt-get install -y libhunspell-dev 

#Cyhunspell dependency

ADD benesse-demo/env.yml /

RUN cd / && conda env update -f env.yml 
# create the conda environment
# SHELL ["conda", "run", "-n", "v5onv1", "/bin/bash", "-c"]
# RUN conda init bash

RUN conda run -n v5onv1 pip install attrdict

ADD benesse-demo /benesse-demo
WORKDIR /benesse-demo
RUN conda run -n v5onv1 pip install -e src/api/model

# RUN conda run -n v5onv1 pip install -e src/api/model
# install fairseq

# ENTRYPOINT ["/bin/bash", "/benesse-demo/run.sh"]