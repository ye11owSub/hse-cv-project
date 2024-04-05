FROM python:3.10

ENV PYTHONUNBUFFERED True

COPY . /opt/hse_cv_project/
WORKDIR /opt/hse_cv_project

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN python3 -m pip install --upgrade pip && \ 
    python3 -m pip install -e .[develop]

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/hse_cv_project/demo_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

