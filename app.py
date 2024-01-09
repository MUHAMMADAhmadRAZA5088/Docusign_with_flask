from flask import Flask, render_template, request
from datetime import datetime, timedelta
import base64
import requests
import json

app = Flask(__name__)


def file_to_base64(file):
    try:
        return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file to base64: {str(e)}")
        return None


def template_to_envelope():
    url = "https://demo.docusign.net/restapi//v2.1/accounts/bd182fdb-bda4-40d6-85b5-0a452eaef7e6/envelopes"

    file_path = 'file.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    payload = json.dumps({
    "templateId": "3407aa9a-b666-4172-8416-89ff90110c04",
    "templateRoles": [
        {
        "email": "ahmadelectricaltraders@gmail.com",
        "name": "malik ahmad",
        "roleName": "Signer"
        }
    ],
    "status": "sent"
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {data['access_token']}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


def create_template(base64_data, subject_of_email):
    url = "https://demo.docusign.net/restapi//v2.1/accounts/bd182fdb-bda4-40d6-85b5-0a452eaef7e6/templates"

    file_path = 'file.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    payload = json.dumps({
    "documents": [
        {
        "name": "agreement",
        "documentBase64": f"{base64_data}",
        "documentId": "1234",
        "fileExtension": "docx"
        }
    ],
    "emailBlurb": "Email message",
    "emailSubject": f"{subject_of_email}",
    "recipients": {
        "signers": [
        {
            "recipientId": "1",
            "roleName": "seller"
        }
        ]
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {data['access_token']}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text

def create_envelope(base64_data, name, email, subject_of_email):
    url = "https://demo.docusign.net/restapi//v2.1/accounts/bd182fdb-bda4-40d6-85b5-0a452eaef7e6/envelopes"

    file_path = 'file.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    payload = json.dumps({
        "documents": [
            {
                "documentBase64": f"{base64_data}",
                "documentId": 1234,
                "fileExtension": "docx",
                "name": "Malik Ahmad"
            }
        ],
        "emailSubject": f"{subject_of_email}",
        "recipients": {
            "signers": [
                {
                    "email": f"{email}",
                    "name": f"{name}",
                    "recipientId": "451"
                }
            ]
        },
        "status": "sent"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {data['access_token']}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def access_token():
    file_path = 'file.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    # given_string = "2024-01-02 19:20:37.871016"
    given_string = data["time"]
    given_datetime = datetime.strptime(given_string, "%Y-%m-%d %H:%M:%S.%f")

    # Get the current time
    current_time = datetime.now()

    # Check the condition
    if current_time < given_datetime + timedelta(hours=7):
        return "not update"
    else:
        url = "https://account-d.docusign.com/oauth/token"

        payload = {
            'refresh_token': f'{data["refresh_token"]}',
            'grant_type': 'refresh_token'
        }

        headers = {
            'Authorization': 'Basic MDgxM2JlZGUtYjA5NS00MzNkLWE3YjUtYmJiMjVkYWY2YmQ4OjA4ZGRkZGZmLWE3NTEtNGY4Mi04MTQwLWExMDc1Y2Y0M2YzNg==',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            res = json.loads(response.text)
            res["time"] = str(current_time)

            # Read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Delete the last value
            last_key = list(data.keys())[-1]
            del data[last_key]

            # Writing dictionary to JSON file
            with open(file_path, 'w') as json_file:
                json.dump(res, json_file)





@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        subject_of_email = request.form['subject_of_email']

        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        # Convert file to base64
        base64_data = file_to_base64(file)

        # access Key docusign
        access_token()
        
        try:
            if name and email and subject_of_email and  base64_data:
                # create envelope
                envelope = create_envelope(base64_data, name, email, subject_of_email)
                # new working
                file_path = 'envelope.json'
                with open(file_path, 'r') as file:
                    data = json.load(file)
                data.append(envelope)
                print(data)
                file_path = 'envelope.json'
                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file)
                return envelope
            
        except:
            return "try again"


@app.route('/envelope_view')
def envelope_view():
    file_path = 'envelope.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    envelope_list = [json.loads(item) for item in data]
    return render_template("envelope_view.html", envelope_list = envelope_list)


@app.route('/template')
def template():
    return render_template('template.html')


@app.route('/templateUpload', methods=['POST'])
def templateUpload():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        subject_of_email = request.form['subject_of_email']

        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        # Convert file to base64
        base64_data = file_to_base64(file)

        # access Key docusign
        access_token()

        template = create_template(base64_data, subject_of_email) 
        file_path = 'template.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        data.append(template)
        
        file_path = 'template.json'
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
        
        return "success"
        # return envelope
        

@app.route('/template_view')
def template_view():
    file_path = 'template.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    template_list = [json.loads(item) for item in data]
    print(template_list)
    return render_template("template_view.html", template_list = template_list)


@app.route("/send_envelope", methods=['GET','POST'])
def send_envelope():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        template_id = request.form['template_id']
        print(name)
        print(email)
        print(template_id)
        url = "https://demo.docusign.net/restapi//v2.1/accounts/bd182fdb-bda4-40d6-85b5-0a452eaef7e6/envelopes"

        file_path = 'file.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        payload = json.dumps({
        "templateId": f"{template_id}",
        "templateRoles": [
            {
            "email": f"{email}",
            "name": f"{name}",
            "roleName": "Signer"
            }
        ],
        "status": "sent"
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {data['access_token']}"
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text
            
        
    file_path = 'template.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    template_list = [json.loads(item) for item in data]
    return render_template("send_envelope.html", template_list = template_list)

if __name__ == '__main__':
    app.run(debug=True)


