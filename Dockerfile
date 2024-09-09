FROM jodogne/orthanc:1.12.4
COPY orthanc.json /etc/orthanc/
ENV ORTHANC_JSON /etc/orthanc/orthanc.json