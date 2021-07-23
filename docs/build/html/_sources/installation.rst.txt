Installations and First Steps
=============================

Installation
---------------

It can be installed cloning the github repository:

.. code-block:: console
    
    $ git clone https://github.com/bihealth/edu-bsc-beacon-julia

Then the pipenv should be activated:

.. code-block:: console

    $ pipenv install
    $ pipenv shell

For trying if the installation was succesfull tests can be run:

.. code-block:: console

    $ python manage.py test

First Steps
---------------

Before the system is fully functionable those steps have to be done:

1. register as an admin

.. code-block:: console

   $ python manage.py createsuperuser

2. open the admin web interface by opening a web browser and go to “/admin/” on your local domain. 
3. add a MetadataBeacon Entry
4. add a MetadatBeaconOrganisation Entry
5. add a MetadatBeacondataset
6. add a RemoteSite with name="public" and key="public"

Then the server can be started and the new Beacon enlighted!

.. code-block:: console

   $ python manage.py runserver

Example Request
----------------

This is an example request of the info endpoint:

.. code-block:: console

	$ curl http://127.0.0.1:8000/
	{  
	  "id": "beacon-01", 
	  "name": "Beacon 1",
	  "apiVersion": "1.0.0", 
	  "datasets": [
	    {
	      "id": "dataset_01", 
	      "name": "dataset"
	      "assemblyId": "GRCh37", 
	      "createDateTime":"2021-07-05T00:00.000Z",
	      "updateDateTime":"2021-07-05T00:00.000Z",
	    }
	  ], 
	  "organization": {
	    "id": "organization_1", 
	    "name": "First extended Beacon organization.", 
	    "contactUrl": "contact@email.com",
	  }, 
	}

This is an example request of the query endpoint:

.. code-block:: console

	$ curl -H "Authorization:xxx" -H "X-Remote-User:user_1" -v -X GET "http://127.0.0.1:8000/query?referenceName=1&start=12344&end=12345&referenceBases=C&alternateBases=T"
	{
	    "beaconId": "beacon-01",
	    "apiVersion": "1.0.0",
	    "exists": true,
	    "error": null,
	    "alleleRequest": {
		"referenceName": "1",
		"start": 12344,
		"end": 12345,
		"referenceBases": "C",
		"alternateBases": "T",
		"assemblyId": "GRCh37",
	    },
	    "datasetAlleleResponses": [
		{
		    "exists": true,
		    "sampleCount": 7,
		    "variantCount>10": True,
		    "variantCount": 7,
		    "frequency": 0.53,
		    "coarsePhenotype": ["HP:0000271"],
		    "phenotype": ["HP:0025521"],
		    "caseName": ["case_index_01", "case_index_02"],
		}
	    ]
	}
