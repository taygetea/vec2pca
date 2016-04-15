import os
from flask import send_from_directory
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from vec2pca import main as vec2pca
import glob
RESULTS_FOLDER = 'results'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER


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
                results_file = '.'.join(results_file.split('.')[:-1]) + '.csv'
            else:
                results_file = results_file + '.csv'
            results_file = results_file + ".html"
            file.save(upload_file)
            results = vec2pca(upload_file, results_file)

            return redirect(url_for('uploaded_file',
                                    filename=os.path.split(results_file)[1]))
    html = '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
    fnames = glob.glob(os.path.join(app.config['RESULTS_FOLDER'], '*.*'))
    links = ['<p><a href="%s">%s</a></p>' % (fname, os.path.split(fname)[1]) for fname in fnames]
    html += '\n'.join(links)
    return html



@app.route('/results/<filename>')
def uploaded_file(filename):
    header = '''
    <html>
    <head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.6/css/materialize.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.6/js/materialize.min.js"></script>
    </head>
    <body>
    <h1>Vec2PCA for %s</h1>
    ''' % filename

    footer = '''
    </body></html>
    '''
    # return header + send_from_directory(app.config['RESULTS_FOLDER'], filename) + footer
    with open(os.path.join(app.config['RESULTS_FOLDER'], filename)) as f:
        return header + f.read().replace('class="dataframe"', 'class="centered"') + footer


if __name__ == "__main__":
    app.run()
