import os
from flask import *
from werkzeug import secure_filename
from vec2pca import main as vec2pca
import glob
RESULTS_FOLDER = 'results'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

def results_files():
    return glob.glob(os.path.join(app.config['RESULTS_FOLDER'], '*.*'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            upload_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            results_file = os.path.join(app.config['RESULTS_FOLDER'], filename)
            if "." in results_file[-6:]:
                results_file = '.'.join(results_file.split('.')[:-1]) + '.html'
            else:
                results_file = results_file + '.html'
            file.save(upload_file)
            results = vec2pca(upload_file, results_file)

            return redirect(url_for('uploaded_file',
                                    filename=os.path.split(results_file)[1]))
    links = [{'link': fname, 'text': os.path.split(fname)[1]} for fname in results_files()]
    fnames = [os.path.split(n)[1] for n in results_files()]
    return render_template('index.html', links=links, filenames=fnames)



@app.route('/results/<filename>')
def uploaded_file(filename):
    with open(os.path.join(app.config['RESULTS_FOLDER'], filename)) as f:
        html = f.read().replace('class="dataframe"', 'class="centered"')
    return render_template('result.html', table=html, filename=filename)

@app.route('/select.html')
def get_table():
    fnames = [os.path.split(n)[1] for n in results_files()]
    return render_template('select.html', filenames=fnames)

@app.route('/ajax', methods=['POST'])
def dropdown():
    filename = request.form['filename']
    with open(os.path.join(app.config['RESULTS_FOLDER'], filename)) as f:
        table_html = f.read().replace('class="dataframe"', 'class="centered"')
    return jsonify(filename=table_html)


if __name__ == "__main__":
    app.run(debug=True)
