from app import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

@app.route('/database/session/<page>', methods=['GET', 'POST','DELETE'])
def on_session(page):
    dataEntry_int = forms.dataEntry_int()
    dataEntry_poly = forms.dataEntry_poly()
    dataEval = forms.dataEval()
    dataDecrypt = forms.dataDecrypt()
    dataDelete = forms.dataDelete()

    session['pickle_path'] = str(pathlib.Path(__file__).parent.parent.absolute() / 'etc' / str(session['session_name']+'.p'))

    if request.method == "POST":

        session['decrypted'] = None

        # validates data entry form
        if dataEntry_int.validate_on_submit():

            session_obj = jsonpickle.decode(session['session_obj'])

            # TODO ... Overwrite
            if dataEntry_int.data_label_int.data in session_obj.set:
                session.pop('_flashes', None)
                flash("Label exists in this session. Try another label or delete this label first.", "error")

            else:
                x = FHE_Integer.FHE_Integer(dataEntry_int.data_field_int.data, session_obj.fhe.m, session_obj.fhe.p)
                encrypted = x.encrypt()
                set_id = apis.create_data(encrypted.x_prime, encrypted.q)
                session_obj.set[dataEntry_int.data_label_int.data] = {"q": encrypted.q,
                                                                      "p": encrypted.p,
                                                                      "set_id": set_id}
                encrypted = None
                session['label_list'].append(dataEntry_int.data_label_int.data)
                session.pop('_flashes', None)
                flash("Data created", "success")

            session['session_obj'] = jsonpickle.encode(session_obj)
            return redirect(url_for('on_session', page=page))


        elif dataEntry_int.submit_int.data and dataEntry_int.validate_on_submit() == False:
            session.pop('_flashes', None)
            flash("Invalid Label (AlphaDash) or Data (Integer). Please try again.", "error")

        if dataEval.validate_on_submit():

            session_obj = jsonpickle.decode(session['session_obj'])

            # TODO ... Overwrite
            if dataEval.data_label_eval.data in session_obj.set:
                session.pop('_flashes', None)
                flash("Label exists in this session. Try another label.", "error")
            else:
                parser = Parser()
                try:
                    expr = parser.parse(dataEval.data_field_eval.data).simplify({})
                    expr_str = expr.toString()
                    var = expr.variables()
                    if len(var) < 1:
                        session.pop('_flashes', None)
                        flash("Expression needs to have at least one variable. Please try another expression", "error")
                    else:
                        for i in var:
                            expr_str = expr_str.replace(i, "")
                        if any(c not in '(+-*)1234567890' for c in expr_str):
                            session.pop('_flashes', None)
                            flash("Only +,-,*,() are allowed. Please consult the Usage Guide.", "error")
                        elif any(l not in session_obj.set for l in var):
                            session.pop('_flashes', None)
                            flash("Label(s) in the expression doesn't exist. Please try again.", "error")
                        elif any(l=='tmp' for l in var):
                            session.pop('_flashes', None)
                            flash("tmp is a reserved keyword. Please try again.", "error")
                        else:
                            expr_str = expr.toString()
                            expr_obj = expr.toString()
                            # Resolve numerical values to FHE Objects
                            tmp_split = expr.toString().replace('(', ' ( ').replace(')', ' ) ').replace('+', ' + ').replace('-', ' - ').replace('*', ' * ').split(" ")
                            for i in tmp_split:
                                if i in session_obj.set: # resolve variables
                                    curr_int = session_obj.set.get(i)
                                    expr_str = re.sub(r'\b'+i+r'\b', curr_int['set_id'], expr_str) # translates labels to ids
                                    x_prime = apis.get_encrypted(curr_int['set_id'])
                                    enc_str  = 'FHE_Integer.FHE_Integer_Enc(' +  str(x_prime) + ',' + str(curr_int['q']) + ',' +  str(session_obj.fhe.m) + ',' + str(curr_int['p']) + ')'
                                    expr_obj = re.sub(r'\b'+i+r'\b', enc_str, expr_obj)
                                elif i not in '(+-*)' and i.isalpha()==False: # resolve numericals
                                    x = FHE_Integer.FHE_Integer(int(i), session_obj.fhe.m, session_obj.fhe.p)
                                    encrypted = x.encrypt()
                                    set_id = apis.create_data(encrypted.x_prime, encrypted.q)
                                    session_obj.set[i] = {"q": encrypted.q,
                                                          "p": encrypted.p,
                                                          "set_id": set_id}

                                    expr_str = re.sub(r'\b'+i+r'\b', set_id, expr_str) # translates labels to ids
                                    enc_str = 'FHE_Integer.FHE_Integer_Enc(' +  str(encrypted.x_prime) + ',' + str(encrypted.q) + ',' +  str(session_obj.fhe.m) + ',' + str(session_obj.fhe.p) + ')'
                                    expr_obj = re.sub(r'\b'+i+r'\b', enc_str, expr_obj)
                            server_eval_id = apis.create_eval(expr_str)
                            session_obj.set[dataEval.data_label_eval.data] = {"q": eval(expr_obj).q,
                                                                              'p': eval(expr_obj).p,
                                                                              "set_id": server_eval_id}
                            session['label_list'].append(dataEval.data_label_eval.data)
                            session.pop('_flashes', None)
                            flash("Expression created", "success")
                except Exception as e:
                    print("error ", e)
                    session.pop('_flashes', None)
                    flash("Illegal expression. Please consult the Usage Guide.", "error")

                session['session_obj'] = jsonpickle.encode(session_obj)
                return redirect(url_for('on_session', page=page))

        elif dataEval.submit_eval.data and dataEval.validate_on_submit() == False:
            session.pop('_flashes', None)
            flash("Invalid Label (AlphaDash) or Expression. Please try again.", "error")

        if dataDecrypt.validate_on_submit():
            session_obj = jsonpickle.decode(session['session_obj'])

            if dataDecrypt.data_label_decrypt.data not in session_obj.set:
                session.pop('_flashes', None)
                flash("Label does not exist in this session. Use another label.", "error")

            else:
                int_obj = session_obj.set[dataDecrypt.data_label_decrypt.data]
                x_prime = apis.get_encrypted(int_obj['set_id'])
                q = int_obj['q']
                p = int_obj['p']
                # TODO ... overlay window for decrypt
                session['decrypted'] = [dataDecrypt.data_label_decrypt.data, session_obj.fhe.decrypt_int(x_prime, q, p)]
                session.pop('_flashes', None)
                flash("Decrypted", "success")

            session['session_obj'] = jsonpickle.encode(session_obj)
            return redirect(url_for('on_session', page=page))


        elif dataDecrypt.submit_decrypt.data and dataDecrypt.validate_on_submit() == False:
            session.pop('_flashes', None)
            flash("Invalid Label (AlphaDash). Please try again.", "error")

        if dataDelete.validate_on_submit():
            session_obj = jsonpickle.decode(session['session_obj'])

            if dataDelete.data_label_delete.data not in session_obj.set:
                session.pop('_flashes', None)
                flash("Label does not exist in this session. Use another label.", "error")

            else:
                deleted = apis.delete_data(session_obj.set.get(dataDelete.data_label_delete.data)['set_id'])
                if deleted:
                    session['label_list'].remove(dataDelete.data_label_delete.data)
                    session_obj.set.pop(dataDelete.data_label_delete.data)
                    session.pop('_flashes', None)
                    flash("Deleted", "success")
                else:
                    session.pop('_flashes', None)
                    flash("Something's wrong on the server side.", "error")

            session['session_obj'] = jsonpickle.encode(session_obj)
            return redirect(url_for('on_session', page=page))

        if request.form.get('delete') == 'true':
            flash("Session Deleted.", "info")
            return url_for('about')

        if request.form.get('download') == 'true':
            session_obj = jsonpickle.decode(session['session_obj'])
            for i in session_obj.set.values():
                x = apis.get_server_int(i['set_id'])
                session_obj.all_int_set.append(x)
            pickle.dump( session_obj, open(session['pickle_path'] , "wb" ) )
            session_obj = None
            session['session_obj'] = None
            flash("Session Downloaded.", "info")
            return url_for('about')

    return render_template('session.html', page=page,
                           dataEntry_int=dataEntry_int,
                           dataEntry_poly=dataEntry_poly,
                           dataEval=dataEval,
                           dataDecrypt=dataDecrypt,
                           dataDelete=dataDelete)
