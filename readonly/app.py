import os
from flask import *
import pandas as pd

app = Flask(__name__)
app.config['RESULTS_FOLDER'] = "results"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


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
        "top": "  ".join(df.iloc[0:200,i]),
        "bottom": "  ".join(list(df.iloc[-200:,i])[::-1])})
    return render_template('result.html', components=components)

if __name__ == "__main__":
    app.run(debug=True)

