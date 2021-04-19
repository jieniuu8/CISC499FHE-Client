from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/database/connect', methods=['GET', 'POST'])
def connect():

    # if current session is still saves in cookies, return to that session
    if session.get('session_obj'):
        session.pop('_flashes', None)
        flash('Returned to the previous unsaved session.', 'info')
        session_obj = jsonpickle.decode(session['session_obj'])
        #remove decrypted value from session to prevent shown on the screen after other requests
        if session.get('decrypted'):
            session.pop('decrypted')
        return redirect(url_for('on_session', page=session_obj.getName()))

    # initialize form
    ipform = forms.IPForm()

    server_connected = False
    if request.method == "POST":

        if ipform.validate_on_submit():
            # try server connection and if responding
            try:
                server_connected = apis.connect_server(ipform.ip.data, ipform.port.data)
                if server_connected == True:
                    session['ip'], session['port'] = ipform.ip.data, ipform.port.data
                    session.pop('_flashes', None)
                    flash('Successfully connected to the server.', 'success')
                    return redirect(url_for('login'))
                else:
                    session.pop('_flashes', None)
                    flash('Unable to connect to server.', 'error')
            except:
                session.pop('_flashes', None)
                flash('Unable to reach the server. Please check if you have FHE_Server setup properly.', "error")

        if not ipform.validate_on_submit():
            session.pop('_flashes', None)
            flash('Invalid IP Address or Port. Please try again.', "error")
            return redirect(url_for('connect'))

    return render_template('connect.html', page='Database Connect', ipform=ipform)
