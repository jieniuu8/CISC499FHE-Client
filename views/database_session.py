from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/database/session/<page>', methods=['GET', 'POST','DELETE'])
def on_session(page):

    # Forms Initialization
    dataEntry_int = forms.dataEntry_int()
    dataEntry_poly = forms.dataEntry_poly()
    dataEval = forms.dataEval()
    dataDecrypt = forms.dataDecrypt()
    dataDelete = forms.dataDelete()

    # Get current path from system to save file later
    if session.get('session_name'):
        session['pickle_path'] = str(pathlib.Path(__file__).parent.parent.absolute() / 'etc' / str(session['session_name']+'.p'))

    # Protect the end point (i.e. not allow user to go to a uncreated session)
    if request.method == "GET":
        # If session has never been created
        if session.get('session_name') == None:
            session.pop('_flashes', None)
            flash("Unauthorized. Please create a new session or upload a session file.", "error")
            return redirect(url_for('about'))
        # If session was created but not same name in the endpoint
        elif session.get('session_name') != None:
            if page != session['session_name']:
                session.pop('_flashes', None)
                flash("Unauthorized. Please save or delete the previous session.", "error")
                return redirect(url_for('about'))
        try:
            server_connected = apis.connect_server(session['ip'], session['port'])
        except:
            session.pop('_flashes', None)
            flash("Server Error. Please check if you have FHE_Server enabled.", "error")

    if request.method == "POST":

        try:
            server_connected = apis.connect_server(session['ip'], session['port'])

            #remove decrypted value from session to prevent shown on the screen after other requests
            if session.get('decrypted'):
                session.pop('decrypted')

            # validates data entry form
            if dataEntry_int.validate_on_submit():

                session_obj = jsonpickle.decode(session['session_obj'])

                # If data label exists
                if dataEntry_int.data_label_int.data in session_obj.set:
                    session.pop('_flashes', None)
                    flash("Label exists in this session. Try another label or delete this label first.", "error")

                # encrypt integer and sent to server
                else:
                    x = FHE_Integer.FHE_Integer(dataEntry_int.data_field_int.data, session_obj.fhe.m, session_obj.fhe.p)
                    encrypted = x.encrypt()
                    set_id = apis.create_data(encrypted.x_prime, encrypted.q)
                    # save q and p as local variable for data_eval and decryption to verify
                    session_obj.set[dataEntry_int.data_label_int.data] = {"q": encrypted.q,
                                                                          "p": encrypted.p,
                                                                          "set_id": set_id}
                    encrypted = None
                    if session.get('label_list'):
                        session['label_list'].append(dataEntry_int.data_label_int.data)
                    else:
                        session['label_list'] = [dataEntry_int.data_label_int.data]
                    session.pop('_flashes', None)
                    flash("Data created", "success")

                session['session_obj'] = jsonpickle.encode(session_obj)
                return redirect(url_for('on_session', page=page))

            # Data entry validation error: if label is not in a python-like variable name
            elif dataEntry_int.submit_int.data and dataEntry_int.validate_on_submit() == False:
                session.pop('_flashes', None)
                flash("Invalid Label or Data (Integer). Please consult the Usage Guide and try again.", "error")


            # Data evaluation form
            if dataEval.validate_on_submit():

                session_obj = jsonpickle.decode(session['session_obj'])

                # If data label exists
                if dataEval.data_label_eval.data in session_obj.set:
                    session.pop('_flashes', None)
                    flash("Label exists in this session. Try another label or delete this label first.", "error")

                # parse equation the user entered
                else:
                    parser = Parser()
                    # Try-catch block: throw error if in the process of parsing
                    try:
                        expr = parser.parse(dataEval.data_field_eval.data).simplify({})
                        expr_str = expr.toString()
                        var = expr.variables() # get a list of non-numerical variables
                        if len(var) < 1:
                            session.pop('_flashes', None)
                            flash("Expression needs to have at least one variable. Please try another expression", "error")
                        else:
                            # remove variables to validate user's equation
                            for i in var:
                                expr_str = expr_str.replace(i, "")
                            # detect any other invalid symbols
                            if any(c not in '(+-*)1234567890' for c in expr_str):
                                session.pop('_flashes', None)
                                flash("Only +,-,*,() are allowed. Please consult the Usage Guide.", "error")
                            # detect if any variables user entered exist
                            elif any(l not in session_obj.set for l in var):
                                session.pop('_flashes', None)
                                flash("Label(s) in the expression doesn't exist. Please try again.", "error")
                            else:
                                # After testing the equation is valid
                                expr_str = expr.toString()
                                expr_obj = expr.toString()
                                # Resolve numerical values to FHE Objects
                                # get extra space near the axioms and brackets for better parsing
                                tmp_split = expr.toString().replace('(', ' ( ').replace(')', ' ) ').replace('+', ' + ').replace('-', ' - ').replace('*', ' * ').split(" ")
                                for i in tmp_split:
                                    # resolve variables
                                    if i in session_obj.set:
                                        curr_int = session_obj.set.get(i) # get q,p,server_id for the var
                                        expr_str = re.sub(r'\b'+i+r'\b', curr_int['set_id'], expr_str) # translates labels to ids using regex
                                        x_prime = apis.get_encrypted(curr_int['set_id']) # get the x' from the server
                                        # recalcutaes the padding and quotient needed for all variables
                                        enc_str  = 'FHE_Integer.FHE_Integer_Enc(' +  str(x_prime) + ',' + str(curr_int['q']) + ',' +  str(session_obj.fhe.m) + ',' + str(curr_int['p']) + ')'
                                        expr_obj = re.sub(r'\b'+i+r'\b', enc_str, expr_obj)
                                    # resolve numericals (has to be integer as in before validation, no dot allowed in equation)
                                    elif i not in '(+-*)' and i.isalpha()==False:
                                        # encrypt that integer and send to server
                                        x = FHE_Integer.FHE_Integer(int(i), session_obj.fhe.m, session_obj.fhe.p)
                                        encrypted = x.encrypt()
                                        set_id = apis.create_data(encrypted.x_prime, encrypted.q)
                                        # session_obj.set[i] = {"q": encrypted.q,
                                        #                       "p": encrypted.p,
                                        #                       "set_id": set_id}
                                        expr_str = re.sub(r'\b'+i+r'\b', set_id, expr_str) # translates labels to ids
                                        # recalcutaes the padding and quotient needed for all variables
                                        enc_str = 'FHE_Integer.FHE_Integer_Enc(' +  str(encrypted.x_prime) + ',' + str(encrypted.q) + ',' +  str(session_obj.fhe.m) + ',' + str(session_obj.fhe.p) + ')'
                                        expr_obj = re.sub(r'\b'+i+r'\b', enc_str, expr_obj)
                                # send the euqation of server ids to the server
                                server_eval_id = apis.create_eval(expr_str)
                                # get the new p,q,setid to the associated label, this utilizes Python's eval function: Compile and run a command in string type
                                session_obj.set[dataEval.data_label_eval.data] = {"q": eval(expr_obj).q,
                                                                                  'p': eval(expr_obj).p,
                                                                                  "set_id": server_eval_id}
                                session['label_list'].append(dataEval.data_label_eval.data)

                                session.pop('_flashes', None)
                                flash("Expression created", "success")
                    except Exception as e:
                        print("error ", e)
                        session.pop('_flashes', None)
                        flash("Something went wrong. Please consult the Usage Guide.", "error")

                    session['session_obj'] = jsonpickle.encode(session_obj)
                    return redirect(url_for('on_session', page=page))

            # if label is not in a python-like variable name
            elif dataEval.submit_eval.data and dataEval.validate_on_submit() == False:
                session.pop('_flashes', None)
                flash("Invalid Label or Expression. Please consult the Usage Guide and try again.", "error")

            # Data decryption form
            if dataDecrypt.validate_on_submit():
                session_obj = jsonpickle.decode(session['session_obj'])

                # If data label does not exist
                if dataDecrypt.data_label_decrypt.data not in session_obj.set:
                    session.pop('_flashes', None)
                    flash("Label does not exist in this session. Use another label.", "error")
                else:
                    int_obj = session_obj.set[dataDecrypt.data_label_decrypt.data] # get server_id
                    x_prime = apis.get_encrypted(int_obj['set_id'])
                    q,p = int_obj['q'], int_obj['p']
                    # decrypt and pass the data to HTML
                    session['decrypted'] = [dataDecrypt.data_label_decrypt.data, session_obj.fhe.decrypt_int(x_prime, q, p)]
                    session.pop('_flashes', None)
                    flash("Decrypted", "success")
                    session['session_obj'] = jsonpickle.encode(session_obj)
                    return redirect(url_for('on_session', page=page))


            elif dataDecrypt.submit_decrypt.data and dataDecrypt.validate_on_submit() == False:
                session.pop('_flashes', None)
                flash("Invalid Label. Please try again.", "error")

            # Data deletion form
            if dataDelete.validate_on_submit():
                session_obj = jsonpickle.decode(session['session_obj'])

                if dataDelete.data_label_delete.data not in session_obj.set:
                    session.pop('_flashes', None)
                    flash("Label does not exist in this session. Try another label.", "error")

                else:
                    # Send api call to server to delete data
                    deleted = apis.delete_data(session_obj.set.get(dataDelete.data_label_delete.data)['set_id'])
                    if deleted:
                        # remove data from client
                        session['label_list'].remove(dataDelete.data_label_delete.data)
                        session_obj.set.pop(dataDelete.data_label_delete.data)
                        session.pop('_flashes', None)
                        flash("Data Deleted", "success")
                    else:
                        session.pop('_flashes', None)
                        flash("Something's wrong on the server side.", "error")

                session['session_obj'] = jsonpickle.encode(session_obj)
                return redirect(url_for('on_session', page=page))


            # Session Management
            # Delete entire session data from the server
            if request.form.get('delete') == 'true':
                # if not NoneType, 'label_list' would be a [], meaning there was data entered then deleted
                if session.get('label_list'):
                    deleted = apis.delete_session(session["server_id"])
                    if deleted:
                        session.clear()
                        flash("Session Deleted.", "success")
                        return url_for('about')
                    else:
                        session.clear()
                        flash("Session Deleted on this computer. But some error happened on the server.", "info")
                        return url_for('about')
                # if NoneType, 'label_list' has never been initialized, and no session was created in the server
                else:
                    session.clear()
                    flash("Session Deleted.", "success")
                    return url_for('about')

            # Download entire session to binary file
            if request.form.get('download') == 'true':
                session_obj = jsonpickle.decode(session['session_obj'])
                # get all server data for a session by api
                for i in session_obj.set.values():
                    x = apis.get_server_int(i['set_id'])
                    session_obj.all_int_set.append(x)
                # put in a binary pickle file that python supports
                pickle.dump( session_obj, open(session['pickle_path'] , "wb" ) )

                # security safegaurd - delete all relevant info from cookie and from server
                deleted = apis.delete_session(session["server_id"])
                session.clear()

                session.pop('_flashes', None)
                flash("Session Downloaded.", "info")
                return url_for('about')

        except:
            session.pop('_flashes', None)
            flash("Server Error. Please check if you have FHE_Server enabled.", "error")


    return render_template('session.html', page=page,
                           dataEntry_int=dataEntry_int,
                           dataEntry_poly=dataEntry_poly,
                           dataEval=dataEval,
                           dataDecrypt=dataDecrypt,
                           dataDelete=dataDelete)
