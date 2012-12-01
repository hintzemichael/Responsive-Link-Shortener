#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
import os
from os import environ
from flask import render_template
from time import gmtime,strftime
from flask import make_response
import json

app = flask.Flask(__name__)
app.debug = True

db = shelve.open("shorten.db")

@app.route('/')
def index():
    """Builds a template based on a GET request, with some default
    arguements"""
    index_title = request.args.get("title", "Link Shortener")
    hello_name = request.args.get("name", "Michael")

    if not request.cookies.get('Cookie_ID'):
        cookie_id = os.urandom(16).encode('hex')
        response = make_response(render_template('index.html'))
        response.set_cookie('Cookie_ID', cookie_id)
        return response

    response_cookies = request.cookies.get('Cookie_ID')
    current_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
    request_user_agent = request.headers.get('User-Agent').split("Gecko) ", 1)
    action = 'page_load'

    f = open("test.json",'a')
    log_data = {}
    log_data['cookie_id'] = response_cookies
    log_data['date'] = current_date
    log_data['browser'] = request_user_agent[1]
    log_data['action'] = action
    data = json.dumps(log_data)
    f.write(data)
    f.write("\n")
    f.close()

    return render_template('index.html')

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
                'png:-']), 200);
    # Comment in to set header below
    resp.headers['Content-Type'] = 'image/png'
    resp.headers['Accept']='*/*'

    return resp

@app.route("/wiki", methods=['PUT', 'POST'])
def install_wiki_redirect():
    wikipedia = request.form.get('url', "http://en.wikipedia.org")
    db['wiki'] = wikipedia
    return "Stored wiki => " + wikipedia

@app.route("/wiki", methods=["GET"])
def redirect_wiki():
    destination = db.get('wiki', '/')
    app.logger.debug("Redirecting to " + destination)
    return redirect(destination)

@app.route("/create", methods=['PUT', 'POST'])
def create():
    long_link = request.form.get('long-link')
    short_link = request.form.get('short-link')
    db[str(short_link)] = long_link

    response_cookies = request.cookies.get('Cookie_ID')
    current_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
    request_user_agent = request.headers.get('User-Agent').split("Gecko) ", 1)
    action = 'save_URL'

    f = open("test.json",'a')
    log_data = {}
    log_data['cookie_id'] = response_cookies
    log_data['date'] = current_date
    log_data['browser'] = request_user_agent[1]
    log_data['action'] = action
    data = json.dumps(log_data)
    f.write(data)
    f.write("\n")
    f.close()

    return flask.render_template(
           'success.html', 
            short=short_link, 
            long=long_link)

@app.route("/<short>", methods=['GET'])
def redirect(short):
    destination = db.get(str(short))
    if (destination is not None):
        response_cookies = request.cookies.get('Cookie_ID')
        current_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        request_user_agent = request.headers.get('User-Agent').split("Gecko) ", 1)
        action = 'redirect'

        f = open("test.json",'a')
        log_data = {}
        log_data['cookie_id'] = response_cookies
        log_data['date'] = current_date
        log_data['browser'] = request_user_agent[1]
        log_data['action'] = action
        log_data['url'] = destination
        data = json.dumps(log_data)
        f.write(data)
        f.write("\n")
        f.close()
        return flask.redirect('http://'+str(destination))
    else: 
        return flask.render_template('page_not_found.html'), 404

@app.route("/<short>", methods=['DELETE'])
def destroy(short):
    raise NotImplementedError


if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))