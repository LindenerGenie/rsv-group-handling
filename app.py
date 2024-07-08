from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import csv
import io
import os

app = Flask(__name__, static_folder='dist')
CORS(app)

users_data = []
column_order = []

@app.route('/upload', methods=['POST'])
def upload_csv():
    global users_data, column_order
    file = request.files['file']
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    column_order = csv_reader.fieldnames
    users_data = list(csv_reader)
    return jsonify({"message": "CSV uploaded successfully"})

@app.route('/users', methods=['GET'])
def get_users():
    search = request.args.get('search', '').lower()
    department = request.args.get('department', '')

    filtered_users = []
    for user in users_data:
        if (search in user['lastname'].lower() or
            search in user['firstname'].lower() or
            search in user['email'].lower() or
            (department and department in user.get('departments', '').split(','))):
            filtered_users.append(user)

    return jsonify(filtered_users)

@app.route('/update-groups', methods=['POST'])
def update_groups():
    data = request.json
    user_ids = data['userIds']
    groups_to_add = data['groupsToAdd']
    groups_to_remove = data['groupsToRemove']

    for user in users_data:
        if f"{user['firstname']}_{user['lastname']}_{user['email']}" in user_ids:
            current_groups = set(user.get('groups', '').split(';')) if user.get('groups') else set()
            current_groups.update(groups_to_add)
            current_groups.difference_update(groups_to_remove)
            user['groups'] = ';'.join(sorted(current_groups))

    return jsonify({"message": "Groups updated successfully"})

@app.route('/export', methods=['GET'])
def export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=column_order)
    writer.writeheader()
    writer.writerows(users_data)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=exported_users.csv'
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/test')
def test():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
