FROM python:3.8
EXPOSE 8080

# set the base installation, requirements are not changed often
RUN pip install --upgrade pip setuptools wheel pipenv

WORKDIR /app
ADD ./requirements.txt ./Pipfile ./Pipfile.lock ./datasafe.svg ./
RUN pipenv install --system

ENV OPENAPI_MULTIPLE_FILES      "interface_port_metadata.yml"

ADD "https://raw.githubusercontent.com/Sciebo-RDS/Sciebo-RDS/master/RDS/circle2_use_cases/interface_port_metadata.yml" ./

# now add everything else, which changes often
ADD src ./

ENTRYPOINT [ "python", "server.py" ]