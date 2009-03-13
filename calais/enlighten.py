#!/usr/bin/python
"""
An opencalais processor

filefetcher.py [-f|--file <path to text content to be processed] [-h|--help]

Jonah Bossewitch, http://alchemicalmusings.org

"""

import sys
import getopt
import os
from StringIO import StringIO
from urllib import urlopen, urlencode
from rdfxml import parseRDF

API_URL="http://api.opencalais.com/enlighten/rest/"
LICENSE_ID_TXT = "licenseID.txt"
PARAMS_XML = "params.xml"

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def process_file(filename):
    text = str(open(filename).read())
    # text = sys.stdin.read()
    rdf = enlighten(text)
    simple = rdf2simple(rdf)

    (basename, ext) = os.path.splitext(filename)
    outfilename = basename + '.metadata'
    outfile = open(outfilename, 'w')
    print >> outfile, simple
    outfile.close()
    #print >> sys.stdout, simple



def enlighten(text):
    licenseID = findLicenseID()
    paramsXML = findParamsXML()
    #import pdb; pdb.set_trace()
    data = urlencode({'licenseID':findLicenseID(), 'content':text, 'paramsXML':findParamsXML()}) 
    f = urlopen(API_URL, data) 
    response = f.read()
    #if not "xmlns" in response:
    #    raise RuntimeError, response
    return response

def rdf2simple(rdf):
    class Graph:
        def __init__(self):
            self.statements = []
        def triple(self, s, p, o):
            self.statements.append((s, p, o))
            
    g = Graph()
    parseRDF(rdf, None, g)

    output = StringIO()
    for s, p, o in g.statements:
        if p == "<http://s.opencalais.com/1/pred/language>":
            print >> output, "Language: %s" % (o)

    for s, p, o in g.statements:
        if p == "<http://s.opencalais.com/1/pred/categoryName>":
            print >> output, "Category: %s" % (o)

    print >> output, "Tags: ",
    for s, p, o in g.statements:
        if p == "<http://s.opencalais.com/1/pred/name>":
            print >> output, ", %s" % (o),
    print >> output

    for s, p, o in g.statements:
        if p == "<http://s.opencalais.com/1/pred/exact>":
            print >> output, "%s" % (o)

    return output.getvalue()


def findLicenseID():
    return open(LICENSE_ID_TXT).read().rstrip()

def findParamsXML():
    return open(PARAMS_XML).read().rstrip()


def main(argv=None):
    # import pdb; pdb.set_trace()
    
    if argv == None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "f:h", ["file=", "help"])
        except getopt.error, msg:
            raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    if not opts:
        print __doc__
        return 2
    
    f = None
    arg = None
    for o, a in opts:
        if o == "-f" or o == "--file":
            f = process_file
            arg = a
        elif o == "-h" or o == "--help":
            print __doc__
            return 2
        else:
            return 2
    rc = f(arg)

    return rc
            

if __name__ == "__main__":
    exit(main())



