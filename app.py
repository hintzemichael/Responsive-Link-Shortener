#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
from flask import Response
from time import gmtime,strftime
from os import environ
import json


app = flask.Flask(__name__)
app.debug = True



db = shelve.open("shorten.db")

@app.route('/')
def index():
    """Builds a template based on a GET request, with some default
    arguements"""
    index_title = request.args.get("title", "Aijia's URL Shortener")
    hello_name = request.args.get("name", "Aijia")
   
    request_header = request.headers
    request_method = request.method
   
    response= flask.make_response()
    response.headers['Date']=strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

    response.set_cookie(key = "Cookie-ID", value = 1234)
   
    response_cookies = response.headers.get('Set-Cookie')
    response_date = response.headers.get('Date')
    request_user_agent = request.headers.get('User-Agent')
    response_header = response.headers

    file = open("./test.json",'w')
    file.write(json.dumps({'datetime': response_date, 'cookie': response_cookies, 'useragent': request_user_agent, 'action': {'pageload': 'index'}}))
    file.write("\n")
    file.close()

    
    return flask.render_template(
            'index.html',
            title=index_title,
            name=hello_name, requestHeader=request_header,requestMethod=request_method,responseHeader = response_header,responseCookies=response_cookies)


###
# This function is not working properly because the Content-Type is not set.
# Set the correct MIME type to be able to view the image in your browser
##/
@app.route('/image')
def image():
    """Returns a PNG image of madlibs text"""
    relationship = request.args.get("relationship", "friend")
    name = request.args.get("name", "Jim")
    adjective = request.args.get("adjective", "fun")

    resp = flask.make_response(
            check_output(['convert', '-size', '600x400', 'xc:transparent',
                '-font', '/usr/share/fonts/thai-scalable/Waree-BoldOblique.ttf',
                '-fill', 'black', '-pointsize', '32', '-draw',
                "text 10,30 'My %s %s said i253 was %s'" % (relationship, name, adjective),
                'png:-']), 200)
    # Comment in to set header below
    resp.headers['Content-Type'] = 'image/png'
    resp.headers['Accept']='*/*'

    return resp


###
# Below is an example of a shortened URL
# We can set where /wiki redirects to with a PUT or POST command
# and when we GET /wiki it will redirect to the specified Location
##/
@app.route("/wiki", methods=['PUT', 'POST'])
def install_wiki_redirect():
    wikipedia = request.form.get('url', "http://en.wikipedia.org")
    db['wiki'] = wikipedia
    return "Stored wiki => " + wikipedia

@app.route("/wiki", methods=["GET"])
def redirect_wiki():
    destination = db.get('wiki', '/')
    app.logger.debug("Redirecting to " + destination)
    return flask.redirect(destination) #depends on how we validate, the destination can be changed to "http://" + 


###
# Now we'd like to do this generally:
# <short> will match any word and put it into the variable =short= Your task is
# to store the POST information in =db=, and then later redirect a GET request
# for that same word to the URL provided.  If there is no association between a
# =short= word and a URL, then return a 404
##/
@app.route("/create", methods=['PUT', 'POST'])
def create():
    short_path = request.form.get('shorturl')
    long_path = request.form.get('longurl')
    db[str(short_path)] = long_path

    return flask.render_template("redirect.html", longPath=str(long_path), shortPath = str(short_path))    #The long URL:  " + str(long_path) + " has been successfully stored into " +  str(short_path) + "!"

@app.route("/<short>", methods=['GET'])
def redirect(short):

    destination = db.get(str(short))
    if destination != None:
        return flask.redirect(destination)
    else:
        return flask.render_template('404.html', string=str(short))

    

@app.route("/<short>", methods=['DELETE'])
def destroy(short):
    """Remove the association between =short= and it's URL"""
    db.get(str(short)).delete()
    #raise NotImplementedError

if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
