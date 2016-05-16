import os
from flask import *
from werkzeug import secure_filename
from vec2pca import main as vec2pca
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


# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        mail.send(msg)

@celery.task
def runmodel(upload, result):
    with app.app_context():
        return vec2pca(upload, result)

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


@app.route('/', methods=['GET'])
def main():
    fnames = [os.path.split(n)[1] for n in results_files()]
    return render_template('index.html', filenames=fnames)

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
            results = runmodel(upload_file, results_file)
            ajax_table, thead, ttail = load_table(os.path.split(results_file)[1])
            return render_template('upload.html', filenames=fnames,
                ajax_table=ajax_table, thead=thead, ttail=ttail)
    return render_template('upload.html', filenames="", thead="", ttail="")

@app.route('/results/<filename>')
def uploaded_file(filename):
    table, thead, ttail = load_table(filename)
    return render_template('result.html', table=table, thead=thead, ttail=ttail, filename=filename)

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

@app.route('/debug')
def debug():
    df = pd.read_csv("~/datascience/lw_components.csv")

    components = []
    for i in range(1,9):
        components.append({
        "name": "PC%d" % i,
        "top": " ".join(df.iloc[0:200,i])[:1300],
        "bottom": " ".join(list(df.iloc[-200:,i])[::-1])})
    print(components[0])
    return render_template('debug.html', components=components)

if __name__ == "__main__":
    app.run(debug=True)

