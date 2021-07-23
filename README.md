# edu-bsc-beacon-julia
Repository for Bachelor Thesis for Julia (Beacons)

In this repository a modified and extended version of the GA4GH Beacon protocol was implemented.

## Installation
The software was developed in Ubuntu 18.04.5 LTS and those python packages are required:

alabaster==0.7.12 <br>
appdirs==1.4.4 <br>
asgiref==3.4.1 <br>
attr==0.3.1 <br>
attrs==21.2.0 <br>
Babel==2.9.1 <br>
black==21.5b1 <br>
certifi==2021.5.30 <br>
chardet==4.0.0 <br>
click==8.0.0 <br>
coverage==5.5 <br>
cycler==0.10.0 <br>
dataclasses==0.8 <br>
decorator==4.4.2 <br>
Django==3.2.5 <br>
django-nose==1.4.7 <br>
docutils==0.17.1 <br>
factory-boy==3.2.0 <br>
Faker==8.9.1 <br>
flake8==3.9.2 <br>
idna==2.10 <br>
imagesize==1.2.0 <br>
importlib-metadata==4.0.1 <br>
Jinja2==3.0.1 <br>
kiwisolver==1.3.1 <br>
MarkupSafe==2.0.1 <br>
matplotlib==3.3.4 <br>
mccabe==0.6.1 <br>
mypy-extensions==0.4.3 <br>
networkx==2.5.1 <br>
nose==1.3.7 <br>
numpy==1.19.5 <br>
obonet==0.3.0 <br>
packaging==21.0 <br>
pandas==1.1.5 <br>
pathspec==0.8.1 <br>
Pillow==8.3.0 <br>
pycodestyle==2.7.0 <br>
pyflakes==2.3.1 <br>
Pygments==2.9.0 <br>
pyparsing==2.4.7 <br>
python-dateutil==2.8.1 <br>
pytz==2021.1 <br>
regex==2021.4.4 <br>
requests==2.25.1 <br>
scipy==1.5.4 <br>
seaborn==0.11.1 <br>
six==1.16.0 <br>
snowballstemmer==2.1.0 <br>
Sphinx==4.0.2 <br>
sphinx-rtd-theme==0.5.2 <br>
sphinxcontrib-applehelp==1.0.2 <br>
sphinxcontrib-devhelp==1.0.2 <br>
sphinxcontrib-htmlhelp==2.0.0<br>
sphinxcontrib-jsmath==1.0.1<br>
sphinxcontrib-qthelp==1.0.3<br>
sphinxcontrib-serializinghtml==1.1.5<br>
sqlparse==0.4.1<br>
text-unidecode==1.3<br>
toml==0.10.2<br>
typed-ast==1.4.3<br>
typing==3.7.4.3<br>
typing-extensions==3.10.0.0<br>
urllib3==1.26.6<br>
zipp==3.4.1`<br>

It can be installed cloning the github repository:

`git clone https://github.com/bihealth/edu-bsc-beacon-julia`

Then the pipenv should be activated:

`pipenv install` <br>
`pipenv shell`

For trying if the installation was succesfull tests can be run:

`python manage.py test`

## First Steps
Before the system is fully functionable those steps have to be done:
1. register as an admin<br>
`python manage.py createsuperuser`
2. open the admin web interface by opening a web browser and go to “/admin/” on your local domain. 
3. add a MetadataBeacon Entry
4. add a MetadatBeaconOrganisation Entry
5. add a MetadatBeacondataset
6. add a RemoteSite with name="public" and key="public"

Then the server can be started and the new Beacon enlighted!<br>
`python manage.py runserver`

## Further Information
More information and a detailled documentation is provided [here](https://github.com/bihealth/edu-bsc-beacon-julia/blob/main/docs/build/html/index.html).

