FROM jaszhou/python:latest
WORKDIR /srv
#ADD ./requirements.txt /srv/requirements.txt
#RUN pip install -r requirements.txt 
ADD *.* /srv
ENV PYTHONUNBUFFERED=1
CMD python -u /srv/day_trade.py
#CMD python /srv/run.py

