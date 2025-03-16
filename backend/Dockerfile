FROM python:3.12

RUN apt update && apt install -y g++
RUN groupadd -r maeuschen && useradd -r -g maeuschen maeuschen

ENV HOME=/home/maeuschen
USER maeuschen
WORKDIR $HOME
COPY --chown=maeuschen:maeuschen pyproject.toml pyproject.toml

RUN pip install --user --no-cache-dir e .
ENV PATH="$HOME/.local/bin:${PATH}"
