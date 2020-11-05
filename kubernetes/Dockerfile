# Read from Ubuntu Base Image
FROM python:3.6
RUN mkdir -p /service
# Copy over all the files of interest
ADD requirements.txt /service/requirements.txt
RUN pip install -r /service/requirements.txt
ADD politeness /service/politeness
ADD static /service/static
ADD outputs /service/outputs
ADD templates /service/templates
ADD db_mysql.py /service/db_mysql.py
ADD utils.py /service/utils.py
ADD app.py /service/app.py
WORKDIR /service/
RUN python -m spacy download en
RUN python -m nltk.downloader punkt
CMD python app.py