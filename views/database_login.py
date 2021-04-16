from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/database/login', methods=['GET', 'POST'])
def login():
    session['label_list'] = []
    # if user closed broswer window or cookie expired
    if session.get('ip') is None:
        flash('Session expired. Please reconnect to the server.', "info")
        return redirect(url_for('connect'))
    # if current session is still saves in cookies, return to that session
    # if session['session_obj']:
    #     flash('Returned to the previous unsaved session.', 'info')
    #     session_obj = jsonpickle.decode(session['session_obj'])
    #     return redirect(url_for('on_session', page=session_obj.getName()))

    newSessionConfig = forms.configNewSession()
    fileForm = forms.fileForm()

    if request.method == "POST":
        # If clicked on new session submit
        if newSessionConfig.validate_on_submit():
            # Check if session of same name under one public ip exists
            # checkExist = apis.exist_session(newSessionConfig.session_name.data)
            # if type(checkExist) == bool and checkExist == True:
            #     session.pop('_flashes', None)
            #     flash("This session name is used. Please upload the file or enter a new name.", 'error')
            #     return redirect(url_for('login'))
            # else:

            apis.create_session()
            new_session = users.Session()
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

        elif newSessionConfig.session_name.data and validate_on_submit()==False:
            session.pop('_flashes', None)
            flash("You have entered a invalid session name. Name should only contain letters.", "error")
            return redirect(url_for('login'))

        # TODO ... FILE UPLOAD
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

    return render_template('login.html', newSessionConfig=newSessionConfig, fileForm=fileForm, page="Database Login")
