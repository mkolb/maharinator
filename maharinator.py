import os, csv, time
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='xxx development 123',
))
app.config.from_envvar('MAHARINATOR_SETTINGS', silent=True)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def store_file(file, t):
    if file and allowed_file(file.filename):
        f = secure_filename(file.filename)
        filename =  t + '-' + f
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        t = str(int(time.time()))
        files = []
        for f in ['enrollment', 'mahara']:
            files.append(store_file(request.files[f], t))
        return maharinate(files[0], files[1], t)

    return render_template("layout.html")

def maharinate(e, m, t):
    skips = set()
    enrollment = open(UPLOAD_FOLDER + e, "rb")
    mahara = open(UPLOAD_FOLDER + m, "rb")

    outfile = t + '-out.csv'
    out = open(UPLOAD_FOLDER + outfile, "wb")

    mr = csv.reader(mahara)
    for row in mr:
        skips.add(row[0])
    er = csv.reader(enrollment, skipinitialspace=True)
    ow = csv.writer(out)
    next(er, None) # get rid of the header
    ow.writerow(["username", "password", "firstname", "lastname", "email", "studentid"]);
    i = 0
    for row in er:
        if row[0] in skips: # don't create entries for existing users
            continue
        i += 1
        ow.writerow([row[0].strip(), "Deltak01+", row[1].strip(), row[2].strip(), row[3].strip(), row[0].strip()])
    enrollment.close()
    mahara.close()
    out.close()
    return render_template("m.html", count=i, filename=outfile)
    

@app.route('/maharinated/<filename>')
def maharinated_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
