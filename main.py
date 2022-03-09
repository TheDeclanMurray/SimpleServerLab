# from urllib import request
import io
import os
import pathlib
from os import abort, listdir, path
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
rootDir = "C:/Users/decla/VSCode/SimpleServerLab/Data"

@app.route("/browse")
def browse():

    # grab the URL encodeed path
    r = request.args.get("p")
    if(r == None):
        r = ""
    
    parent = ""
    k = r.split("/")
    for a in range(1,len(k)-1):
        parent += "/"+k[a]
    
    # get the absolute path
    route = path.abspath(rootDir+r)
    
    if(path.isdir(route)):
        dir = listdir(route)
    

    # protects against client access local files
    if(route[:42] != path.abspath(rootDir)):
        return "Foul Play Detected"
    
    if(path.isfile(route)):
        # File
        return send_file(route, as_attachment=True)
    if(path.isdir(route)):
        # Directory
        return render_template("directory.html",dirList=dir,r=r,p=parent)
    return "we Failed"
    
@app.route("/file", methods=["GET","POST"])
def fileControle():

    if request.method == "GET":
        return getMyFile()
    
    if request.method == "POST":
        return putFile()

    return "Incorrect Request Method"

def getMyFile():
    # grab the URL encodeed path
    r = request.args.get("p")
    if(r == None):
        r = ""
    
    # get the absolute path
    route = path.abspath(rootDir+r)
    
    # protects against client access local files
    if route[:42] != path.abspath(rootDir):
        return "Foul Play Detected"
    
    if not path.exists(route) :
        return "No File Detected"

    if path.isfile(route):
        # File
        return send_file(route, as_attachment=True)
    
    if path.isdir(route):


        pass

    return "No File Detected"

def putFile():



    return 

@app.route("/zipper")
def zipper():
    


    baser = path.abspath("./Data")
    baser = pathlib.Path(baser)
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode="w") as zp:
        for root,dirs,files in os.walk(baser):
            pass
            # zp.write(i)
    data.seek(0)
    return send_file(data, mimetype="zip", as_attachment=True, attachment_filename="DATA.zip")
    

app.run(port=8080) 