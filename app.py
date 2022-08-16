from flask import Flask
import ghhops_server as hs

#Description
#Belt - cook, conversationlist, and keeps my pants up

# Resources
# https://pythonhosted.org/PyPDF2/PdfFileWriter.html
# https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/pdf_reference_archives/PDFReference.pdf

# cloud function taking arguments: https://codelabs.developers.google.com/codelabs/cloud-functions-python-http#3

import fitz #need to install
from spellchecker import SpellChecker #need to install
from os import path
# import json

# import csv
# import itertools
# import re
# from time import sleep
import sys
sys.path.append("C:\Python38\Lib\site-packages")


def pdfLinker(pdfLinkFolder, pdfName, SearchText, excludeListInput ):
    # pdfLinkFolder = sys.argv[1]
    # pdfName = sys.argv[2]
    print (pdfLinkFolder,pdfName)
    pdfLink = pdfLinkFolder + pdfName + '.pdf'

    # ------- using fitz to read the text and search through to find items
    # ------- PDFwriter to writ stuff


    ### READ IN PDF
    doc = fitz.open(pdfLink)



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

    # --- spell check---------------------------------------------------------------

    misspelledList = []
    pageHeader = []

    print("page text")
    # print (doc.metadata)

    for page in doc:
    # page = doc[0]
        ### SEARCH
        print('-----------page', page)
        # print (page.clean_contents())
        pageHeader.append('page num {0}'.format(page.number))
        # textToCheck = page.get_text('text')
        textListClean =[]
        new_string = []
        updateMisspelled = []
        textToIgnore = SearchText + excludeList
        textToIgnoreList = []
        textToIgnoreList2 = []
        searchCharInit = ["$","@","Â","©", "ï","¿","|",  "'",'½', 'ï', '�', '©' ] 

        pageText = page.get_text('text').split('\n')
        cleanedPageText = []
        # print(pageText)
        # print(len(pageText))
        for eachtext in pageText:
        # for eachText in cleanedPageText:
            # print(eachtext)
            #  any("abc" in s for s in some_list):
            if any(s in eachtext for s in searchCharInit):
                # print( eachtext)
                x=1
            else:
                cleanedPageText.append(eachtext)
                


        # for each in textList:
        # for each in textListMultiClean:
        for each in cleanedPageText:
            # print (len(each))
            if (len(each) > 0):
                # print (each)
                splitText = each.split(' ')
                if(len(splitText)>1):
                    for i in splitText:
                        textListClean.append(i)
                else:
                    # print (len(splitText))
                    textListClean.append(splitText[0])

        # print (textListClean)
        for textRemove in textListClean:
        # for textRemove in textList:
            # print(textRemove)

            if (textRemove not in textToIgnore):
                # print (textRemove, textToIgnore)
                textToIgnoreList.append(textRemove)

        # print (textToIgnoreList)
        spell = SpellChecker(distance=1)
        misspelled = spell.unknown(textToIgnoreList)
        # misspelledLister = []
        # spezzed = spell.known(textToIgnoreList)
        # for eachword in textToIgnoreList:
        #     if eachword not in spezzed:
        #         misspelledLister.append(eachword)

        # misspelled2 = list(misspelled)
        # print (misspelledLister)

        # something about this is clumsy
        # for stringy in misspelled:
        for stringy in misspelled:
            # cleanstring = ''.join(char for char in stringy if char.isalnum()) #I don't want to remove middle of word hyphnes etc, 
            # print('stringy',stringy)
            searchChar = ["$","@","&","Â","©",",", "ï","¿","|", "(", ")", "'",'½', 'ï'] 
            cleanstring = ''
            if(len(stringy)>1):
                if (not stringy[len(stringy)-1].isalnum()):
                    # print (stringy, stringy[-1:], stringy[:-1])
                    cleanstring = stringy[:-1]
                    # cleanstring = ''.join(char for char in stringy if char.isalnum())
                    # cleanstring = re.sub("[$@&Â©,n22Â©ak]","",stringy)
                elif (not stringy[0].isalnum()):
                    # print(stringy, stringy[1], stringy[1].isalnum(),  stringy[1:])
                    cleanstring = stringy[1:]
                
                else:
                    # print(stringy)
                    cleanstring = stringy

            if (r'/' in stringy):
                # break
                # print('slash', stringy)
                cleanstring = ''
            for eachChar in searchChar:
                if (eachChar in cleanstring):
                    cleanstring = ''
            if(len(cleanstring)>1):

                # print(cleanstring, ''.join(cleanstring.split('-')))
                try:
                    if (int(''.join(cleanstring.split('-')))):
                        # break
                        # print('is_integer', cleanstring)
                        cleanstring = ''
                except:
                    # print('notstring')
                    x=1
            #remove exceptions 
            if len(cleanstring) > 3:
                # print (cleanstring)
                # new_string.append(''.join(char for char in stringy if char.isalnum()))
                new_string.append(cleanstring)
                # new_string.append(stringy)

        for textRemove2 in new_string:
            if textRemove2.lower() not in textToIgnore:
                textToIgnoreList2.append(textRemove2)

        def myFunc(e):
            return len(e)
        misspelledcleaned = spell.unknown(textToIgnoreList2)
        listToSort = list(misspelledcleaned)
        listToSort.sort(key=myFunc)

        misspelledList.append(listToSort)


    # writeList = list(map(list, itertools.zip_longest(*misspelledList, fillvalue=None)))
    # print('report.csv', pageHeader, writeList)
    # writeCsv(pdfLink[:-4]+'_report.csv', ['detailsNotFound'], detailsNotFound, pageHeader, writeList )
    return 'processed'



# sleep(10)

#-------------------------------------------------------------------------------------------register hops app as middleware
app = Flask(__name__)
hops = hs.Hops(app)

@hops.component(
    "/BELTED",
    name="BELTED",
    description="cook, conversationalist, adds links to pdf",
    icon="pointat.png",
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

def BELTED(run,  pdfFolder, pdfNamer, details, ignorDetails):
    print ('pdfFolder', pdfFolder , '\n', 'pdfNamer', pdfNamer, '\n', 'details', details, '\n', 'ignorDetails', ignorDetails)
    if(run):
        # print (details, details, pdfFolder, pdfNamer, ignorDetails),
        msg = pdfLinker(  pdfFolder, pdfNamer, details, ignorDetails),
        
        # return ['ran', details, details, pdfFolder, pdfNamer]
        return msg
    else:
        return 'waiting'

if __name__ == "__main__":
    app.run()