import os
from flask import *
from werkzeug import secure_filename
from vec2pca import vec2pca
import glob
from flask.ext.mail import Mail, Message
from celery import Celery
import pandas as pd

RESULTS_FOLDER = 'results'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = "taygeteatesting@gmail.com"



# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_IMPORTS'] = ('tasks.runmodel', )


# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], include=['app.tasks'])
celery.conf.update(app.config)

@celery.task(name="tasks.runmodel")
def runmodel(upload, result):
    return vec2pca(upload, result)

@celery.task(bind=True)
def long_task(self, function, *args):
    """Background task that runs a long function with progress reports."""

    result = function(*args)
    vec2pca("~/datascience/vec2pca/web/uploads/jsmSmaller.txt", "~/datascience/vec2pca/web/results/jsmtest.csv")
    return result.get()

@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")



def results_files():
    return glob.glob(os.path.join(app.config['RESULTS_FOLDER'], '*.*'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def load_table(filename, rows=25):
    with open(os.path.join(app.config['RESULTS_FOLDER'], filename)) as f:
        table = f.read().replace('class="dataframe"', 'class="centered striped"')
        splitup = table.split('</thead>')
        index = splitup[0] + '</thead>'
        body = splitup[1].replace('<tbody>', '').split('</tbody>')[0]
        head = index + "</tr>".join(body.split("</tr>")[:rows]) + "</tr>" + '</tbody>'
        tail = index + "<tr>" + "<tr>".join(body.split("</tr>")[-rows:]) + '</tbody>'
        # import pdb; pdb.set_trace()
        return table, head, tail


# @app.route('/', methods=['GET'])
# def main():
#     fnames = [os.path.split(n)[1] for n in results_files()]
#     return render_template('index.html', filenames=fnames)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    fnames = [os.path.split(n)[1] for n in results_files()]
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            upload_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            results_file = os.path.join(app.config['RESULTS_FOLDER'], filename)
            if "." in results_file[-6:]:
                results_file = '.'.join(results_file.split('.')[:-1]) + '.html'
            else:
                results_file = results_file + '.html'

        msg = Message('Hello from Flask',
                       recipients=[request.form['email']])
        msg.body = 'This is a test email sent from a background Celery task. http://localhost:5000/%s' % results_file
        if request.form['submit'] == 'Send':
            send_async_email.delay(msg)
            #mail.send(msg)
            flash('Sending email to {0}'.format(email))

        if upload_file != 'uploads/':
            result = long_task.delay(vec2pca, [upload_file, results_file[:-5]])
            _df, df = result.get()
            components = []
            for i in range(1,9):
                components.append({
                    "name": "PC%d" % i,
                    "top": " ".join(df.iloc[0:200,i]),
                    "bottom": " ".join(list(df.iloc[-200:,i])[::-1])})

            #ajax_table, thead, ttail = load_table(os.path.split(results_file)[1])
            return render_template('upload.html', components=components)
    return render_template('upload.html', filenames="", thead="", ttail="")

@app.route('/ajax', methods=['POST'])
def dropdown():
    filename = request.form['filename']
    table, thead, ttail = load_table(filename)
    return jsonify(filename=table, thead=thead, ttail=ttail)

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/results/<filename>')
def result(filename):
    df = pd.read_csv(os.path.join(app.config['RESULTS_FOLDER'], filename))

    components = []
    for i in range(1,9):
        components.append({
        "name": "PC%d" % i,
        "top": " ".join(df.iloc[0:200,i]),
        "bottom": " ".join(list(df.iloc[-200:,i])[::-1])})
    print(components[0])
    return render_template('result.html', components=components)

if __name__ == "__main__":
    app.run(debug=True)

