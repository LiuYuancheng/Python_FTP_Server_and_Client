import os
import platform
from flask import Flask, render_template_string, send_from_directory, abort

app = Flask(__name__)

dirpath = os.path.dirname(os.path.abspath(__file__))
# The root directory you want to serve
ROOT_DIR = os.path.join(dirpath, 'AgentLogFolder')

slashCar = '\\' if platform.system() == "Windows" else '/'

@app.route('/')
@app.route('/<path:subpath>')
def show_directory(subpath=''):

    subpathList = subpath.split('/')

    current_path = None
    
    # remove the duplicate in the path sub path.
    for i in range(len(subpathList)):
        testSubpath = slashCar.join(subpathList[i:])
        testPath = os.path.join(ROOT_DIR, testSubpath)
        if os.path.exists(testPath):
            current_path = testPath
            subpath = '/'.join(subpathList[i:])
            break

    if current_path is None: abort(404)
    
    if os.path.isdir(current_path):
        # List directory contents
        contents = os.listdir(current_path)
        print(contents)
        directories = [d for d in contents if os.path.isdir(os.path.join(current_path, d))]
        files = [f for f in contents if os.path.isfile(os.path.join(current_path, f))]
        print(files)
        
        return render_template_string(DIRECTORY_TEMPLATE, subpath=subpath, directories=directories, files=files)
    else:
        # Serve a file
        return send_from_directory(ROOT_DIR, subpath)

DIRECTORY_TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Directory Viewer</title>
</head>
<body>
    <h1>Directory listing for: {{ subpath }}</h1>
    <ul>
        {% for directory in directories %}
            <li><a href="{{ subpath }}/{{ directory }}">{{ directory }}/</a></li>
        {% endfor %}
        {% for file in files %}
            <li><a href="{{ subpath }}/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
