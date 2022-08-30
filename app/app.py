from flask import Flask, request, flash, redirect, url_for, send_from_directory
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

# import json

# import csv
# import itertools
# import re
# from time import sleep
import sys
sys.path.append("C:\Python38\Lib\site-packages")

from os.path import join, dirname, realpath



#-------------------------------------------------------------------------------------------register hops app as middleware
app = Flask(__name__)
hops = hs.Hops(app)
# hops: hs.HopsFlask = hs.Hops(app)

#-------------------------------------------------------------------------------------------Global vars
#attempt to fix file upload: https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
# UPLOAD_FOLDER = '/path/to/the/uploads'
UPLOAD_FOLDER = 'C:/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/help",  methods=['GET', 'POST'])
def help():
    return "Welcome to Grashopper Hops for CPython!"

@app.route('/upload', methods= ['GET', 'POST'])
# def upload_file(fileLocation, filename):
def upload_file():
    # file = {'files': open(filLocation, 'rb')}
    file = request.files['file']
    # file.save('/Users/djangod/newTest.txt')
    # print ('filLocation', fileLocation)
    # file = request.files[filLocation]
 
    # filename = secure_filename(file.filename) # revise this because this is important for security
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'testing'))
    file.save(app.config['UPLOAD_FOLDER'])
    # return redirect(url_for('download_file', name=filename))
    # return redirect(url_for('download_file', name='testing'))

# def callFile(fileLocation):
#     url = "http://127.0.0.1:5000/upload"
#     files = {'files': open(fileLocation, 'rb')}
#     r = requests.post(url, files=files)

def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    

@hops.component(
    "/pdfering",
    name="pdfering",
    description="cook, conversationalist, adds links to pdf",
    icon="./img/belt.png",
    inputs=[
        hs.HopsBoolean("run", "R", "run the component"),
        hs.HopsString("pdfFolder", "pdf", "pdf location "),
        hs.HopsString("pdfNamer", "name", "pdfn ame to link with details"),
        hs.HopsString("details", "D", "details list to link"),
        hs.HopsString("ignorDetails", "iD", "details to ignore"),
    ],
    outputs=[
        hs.HopsString("oFile", "of", "output file path for pdf"),
    ]
)

def pdfering(run,  pdfFolder, pdfNamer, details, ignorDetails):
    print ('pdfFolder', pdfFolder , '\n', 'pdfNamer', pdfNamer, '\n', 'details', details, '\n', 'ignorDetails', ignorDetails)
    # pdfFolder.replace("\\","/")
    # print ('pdfFolder', pdfFolder)
    if(run):
        # print (details, details, pdfFolder, pdfNamer, ignorDetails),
        # msg = pdfLinker(app,  pdfFolder, pdfNamer, details, ignorDetails),
        msg = pdfLinker( pdfFolder, pdfNamer, details, ignorDetails),
        
        # return ['ran', details, details, pdfFolder, pdfNamer]
        return msg
    else:
        return 'waiting'



def pdfLinker( pdfLinkFolder, pdfName, SearchText, excludeListInput ):
    
    # pdfLink = pdfLinkFolder + pdfName + '.pdf'
    UPLOADS_PATH = join(dirname(realpath(__file__)))
    print ('UPLOADS_PATH', UPLOADS_PATH)
    # for f in os.listdir(pdfLinkFolder):
        # print(f)

    pdfLink = os.path.join('join(dirname(realpath', pdfLinkFolder, pdfName + '.pdf') #strange issue with '\' being added to files path
    print ('pdfLinkFolder', pdfLink)
    # pdfLink = pdfLinkFolder + '/' + pdfName + '.pdf' #strange issue with '\' being added to files path
    app.config['UPLOAD_FOLDER'] = pdfLink
    file_ids = ''
    headers={'Username': 'abc@gmail.com', 'apikey':'123-456'}

    f = open(pdfLink, 'rb')
    files = {"file": (pdfLink, f)}
    # resp = requests.post("http://127.0.0.1:5000/upload", files=files, headers=headers )
    resp = requests.post("https://pdf-linking.herokuapp.com/upload", files=files, headers=headers )
    print (resp.text)

    # pdfLinkFolder = sys.argv[1]
    # pdfName = sys.argv[2]
    
    procName = pdfName + '.pdf'
    # ------- using fitz to read the text and search through to find items
    # ------- PDFwriter to writ stuff
    # callFile(pdfLink)
    # upload_file(pdfLink, pdfName)

    urlpdfLink = app.config['UPLOAD_FOLDER']
    # urlpdfLink = app.config['UPLOAD_FOLDER']+ '//' + procName
    ### READ IN PDF
    print (urlpdfLink)
    doc = fitz.open(urlpdfLink)
    # doc = fitz.open(pdfLink)



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
    doc.ez_save(pdfLink[:-4] + '_Belted.pdf')
    # download_file(pdfLink[:-4] + '_Belted.pdf')

    
    return 'processed'





if __name__ == "__main__":
    app.run(debug=True)