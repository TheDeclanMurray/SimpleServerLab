from os import listdir, path, makedirs, remove
import shutil
import io
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
rootDir = "C:/Users/decla/VSCode/SimpleServerLab/Data"; print(rootDir)
generalDir = path.abspath("./Data"); print(generalDir, len(generalDir))
rootDir = generalDir


app.config["UPLOAD_FOLDER"] = rootDir

@app.route("/browse")
def browse():
    print("   [[Browse]]")

    # grab the URL encodeed path
    r = request.args.get("p")
    if(r == None):
        r = ""
    
    # get the partent of the given path
    parent = ""
    k = r.split("/")
    for a in range(1,len(k)-1):
        parent += "/"+k[a]

    # get the absolute path
    route = path.abspath(rootDir+r)
    
    # list all children in given directory
    if(path.isdir(route)):
        dir = listdir(route)

    # protects against client access local files
    if(route[:len(generalDir)] != path.abspath(rootDir)):
        return tryAgain()
    
    if(path.isfile(route)):
        # File
        return send_file(route, as_attachment=True)
    if(path.isdir(route)):
        # Directory
        return render_template("directory.html",dirList=dir,r=r,p=parent)

    # file/folder not in database
    errormessage = "File Path not Recognized"
    instructions = "Restate Path"
    return render_template("404error.html",prob=[errormessage,instructions])
    
@app.route("/file", methods=["GET","POST"])
def fileControle():

    # GET request
    if request.method == "GET":
        return getMyFile()
    
    # POST request
    if request.method == "POST":
        return putFile(request)

    # returning a string because this error will be thrown from an
    # improper curl request
    return "Incorrect Request Method"

def getMyFile():
    # grab the URL encodeed path
    r = request.args.get("p")
    if(r == None):
        r = ""
    
    # get the absolute path
    route = path.abspath(rootDir+r)
    
    # protects against client access local files
    if route[:len(generalDir)] != path.abspath(rootDir):
        return tryAgain()
    
    # checks to see if the file exits 
    if not path.exists(route):
        return tryAgain()

    if path.isfile(route):
        # File
        return send_file(route, as_attachment=True)
    
    if path.isdir(route):
        # Directory
        return zipper(route[len(generalDir)+1:])

    errormessage = "No File/Folder Found"
    instructions = "Restate Path"
    return render_template("404error.html",prob=[errormessage,instructions])

def putFile(req):

    # start with everything as none
    f = name = p = None

    # get the file to download
    if "file" in req.files:
        f = req.files["file"]

    # get the name of the file
    if "n" in req.form:
        name = req.form["n"]

    # get the path to the dirrectory to save the file under
    if "p" in req.form:
        p = req.form["p"]

    # protect against empty variables
    if p == None:
        p = ""
    if name == None:
        p = f.filename

    # combine root and path
    k = path.join(rootDir,p)
    k = path.abspath(k)

    # protects against client access local files
    if k[:len(generalDir)] != path.abspath(rootDir):
        return tryAgain()

    # make route if it does not yet exist
    makedirs(k,exist_ok=True)
    route = path.join(k,secure_filename(name))
    route = path.abspath(route)

    # protects against client access local files
    if route[:len(generalDir)] != path.abspath(rootDir):
        return tryAgain()

    # overiding file
    if path.isfile(route):
        remove(route)
    f.save(route)

    return "Ran"

@app.route("/tester")
def tester():

    prob = ["server Error","Run Again"]
    return render_template("404error.html",prob=prob)


def zipper(dataRoute):

    # route
    r = path.join(rootDir,dataRoute)
    
    # make a zip file of the route
    shutil.make_archive(
        base_name= "TEMP",
        root_dir=r,    
        format="zip"
    )
    
    # open the zip and copy it into a BytesIO object
    with open("TEMP.zip","rb") as zp:
        zp_bytes = io.BytesIO(zp.read())
    zp.close()

    # delete the saved zip file
    remove("./TEMP.zip")

    # get the name of the file
    p = dataRoute.split("/")
    name = p[len(p)-1]
    if name == "":
        name = "TEMP.zip"
    else:
        name = name + ".zip"

    # return the file
    return send_file(zp_bytes, mimetype="ZIP",as_attachment=True,attachment_filename=name)
    

def tryAgain():
    errormessage = "Foul Play Detected"
    instructions = "Only attempt to access authorized files"
    return render_template("404error.html",prob=[errormessage,instructions])


app.run(port=8080) 