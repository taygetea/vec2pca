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


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    fnames = [os.path.split(n)[1] for n in results_files()]
    ajax_table = ''
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
            print(1)
            ajax_table, thead, ttail = load_table(os.path.split(results_file)[1])
            print(2)
            return render_template('index.html', filenames=fnames,
                ajax_table=ajax_table, thead=thead, ttail=ttail)
    print(3)
    return render_template('index.html', filenames=fnames, thead="", ttail="")



@app.route('/results/<filename>')
def uploaded_file(filename):
    table, thead, ttail = load_table(filename)
    return render_template('result.html', table=table, thead=thead, ttail=ttail, filename=filename)

@app.route('/ajax', methods=['POST'])
def dropdown():
    filename = request.form['filename']
    table, thead, ttail = load_table(filename)
    return jsonify(filename=table, thead=thead, ttail=ttail)

@app.route('/debug')
def page():
    return render_template('debug.html')

if __name__ == "__main__":
    app.run(debug=True)
