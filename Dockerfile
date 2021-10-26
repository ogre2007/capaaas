# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /capa

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN git clone https://github.com/mandiant/capa-rules/
RUN mkdir sigs && cd sigs
RUN wget https://github.com/mandiant/capa/raw/master/sigs/1_flare_msvc_rtf_32_64.sig
RUN wget https://github.com/mandiant/capa/raw/master/sigs/2_flare_msvc_atlmfc_32_64.sig
RUN wget https://github.com/mandiant/capa/raw/master/sigs/3_flare_common_libs.sig
RUN sudo python3 setup.py install --prefix ~/.local && cd .. && rm -rf binwalk
COPY . .

ENV FLASK_APP /app/app.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port 5555"]
