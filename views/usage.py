from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/usage', methods=['GET', 'POST'])
def usage():

    file = open("readme.md")
    md = file.read()
    file.close()
    return render_template('usage.html', md=md, page="Usage Guide")
