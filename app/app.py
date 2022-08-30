from msilib.schema import Directory
from flask import Flask, request, flash, redirect, url_for, send_from_directory, send_file, render_template
import ghhops_server as hs

#Description
#Belt - cook, conversationlist, and keeps my pants up

# Resources
# https://pythonhosted.org/PyPDF2/PdfFileWriter.html
# https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/pdf_reference_archives/PDFReference.pdf

# cloud function taking arguments: https://codelabs.developers.google.com/codelabs/cloud-functions-python-http#3

# Pip install specific versions of multiple packages:
#pip install -r myproject/requirements.txt

import fitz #need to install
from spellchecker import SpellChecker #need to install
from os import path, getcwd
import os
import requests
import webbrowser

# import json

# import csv
# import itertools
# import re
# from time import sleep
import sys
sys.path.append("C:\Python38\Lib\site-packages")

from os.path import join, dirname, realpath



#-------------------------------------------------------------------------------------------register hops app as middleware
app = Flask(__name__, template_folder='templates')
hops = hs.Hops(app)
# hops: hs.HopsFlask = hs.Hops(app)

#-------------------------------------------------------------------------------------------Global vars
#attempt to fix file upload: https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
# UPLOAD_FOLDER = '/path/to/the/uploads'
# UPLOAD_FOLDER = './uploads' #'C:\Users\nbarnes\Documents\GitHub\pdf-linking\app\app.py'
UPLOAD_FOLDER = 'uploads' #'C:\Users\nbarnes\Documents\GitHub\pdf-linking\app\app.py'
# UPLOADS_PATH = join(dirname(realpath(__file__)), UPLOAD_FOLDER)
UPLOADS_PATH = join(app.root_path, UPLOAD_FOLDER)
# UPLOADS_PATH = os.path.abspath('uploads')
# UPLOADS_PATH = join(os.path.abspath(__file__), UPLOAD_FOLDER)
# UPLOADS_PATH = './uploads'

print ('UPLOADS_PATH', UPLOADS_PATH, os.path.abspath('uploads'), app.root_path, )

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH
app.config['DOWNLOAD_FILE'] = UPLOADS_PATH
app.config['param_textToSeach'] = ''
app.config['param_textToExlude'] = ''

filePath = 'I will fix this....'

global textToSeach
global textToExclude

@app.route("/help",  methods=['GET', 'POST'])
def help():
    return "Welcome to Grashopper Hops for CPython!"

@app.route('/vars', methods= ['GET', 'POST'])
def defineUpVars():
    if request.method == 'POST':
      
        filePath =  request.headers['prefile']
        filename = request.headers['name']
        
        textToSeach = request.headers['SearchText']

        #webbrowser.open('http://127.0.0.1:5000/upload', new=2) #dev
        # webbrowser.open('https://pdf-linking.herokuapp.com/upload', new=2)

        # return textToSeach, textToExclude

    return 'none'

@app.route('/upload', methods= ['GET', 'POST'])
# def upload_file(fileLocation, filename):
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        print ('file', file, filename)

    
        # filename = secure_filename(file.filename) # revise this because this is important for security
        print ('os.path.join(app.config[], filename)', os.path.join(app.config['UPLOAD_FOLDER']))

        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #perhaps heroku wants only folder
        file.save(app.config['UPLOAD_FOLDER'])
        print('file saved')
        app.config['UPLOAD_FILE'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print('UPLOAD_FILE updated')
        processPdf()
        print('processpdf')
        # return 'complete'
        app.config['DOWNLOAD_FILE'] = os.path.join(app.config['UPLOAD_FOLDER'],filename[:-4] + '_Belted.pdf')
        return redirect('/file-downloads/')

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
      <h1>{}</h1>
    </form>
    '''.format(filePath)


       


# def callFile(fileLocation):
#     url = "http://127.0.0.1:5000/upload"
#     files = {'files': open(fileLocation, 'rb')}
#     r = requests.post(url, files=files)

# Download API
@app.route("/file-downloads/", methods = ['GET'])
def download_file():
    return render_template('download.html')
    # return render_template('download.html',value=filename)

# @app.route('/uploads/<path:filename>')
@app.route('/uploads/')
# def return_files_tut(filename):
def return_files_tut():
    print ('send_from_directory', app.config["UPLOAD_FOLDER"])
    folderpath = os.path.join(app.config["UPLOAD_FOLDER"])
    name = app.config['DOWNLOAD_FILE']
    print('folderpath', folderpath, name)
    return send_file(name, as_attachment=True)
    
def uploadWindow():
    return''



@hops.component(
    "/kiko",
    name="kiko",
    description="cook, conversationalist, adds links to pdf",
    icon="./img/kiko.png",
    inputs=[
        hs.HopsBoolean("run", "R", "run the component"),
        hs.HopsString("pdfFolder", "pdf", "pdf location "),
        hs.HopsString("pdfNamer", "name", "pdfn ame to link with details"),
        hs.HopsString("details", "D", "details list to link"),
        # hs.HopsString("ignorDetails", "iD", "details to ignore"),
    ],
    outputs=[
        hs.HopsString("oFile", "of", "output file path for pdf"),
    ]
)

# def kiko(run,  pdfFolder, pdfNamer, details, ignorDetails):
def kiko(run,  pdfFolder, pdfNamer, details):
    print ('pdfFolder', pdfFolder , '\n', 'pdfNamer', pdfNamer, '\n', 'details', details, '\n')
    # pdfFolder.replace("\\","/")
    # print ('pdfFolder', pdfFolder)
    if(run):
        msg = pdfLinker( pdfFolder, pdfNamer, details),
        
        # return ['ran', details, details, pdfFolder, pdfNamer]
        return msg
    else:
        return 'waiting'


# def pdfLinker( pdfLinkFolder, pdfName, SearchText, excludeListInput ):
def pdfLinker( pdfLinkFolder, pdfName, SearchText ):
    
    # textToSeach = SearchText
    # textToExclude = excludeListInput

    app.config['param_textToSeach'] = SearchText
    app.config['param_textToExlude'] = 'excludeListInput'


    pdfLink = pdfLinkFolder + '/' + pdfName + '.pdf' #strange issue with '\' being added to files path

    # f = open(pdfLink, 'rb')
    prefiles = {"prefile": pdfLink}
    header = {"name": pdfName, "prefile": pdfLink, 'SearchText': SearchText}
    # requests.post("http://127.0.0.1:5000/vars", files=prefiles, headers=header) #dev
    # requests.post("https://pdf-linking.herokuapp.com/vars", files=prefiles, headers=header)
    
    

    

def processPdf():
    # ----------------commenting below to isolate upload--------------------------------------------------------
    urlpdfLink = app.config['UPLOAD_FILE']
    print ('processPdf Path', UPLOADS_PATH, os.path.abspath('uploads'))

    # for each in os.listdir('/app/app/uploads/'):
    #     print(each)

    # urlpdfLink = app.config['UPLOAD_FOLDER']+ '//' + procName
    ### READ IN PDF
    print ('urlpdfLink', urlpdfLink)
    doc = fitz.open(urlpdfLink)
    # doc = fitz.Document(urlpdfLink)
    print ('fitz open')
    # doc = fitz.open(pdfLink)
    SearchText = app.config['param_textToSeach']
    excludeListInput = app.config['param_textToExlude']



    # SearchText = ['XC-001','XC-A101','XC-D101', 'XC-A201', 'XC-A501','XC-A502','XC-A503','XC-A504','XC-A505','XC-A506', 'XC-D501', 'XC-D502']
    # SearchText = sys.argv[3]
    #------clean sys args--------------------
    SearchText = SearchText.replace("'", '')
    SearchText = SearchText.replace(" ", '')
    SearchText = SearchText.split(",")
    # print (SearchText)

    # excludeListInput = sys.argv[4]
    #------clean sys args--------------------
    excludeListInput = excludeListInput.replace("'", '')
    excludeListInput = excludeListInput.replace(" ", '')
    excludeListInput = excludeListInput.split(",")
    # print (excludeListInput)


    excludeList = ['www.azahner.com', 'WWW.AZAHNER.COM', 'PURLIN', 'ZAHNER', 'AS-BUILT', 'ZEPP', 'Z-CLIP', 'TYP.','TYP', 'JAMBS', 'KERFED', 'SHEATHED', 'SHEATHING', 'HARDSCAPE', 'LAKEFLATO', '24X36"', 'DG04'] + excludeListInput
    callouts = []
    detailsNotFound = []

    ########
    def misspelledWords ():
        textList = page.get_text('text').split('\n')

    def foundDetail (page, searchTxt):
        
        # find each word in the detail list and get its rect. 
        # need to exlude detail pages
        rect = []
        width = page.rect.width - 300
        height = page.rect.height - 200
        
        wlist = page.get_text("words")  # make the word list
        for w in wlist:  # scan through all words on page
            if searchTxt in w[4]:  # w[4] is the word's string
                if (w[0] < width and w[1] < height):
                    # print ('found')
                    r = fitz.Rect(w[:4])  # make rect from word bbox
                    rect.append(r)
                    # print (w)
                    # page.add_underline_annot(r)  # underline

        
        
        return page.number, rect


    def getDetailPage(page, searchTxt):
        # print ('found page')
        # print ('found detail on page')
        # find page that detail links to on it
        # assume lower right hand corner only
        # only one page per many detail
        width = page.rect.width - 300
        height = page.rect.height - 200
        rect = []
        pageNumber = -1

        wlist = page.get_text("words")  # make the word list
        for w in wlist:  # scan through all words on page
            if searchTxt in w[4]:  # w[4] is the word's string
                if (w[0] > width and w[1] > height):
                    # print ('found page')
                    # print (width, height, page.number )
                    # r = fitz.Rect(w[:4])  # make rect from word bbox
                    pageNumber = page.number
                    # rect.append(r)
                    # page.add_underline_annot(r)  # underline

        return pageNumber



    def addLinkstoDetail():
        print ('links added')

    def notFound():
        print ('details not found')



    # def writeCsv(pathToFile, missing, missingName, header, data):
    #     # open the file in the write mode
    #     with open(pathToFile, 'w', encoding='UTF8', newline='') as f:
    #         # create the csv writer
    #         writer = csv.writer(f)

    #         writer.writerow(missing)
    #         writer.writerow(missingName)
    #         # write the header
    #         writer.writerow(header)

    #         # write multiple rows
    #         writer.writerows(data)
    #         # for d in data:
    #         #     writer.writerow(d)


    ## -----------------------end functions -----------------------
    detpageNumber= -1
    detailRect = []
    pages = []
    detialsFound = []
    detailLinkOkj = {}



    for detailName in SearchText:
        detailLinkOkj[detailName] = {'toPages':[], 'destPage':[]}
        # detailLinkOkj[detailName]['pages'] = []
        
    # print ('no idea', detailLinkOkj)
    for page in doc:
        # print('-----------page', page)
        
        for detailName in SearchText:
            
            # detpageNumber = getDetailPage(page, "XC-D501")
            detpageNumber = getDetailPage(page, detailName)
            
            if (detpageNumber != -1):
                # pages.append(detpageNumber)
                detailLinkOkj[detailName]['toPages'].append(detpageNumber)

            # [pgNum, detailRect ]= foundDetail(page, "XC-D501")
            [pgNum, detailRect ]= foundDetail(page, detailName)

            if(len(detailRect)>0):
                # detials.append({pgNum: detailRect})
                detialsFound.append(detailName)
                detailLinkOkj[detailName]['destPage'].append({pgNum: detailRect})
        
    #check if all detiails not found
    for detailName in SearchText:
        
        if (detailName not in detialsFound): #find any detials not located. 
            # print(detailName)
            detailsNotFound.append(detailName)


    # print ('no idea', detailLinkOkj)
    # print ( 'page report', pages, detials)
    #----add links to pages

    for eachDetailObj in detailLinkOkj:
        # print('eachDetailObj', eachDetailObj)
        # print('detailLinkOkj[eachDetailObj][pages]', detailLinkOkj[eachDetailObj]['pages'])
        for eachDestPage in detailLinkOkj[eachDetailObj]['toPages']:
            # print ('each', eachDestPage)
            for eachRect in detailLinkOkj[eachDetailObj]['destPage']:
                # print('eachRect',eachRect)
                # testKey = [k for k, v in each.items()]
                detailPage = list(eachRect.keys())[0]
                detailRect = list(eachRect.values())[0]
                # print('detailPage',detailRect)

                # if (detailPage != pages[0]):
                # print('detailRect', detailRect)
                lnks = doc[detailPage].links()
                # print('links', lnks)

                for everyRect in detailRect:
                    pageToLink = doc[detailPage]
                    # print('pageToLink', pageToLink)
                    # print ('about to link', eachDestPage, detailPage, everyRect)

                    # lnks = {'kind': 1, 'xref': 864, 'from': everyRect, 'type': 'goto', 'page': pages[0], 'to': fitz.Point(100.0, 200.0), 'zoom': 0.0}
                    lnks = {'kind': 1, 'xref': 864, 'from': everyRect, 'type': 'goto', 'page': eachDestPage, 'to': fitz.Point(100.0, 200.0), 'zoom': 0.0}
                    pageToLink.insert_link(lnks)
                    page = doc.reload_page(pageToLink)
            


    
    # doc.ez_save(pdfLinkFolder + pdfName + '_Belted.pdf')
    # doc.ez_save(pdfLink[:-4] + '_Belted.pdf')
    pdfed = urlpdfLink[:-4] + '_Belted.pdf'
    pdfedFile = urlpdfLink.split('\\')[-1]#[:-4] + '_Belted.pdf'
    doc.ez_save(pdfed)
    # download_file(pdfLink[:-4] + '_Belted.pdf')
    #------end comment
    headers={'fileName': pdfed}
    
    # download_file(pdfed)
    # requests.post("http://127.0.0.1:5000/uploads", headers=headers)
    print ('pdfedFile', pdfedFile)
    # webbrowser.open('http://127.0.0.1:5000/uploads/{}'.format(pdfedFile[:-4] + '_Belted.pdf'), new=2)


    return 'processed'



if __name__ == "__main__":
    app.run(debug=True)