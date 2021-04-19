## Client-side Application
<br/>

##### Table of Contents  
- [Deploy](#deploy)
- [Connect to Server](#connect)  
- [Create a New Session](#new_session)  
- [Upload Existing Session](#upload)  
- [Database Session](#session)  
- [Cookies](#cookies)
- [Acknowledgement](#cknowledgement)

<br/>

### Deploy <a name="deploy"></a>

Please download this project as a zip from GitHub, or clone/fork by using `git`.
You must have Python 3+ installed on your computer. To test open Terminal (macOS or Linux) or Command Prompt (Windows) and enter

```
$ python --version
> Python 3.8.9
```


You may upgrade your python if it's still version `2.*.*`
To install dependency packages, run the following from the command-line

```
cd <dir to project folder>
python -m pip install -r etc/config/requirements.txt
```


You may also activate a Python venv. After package installation, you may run the program from command line by

```
flask run
```


And then open a browser (Google Chrome, Firefox, Safari) and open the webpage

```
http://127.0.0.1:5000/
```


<b>Please exit from the command-line of which you run `flask run` command. This will terminate the process for this Python client application.</b>


<br/>

### Connect to Server <a name="connect"></a>
`http://127.0.0.1:5000/database/connect`

The FHE Server must be deployed and started on a computer first. Please consult the guide for the server.

- Server IP: The public/private IP address for the Django FHE Server
- Port: The port opened for Django FHE Server

<br/>


### Create a New Session <a name="new_session"></a>
`http://127.0.0.1:5000/database/login`

After connecting to the server from the above step, we can create a session.

- Session Name: A name on the local side for user to reference. It must be fully alphabetical. This name is kept local and has no real meaning in the server database.
- Key Size: A bit size for generating the modulo `m` in the encryption scheme.
- Data Type:  Only integers can be selected at this point. The field for polynomial is for future work.


<br/>

### Upload Existing Session <a name="upload"></a>
`http://127.0.0.1:5000/database/login`

On this page, we can also upload a binary file ending `*.p` to use the previous downloaded session, which will be detailed in the below sections. The section will throw an error of corruption if it's not the correct extension, or if the binary file was modified.


<br/>

### Database Session <a name="session"></a>
`http://127.0.0.1:5000/database/session/<session_name>`


###### Data Entry
- Labels: The user-assigned variables for the integers in the database. The naming follows PEP standard (just like naming Python variables). This label is kept local and is associated the integer identifiers on the server side.
- Data: The integers can be a number in an arbitrary range as Python natively support Big Integers so won't cause overflow.

###### Data Evaluation
- Labels: Save as above.
- Expression: an equation where user can input in with their created labels or new Integers. Currently it only supports `+,-,*` operations. Some examples can be:

```
abc = a + b * c
abc2 = 2 * abc
abc_neg = -1 * abc
```


###### Manage This Session
- Check Existing Labels: A list of current variables will be shown on the screen.
- Delete Current Session and All Data: This will delete the entire session and its integer data both from local and remote server.
- Download Current Session for Future Use: This will download a binary file compiled by Python Pickle Package for serializing Objects. It will be saved as `projectFolder/etc/*.p` where `*` is the session name. This will also delete the copy on the remote server side for offloading storage.


<br/>

### Cookies <a name="cookies"></a>
The application utilizes Flask's built-in session and cookie management that offers user convenience to prevent data loss.

- Inside browser: when you click on other page's link, the session cookies will be utilized to get you return to the data entry page.
- Close browser tab/window but didn't quit application: user will still be able to get back to their previous session unless they choose to delete or download.
- Quit browser application: this will clear the cookie and user won't be able to return to their unsaved session.

For security, please delete/download the session before closing the browser.

<br/>


### Acknowledgement
We thank Prof. Selim Akl for this amazing opportunity to let us get some hands-on experience to build a mathematical model and a front- and back-end application. Hope you enjoy this project and can let future student do more extensions to it.

###### Reference
- S. G. Akl, Parallel Homomorphic Cryptography: Simple, Efficient, Secure, to appear in: Parallel Processing in Nature and Silicon, Adamatzky et al., Eds., World Scientific Publishing, 2021.
