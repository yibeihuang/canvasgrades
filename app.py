import requests
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os,csv
import json
import flask_login
import uuid
from collections import OrderedDict

app = Flask(__name__)

# in order to use sessions you have to set a secret key
app.secret_key = 'Idontknowwhatthisusedfor'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# mock the authenticated user
users = {'ssolreader':{'password':'23hrp8ddvnq394tuh90'}}

class User(flask_login.UserMixin):
    pass

'''
You will need to provide a user_loader callback. This callback is used to reload the user object
from the user ID stored in the session. It should take the unicode ID of a user, and return the
corresponding user object.
'''
@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return 'Wrong Operation'

    user_username = request.args.get('username')
    user_password = request.args.get('password')

    if user_password == users[user_username]['password']:
        user = User()
        user.id = uuid.uuid4() 
        flask_login.login_user(user)
        return redirect(url_for('protected'))

# for now, I just use protected to test if the grades will be blocked without valid session ID
@app.route('/protected')
@flask_login.login_required
def protected():
    return redirect(url_for('grades'))

@app.route("/grades", methods=["GET"])
def grades():
    r = requests.get('https://columbiasce.test.instructure.com/api/v1/courses/5745/enrollments', \
                headers={'Authorization': 'Bearer 1396~WRVwsmQkgBoOBzVnaImwbAmpQkPDsyx9ZHEJaJ5cdL32lsQTwSFld68NhimNTPQ4'})

    data = bytes.decode(r._content)
    xbox = json.loads(data)
    """
    need stores the three-column data including 'Student Name','Student ID','Final_grade'
    """
    need = []
    for i in range(0,len(xbox)):
        try:
            need.append(OrderedDict({'Student Name':xbox[i]['user']['name'], \
                    'Student ID':xbox[i]['user']['login_id'], \
                    'Course Grade':xbox[i]['grades']['final_grade']}))
        except:
            pass
    print(need)
    keys = need[0].keys()
    with open('info.csv','w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, extrasaction='ignore',delimiter=',')
        dict_writer.writeheader()
        dict_writer.writerows(need)
    string = ''
    with open('info.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\n')
        for row in spamreader:
            string = '\n'.join([string, row[0]])
    return string

@app.route("/submitgrades", methods=['GET', 'POST'])
def submitgrades(name=None):
    return render_template('submitgrade.html', name=name)

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True, host='192.168.33.10', port=5000)

