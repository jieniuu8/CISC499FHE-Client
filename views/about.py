from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/', methods=['GET', 'POST', 'DELETE'])
@app.route('/about')
def about():

    session['label_list'] = []

    return render_template('about.html',
                           page='About')
