# edu-bsc-beacon-julia
Repository for Bachelor Thesis for Julia (Beacons)

In this repository a GA4GH Beacon protocol was developed and 

# Installation
The software was developed in Ubuntu 18.04.5 LTS and those python packages are required:

alabaster==0.7.12
appdirs==1.4.4
asgiref==3.4.1
attr==0.3.1
attrs==21.2.0
Babel==2.9.1
black==21.5b1
certifi==2021.5.30
chardet==4.0.0
click==8.0.0
coverage==5.5
cycler==0.10.0
dataclasses==0.8
decorator==4.4.2
Django==3.2.5
django-nose==1.4.7
docutils==0.17.1
factory-boy==3.2.0
Faker==8.9.1
flake8==3.9.2
idna==2.10
imagesize==1.2.0
importlib-metadata==4.0.1
Jinja2==3.0.1
kiwisolver==1.3.1
MarkupSafe==2.0.1
matplotlib==3.3.4
mccabe==0.6.1
mypy-extensions==0.4.3
networkx==2.5.1
nose==1.3.7
numpy==1.19.5
obonet==0.3.0
packaging==21.0
pandas==1.1.5
pathspec==0.8.1
Pillow==8.3.0
pycodestyle==2.7.0
pyflakes==2.3.1
Pygments==2.9.0
pyparsing==2.4.7
python-dateutil==2.8.1
pytz==2021.1
regex==2021.4.4
requests==2.25.1
scipy==1.5.4
seaborn==0.11.1
six==1.16.0
snowballstemmer==2.1.0
Sphinx==4.0.2
sphinx-rtd-theme==0.5.2
sphinxcontrib-applehelp==1.0.2
sphinxcontrib-devhelp==1.0.2
sphinxcontrib-htmlhelp==2.0.0
sphinxcontrib-jsmath==1.0.1
sphinxcontrib-qthelp==1.0.3
sphinxcontrib-serializinghtml==1.1.5
sqlparse==0.4.1
text-unidecode==1.3
toml==0.10.2
typed-ast==1.4.3
typing==3.7.4.3
typing-extensions==3.10.0.0
urllib3==1.26.6
zipp==3.4.1

It can be installed cloning the github repository:

clone ...
activate pipenv

# First Steps
Before the system is fully functionable those steps have to be done:
1) register as an admin
> python manage.py createsuperuser
2) open the admin web by opening a web browser and go to “/admin/” on your local domain. 
4) add a MetadataBeacon Entry
5) add a MetadatBeaconOrganisation Entry
6) add a MetadatBeacondataset
7) add a RemoteSite with name="public" and key="public"

Then the server can be started and the Beacon enlighted!

# Further Information
More information and a detailled documentation is provided here:

