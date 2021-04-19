from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/database/login', methods=['GET', 'POST'])
def login():

    # if current session is still saves in cookies, return to that session
    if session.get('session_obj'):
        flash('Returned to the previous unsaved session.', 'info')
        session_obj = jsonpickle.decode(session['session_obj'])
        return redirect(url_for('on_session', page=session_obj.getName()))

    # Initialize forms
    newSessionConfig = forms.configNewSession()
    fileForm = forms.fileForm()

    # Check if server is live
    if request.method == "GET":
        try:
            server_connected = apis.connect_server(session['ip'], session['port'])
        except:
            session.pop('_flashes', None)
            flash("Server Error. Please check if you have FHE_Server enabled.", "error")

    if request.method == "POST":

        try:
            server_connected = apis.connect_server(session['ip'], session['port'])

            # If clicked on new session submit
            if newSessionConfig.validate_on_submit():
                # create a new session in the database
                try:
                    apis.create_session()
                except:
                    session.pop('_flashes', None)
                    flash('Unable to reach the server. Please check if you have FHE_Server setup properly.', "error")

                new_session = users.Session()   # create a new session object
                new_session.setName(newSessionConfig.session_name.data)
                new_session.setKeySize(newSessionConfig.key_size.data)
                new_session.setServerId(session['server_id'])
                new_session.setFHEObject(newSessionConfig.data_type.data)

                # session cookie for other views
                session['session_obj'] = jsonpickle.encode(new_session)
                session['session_name'] = newSessionConfig.session_name.data
                session['key_size'] = newSessionConfig.key_size.data
                session['data_type'] = newSessionConfig.data_type.data

                session.pop('_flashes', None)
                flash("New Session created.", "success")
                return redirect(url_for('on_session', page=session['session_name']))

            elif newSessionConfig.session_name.data and newSessionConfig.validate_on_submit()==False:
                session.pop('_flashes', None)
                flash("You have entered a invalid session name. Name should only contain letters.", "error")
                return redirect(url_for('login'))

            # FILE UPLOAD
            if fileForm.validate_on_submit():
                try:
                    apis.create_session()
                    session_obj = pickle.load(fileForm.file.data)
                    session['session_name'] = session_obj.session_name
                    session['key_size'] = session_obj.key_size
                    session['data_type'] = session_obj.data_type
                    session['label_list'] = list(session_obj.set.keys())
                    apis.upload_session(session_obj.all_int_set)
                    session_obj.all_int_set = None
                    session['session_obj'] = jsonpickle.encode(session_obj)

                    session.pop('_flashes', None)
                    flash("File loaded successful.", "success")
                    return redirect(url_for('on_session', page=session['session_name']))

                except Exception as e:
                    print("error: ", e)
                    session.pop('_flashes', None)
                    flash("The file was corrupted. Please create a new session.", "error")
                    return redirect(url_for('login'))

        except:
            session.pop('_flashes', None)
            flash("Server Error. Please check if you have FHE_Server enabled.", "error")

            
    return render_template('login.html', newSessionConfig=newSessionConfig, fileForm=fileForm, page="Database Login")
