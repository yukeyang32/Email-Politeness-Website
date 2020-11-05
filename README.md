# PolitenessFeedback


## How to Run Application:

1. Install requirements
```
pip install -r requirements.txt
```
2. Download Spacy English Model
```
python -m spacy download en
```
3. Within Python, run:
```
import nltk; nltk.download('punkt')
```
4. Run the App
```
python app.py
```


## How to Train and Load Model:

1. Use /politeness/parser.py to parse the csv data inside /politeness/corpora
2. Use train_classifier() function inside /politeness/scripts/train_mode.py to train a new model using the parsed data
3. Change variable MODEL_FILENAME inside /politeness/model.py to the name of trained model.



## Database:
There are three tables: Input, Feedback_Doc, and Feedback_sentence. Their respective fields are listed below.

#### Input:
input id (*automatically assigned, self-increment*), user id, message, timestamp

#### Feedback_Doc:
input id (*defined in the Input table*), word count, label, impolite_score, polite_score

#### Feedback_Sentence:
id (*automatically assigned, self-increment*), input id (*defined in the Input table*), sentence, label, impolite score, polite score, num_strategy, strategy list, index list


### Example with database:

#### Input:
(1, '10183100', 'Nice to meet you! You look great!', 'Apr 24 2020 15:15:19'),

(2, '10183100', 'May I ask you a question please?', 'Apr 24 2020 15:15:48'),

(3, '22990282', 'I hate you! You suck!', 'Apr 24 2020 15:16:15')

#### Feedback_Doc:
(1, 7, 'impolite', 0.5558363956902534, 0.4441636043097465),

(2, 7, 'polite', 0.426353102022843, 0.5736468979771572),

(3, 5, 'impolite', 0.5075150168767901, 0.49248498312320976)

#### Feedback_Sentence:
(1, 1, 'Nice to meet you!', 'impolite', 0.53658481006666, 0.4634151899333399, 0, '[]', '[]'),

(2, 1, 'You look great!', 'impolite', 0.5799089135738043, 0.4200910864261958, 1, "['2nd person start']", '[[(0, 3)]]'),

(3, 2, 'May I ask you a question please?', 'polite', 0.426353102022843, 0.5736468979771572, 0, '[]', '[]'),

(4, 3, 'I hate you!', 'polite', 0.4880425600882068, 0.5119574399117932, 1, "['HASNEGATIVE']", '[[(2, 6)]]'),

(5, 3, 'You suck!', 'impolite', 0.5799089135738043, 0.4200910864261958, 3, "['2nd person start', 'HASPROFANITY', 'HASNEGATIVE']", '[[(0, 3)], [(4, 8)], [(4, 8)]]')


## FAQ:
> Q: How do I delete the database?
>> A: Run ' cur.execute("""DROP TABLE IF EXISTS feedback;""") ' in app.py.

> Q: Can't find model 'en'. It doesn't seem to be a shortcut link, a Python package or a valid path to a data directory.
>> A: have to use python -m spacy download en in virtual environment

> Q: I have installed mysql but still got mysql_config not found error.
>> A: The installer could not find the mysql_config file from the virtual environment. The quickest fix is to create a soft link to the file by running "export PATH=$PATH:/usr/local/mysql/bin" then "pip install requirements".

> Followup: I am now getting ImportError: dlopen(/Path/to/the/app/_mysql.cpython-36m-darwin.so, 2): Library not loaded: @rpath/libmysqlclient.21.dylib
>> A: Same issue with mysql_config. Simply run "export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/" in your terminal.


## Deploy Flask on PythonAnywhere

https://www.pythonanywhere.com/login/

ID: hl934;

PW: Hajin0720


1. Go to the Web Tab and hit 'Add a new web app'. Set domain name, and then choose Flask and Python 3.6.

2. Open a bash console, using 'git clone' command to upload the Flask project. For the purposes of this example, we'll assume the code lives at '/home/hl934/flask_project'.

3. Go to the Web Tab, under the Code Section, change the source code directory to '/home/hl934/flask_project' and working directory to '/home/hl934/'.

4. Open the WSGI configuration file, the content of this file should be as follows. Note that the last line is essential since in PythonAnywhere the flask app can only be recognized when using the name 'application'.

		import sys
		# add your project directory to the sys.path

		project_home = '/home/hl934/flask_project'
		if project_home not in sys.path:
		    sys.path = [project_home] + sys.path
		# import flask app but need to call it "application" for WSGI to work
		from app import app as application  # from 'app.py' file import 'app' and call it 'application'

5. Note that we now use the database provided by PythonAnywhere. The database was already created under the Databases Tab and its name is 'feedback'. In 'app.py' file, Using the following codes to get access to the database:

		app.config['MYSQL_USER'] = 'hl934'
		app.config['MYSQL_PASSWORD'] = 'Hajin0720'
		app.config['MYSQL_DB'] = 'hl934$feedback'
		app.config['MYSQL_HOST'] = 'hl934.mysql.pythonanywhere-services.com'
		app.config['MYSQL_PORT'] = 3306

6. Go back to the Web Tab, click the 'Reload hl934.xxx.com' ('xxx' is the domain name) button to reload the project. For debugging purposes, the log files can be found under the Log Files Section. If everything works fine, click 'hl934.xxx.com', the webpage should appear.
