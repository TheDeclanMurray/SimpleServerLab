from os import abort, listdir, path, makedirs, remove
import shutil
import io
import zipfile
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
rootDir = "C:/Users/decla/VSCode/SimpleServerLab/Data" ; print(rootDir)
generalDir = path.abspath("./Data"); print(generalDir)


app.config["UPLOAD_FOLDER"] = rootDir

@app.route("/browse")
def browse():
    print("   [[Browse]]")

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
        errormessage = "Foul Play Detected"
        instructions = "Only attempt to access authorized files"
        return render_template("404error.html",prob=[errormessage,instructions])
    
    if(path.isfile(route)):
        # File
        return send_file(route, as_attachment=True)
    if(path.isdir(route)):
        # Directory
        return render_template("directory.html",dirList=dir,r=r,p=parent)


    errormessage = "File Path not Recognized"
    instructions = "Restate Path"
    return render_template("404error.html",prob=[errormessage,instructions])
    
@app.route("/file", methods=["GET","POST"])
def fileControle():

    if request.method == "GET":
        return getMyFile()
    
    if request.method == "POST":
        return putFile(request)

    # returning a string because this error will be thrown from an
    # improper curl request
    return "Incorrect Request Method"

def getMyFile():
    print("   [[Get File]]")

    # grab the URL encodeed path
    r = request.args.get("p")
    if(r == None):
        r = ""
    
    # get the absolute path
    route = path.abspath(rootDir+r)
    
    # protects against client access local files
    if route[:42] != path.abspath(rootDir):
        errormessage = "Foul Play Detected"
        instructions = "Only attempt to access authorized files"
        return render_template("404error.html",prob=[errormessage,instructions])
    
    if not path.exists(route):
        errormessage = "No File/Foulder Found"
        instructions = "Restate Path"
        return render_template("404error.html",prob=[errormessage,instructions])

    if path.isfile(route):
        # File
        return send_file(route, as_attachment=True)
    
    if path.isdir(route):
        return zipper(route[43:])

    errormessage = "No File/Folder Found"
    instructions = "Restate Path"
    return render_template("404error.html",prob=[errormessage,instructions])

def putFile(req):
    print("   [[Put File]]")
    # print("-->files",req.files)
    # print("-->args ",req.args)
    # print("-->form ",req.form)
    f = name = p = None

    if "file" in req.files:
        f = req.files["file"]

    if "n" in req.form:
        name = req.form["n"]

    if "p" in req.form:
        p = req.form["p"]

    if p == None:
        p = ""
    if name == None:
        p = f.filename

    print(rootDir,p)
    k = path.join(rootDir,p)
    k = path.abspath(k)

    # protects against client access local files
    if k[:42] != path.abspath(rootDir):
        errormessage = "Foul Play Detected"
        instructions = "Only attempt to access authorized files"
        return render_template("404error.html",prob=[errormessage,instructions])

    makedirs(k,exist_ok=True)
    route = path.join(k,secure_filename(name))
    route = path.abspath(route)

    # protects against client access local files
    if route[:42] != path.abspath(rootDir):
        return "Foul Play Detected"


    if path.isfile(route):
        remove(route)
    f.save(route)

    return "Ran"

@app.route("/tester")
def tester():

    prob = ["server Error","Run Again"]

    return render_template("404error.html",prob=prob)


@app.route("/zipper")
def zip():

    p = path.join(rootDir,"home/filer/superSand")
    p = path.abspath(p)
    print("    P",p)
    makedirs(p,exist_ok=True)


    return "help"




def zipper(dataRoute):

    r = path.join(rootDir,dataRoute)
    
    data = shutil.make_archive(
        base_name= "DATA",
        root_dir=r,    
        format="zip"
    )
    
    zp_bytes = io.BytesIO()
    with zipfile.ZipFile("DATA.zip","r") as zp:
        zp_bytes = zp.extractall()
    zp.close()




    remove("./DATA.zip")

    p = dataRoute.split("/")
    name = p[len(p)-1]
    if name == "":
        name = "Data.zip"
    else:
        name = name + ".zip"

    
    
    return send_file(zp_bytes, mimetype="ZIP",as_attachment=True,attachment_filename=name)
    
    

app.run(port=8080) 