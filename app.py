from flask import Flask, Response, make_response, render_template, redirect, url_for, request, session, g
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
from werkzeug import debug
from yaml.events import DocumentStartEvent
from utils import *
from politeness.features.vectorizer import PolitenessFeatureVectorizer
from politeness.feedbacks.feedback import get_feedback
from pylanguagetool import api
import datetime
import nltk
from jinja2 import Template


################################################################################
local_bool = True  # Set to True if Localhost, False if online hosting
politeness_bool = True  # True to turn on politeness model, False to turn off
num_decimals = 5

app = Flask(__name__)
# for PythonAnywhere
# app.secret_key = 'secret key'
# app.config['MYSQL_USER'] = 'hl934'
# app.config['MYSQL_PASSWORD'] = 'Hajin0720'
# app.config['MYSQL_DB'] = 'hl934$feedback'
# app.config['MYSQL_HOST'] = 'hl934.mysql.pythonanywhere-services.com'
# app.config['MYSQL_PORT'] = 3306

app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config['MYSQL_HOST'] = 'mi3-ss38.a2hosting.com'
app.config['MYSQL_USER'] = 'politene_user'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'politene_ss_test'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

socketio = SocketIO(app)
#################################################################################

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']


@app.route('/login', methods=['GET', 'POST'])
def login():
    global login
    if request.method == 'POST':
        session.pop('user_id', None)
        user_id = request.form['userid']
        session['user_id'] = user_id
        login = True
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    global login
    if not login:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # cur.execute("""DROP TABLE IF EXISTS Feedback_Doc;""")
    # cur.execute("""DROP TABLE IF EXISTS Feedback_Sentence;""")
    # cur.execute("""DROP TABLE IF EXISTS Input;""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Input (
                input_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id TEXT,
                message TEXT,
                time_stamp TEXT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Feedback_Doc (
                input_id INTEGER PRIMARY KEY,
                word_count INTEGER,
                label TEXT,
                impoliteness_score REAL,
                politeness_score REAL,
                FOREIGN KEY (input_id) REFERENCES Input(input_id)
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Feedback_Sentence (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                input_id INTEGER,
                sentence_content TEXT,
                label TEXT,
                impoliteness_score REAL,
                politeness_score REAL,
                strategy_count INTEGER,
                strategies VARCHAR(255),
                indices VARCHAR(255),
                FOREIGN KEY (input_id) REFERENCES Input(input_id)
                )""")
    label_string = ""
    input_text = ""
    title = ""
    strategies_set = set()
    highlight_index_set = set()
    strategies = []
    if request.method == 'POST':
        title = request.form['theme']
        input_text = request.form['sentence']

        # check for grammatical mistakes
        grammar_check = api.check(input_text, api_url='https://languagetool.org/api/v2/', lang='en-US')
        grammar_messages = grammar_check['matches']
        grammar_corrections, split_input, wrong_words, impolite_words, replacements = [], [], [], [], {}
        if len(grammar_messages) != 0:
            for i in range(len(grammar_messages)):
                # og_msg = grammar_messages[i]['context']['text']
                og_msg = input_text
                offset = grammar_messages[i]['offset']
                grammar_corrections.append(grammar_messages[i]['message'])
                wrong_words.append(og_msg[offset:offset+grammar_messages[i]['length']])
                for repl in grammar_messages[i]['replacements']:
                    if i not in replacements:
                        replacements[i] = [repl['value']]
                    else:
                        replacements[i].append(repl['value'])
        split_input = input_text.split()
        ### NEEDS TO BE CHANGED LATER...
        num_corrections = str(len(replacements))
        print(wrong_words)
        print(replacements)


        # Get politeness score for overall document
        doc_res = score_text(input_text)
        print("DOCUMENT POLITENESS:\n", doc_res)
        label_string = doc_res[0]

        # Get politeness score for each sentence in document
        sentence_list = nltk.sent_tokenize(input_text)
        sent_politeness_res = list()
        impolite_sentence_indices = dict()
        for i, sentence in enumerate(sentence_list):
            ## politeness score
            res = score_text(sentence)
            label, impolite_score, polite_score = res[0], res[1], res[2]

            ## strategies feedback
            doc = PolitenessFeatureVectorizer.preprocess([sentence])[0]
            strategies = get_feedback(doc)
            for strat in strategies:
                strategies_set.add(strat[0])
                highlight_index_set.add(strat[1][0])
            sent_politeness_res.append( (sentence, label, impolite_score, polite_score, strategies) )
        
        print("PER SENTENCE POLITENESS\n", sent_politeness_res)

        now = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
        cur.execute("INSERT INTO Input (user_id, message, time_stamp) VALUES (%s, %s, %s)", (g.user, input_text, now))
        cur.execute("SELECT input_id FROM Input WHERE time_stamp = %s", (now,))
        input_id = cur.fetchone()[0]

        cur.execute("INSERT INTO Feedback_Doc (input_id, word_count, label, impoliteness_score, politeness_score) VALUES (%s, %s, %s, %s, %s)",
                    (input_id, len(input_text.split()), doc_res[0], float(doc_res[1]), float(doc_res[2])))

        for m in sent_politeness_res:
            strategies = [i[0] for i in m[4]]
            strategies_idx = [i[1] for i in m[4]]
            cur.execute(
                "INSERT INTO Feedback_Sentence (input_id, sentence_content, label, impoliteness_score, politeness_score, strategy_count, strategies, indices) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (input_id, m[0], m[1], float(m[2]), float(m[3]), len(m[4]), str(strategies), str(strategies_idx)))

        mysql.connection.commit()
        print(strategies)
        # cur.execute("""SELECT * FROM Input""")
        # print(cur.fetchall(), '\n')
        # cur.execute("""SELECT * FROM Feedback_Doc""")
        # print(cur.fetchall(), '\n')
        # cur.execute("""SELECT * FROM Feedback_Sentence""")
        # print(cur.fetchall(), '\n')
        cur.close()
        # return render_template('feedback.html', user_input=input_text, label_string=label_string, impoliteness_score=impoliteness_score, politeness_score=politeness_score, strategies=strategies, grammar_msg=grammar_corrections, repl=replacements, split_inputs=split_input, num_errors=num_corrections, mistakes=wrong_words, impolite_ind=impolite_indices, impolite_words=impolite_words)
    return render_template('new_feedback.html',label_string = label_string, user_input = input_text, title = title,strategies_list = strategies_set, strategies = strategies, highlight_index = highlight_index_set)


login = False
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=4444)  # Use this for Google Cloud"
