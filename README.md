Fyyur
-----

### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.


1. Make sure you have Python 3.6 or later installed on your machine

2. clone the repo

3. Create a virtiual environment

4. Install the dependancies >>>> pip install -r requiremnts.txt

5. Create a database and change the connection in the config file

6. Activate the virtual environment 

7. Run $ flask db migrate

8. Run $ flask db upgrade


### Test the functionality of this project

To start and run the local development server,

1. Clone this repo:
  ```
  $ git clone https://github.com/Philipotieno/Fyyur-App.git
  ```

2. Initialize and activate a virtualenv:
  ```
  $ virtualenv -p python3 venv
  ```
3. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

4. Make migrations:
  ```
  $ flask db migrate
  $ flask db upgrate
  ```

5. Run the development server:
  ```
  $ python3 app.py
  ```

6. Navigate to Home page [http://localhost:8080](http://localhost:808)


#### NOTE 
  ## The DELETE venue endpont can be tested on postman  [http://localhost:8080/venues/venue_id](http://localhost:8080/venues/venue_id)
