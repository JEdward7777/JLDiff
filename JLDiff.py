#!/usr/bin/python

#Copyright (c) 2016, Joshua Lansford @ LaserLinc
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement
from collections import defaultdict

import sys
import codecs

try:
    import cgi
except ImportError:
    cgi = None  # so hasattr() won't crash

if hasattr( cgi, "escape" ):
    cgi_escape = cgi.escape
else:
    import html
    cgi_escape = html.escape


STATE_PASSING_1ST = 0
STATE_PASSING_2ND = 1
STATE_MATCH = 2


class lineCompIndex(object):
    __slots__ = ['errorCount', 'previous', 'state', 'content' ]
    def __init__( self ):
        self.errorCount = 0
        self.previous = None
        self.state = STATE_PASSING_1ST
        self.content = ""
    def __str__( self ):
        result = ""
        if self.state == STATE_PASSING_1ST:
            result = "1st"
        elif self.state == STATE_PASSING_2ND:
            result = "2nd"
        elif self.state == STATE_MATCH:
            result = "M"
        result += " e" + str( self.errorCount )
        result += " " + self.content
        return result

    def __repr__(self) -> str:
        return str(self)

u_intern_dict = {}
def u_intern( value ):
    if value in u_intern_dict:
        return u_intern_dict[value]
    u_intern_dict[value]=value
    return value

def compute_diff( file1, file2, talk=True, axis_penalty=False ):
    lastLine = []
    thisLine = []

    #init the root root
    thisIndex = lineCompIndex()
    thisIndex.state = STATE_MATCH
    thisLine.append( thisIndex )

    #init the root top case
    columnIndex = 1
    for char2 in file2:
        thisIndex = lineCompIndex()
        thisIndex.previous = thisLine[ columnIndex-1 ]
        thisIndex.errorCount = thisIndex.previous.errorCount+1
        thisIndex.content = u_intern(char2)
        thisIndex.state = STATE_PASSING_2ND
        thisLine.append( thisIndex )
        columnIndex += 1

    rowIndex = 1
    for char1 in file1:
        lastLine = thisLine
        thisLine = []

        if talk:
            try:
                sys.stdout.write( char1 )
            except Exception:
                pass

        #init the root left case
        thisIndex = lineCompIndex()
        thisIndex.previous = lastLine[ 0 ]
        thisIndex.errorCount = thisIndex.previous.errorCount+1
        thisIndex.content = u_intern(char1)
        thisIndex.state = STATE_PASSING_1ST
        thisLine.append( thisIndex )

        columnIndex = 1
        for char2 in file2:
            thisIndex = lineCompIndex()


            #just assume it will in this direction.
            thisIndex.previous = thisLine[ columnIndex-1 ]
            thisIndex.content = u_intern(char2)
            thisIndex.state = STATE_PASSING_2ND
            thisIndex.errorCount = thisIndex.previous.errorCount+1

            #but if the other direction is better overwrite.
            if lastLine[ columnIndex ].errorCount+1 < thisIndex.errorCount:
                thisIndex.previous = lastLine[ columnIndex ]
                thisIndex.content = u_intern(char1)
                thisIndex.state = STATE_PASSING_1ST
                thisIndex.errorCount = thisIndex.previous.errorCount+1

            #if we have a match we have a third option
            if( char2 == char1 ):
                axis_penalty_amount = abs(columnIndex - rowIndex)*1e-5 if axis_penalty else 0

                if lastLine[ columnIndex-1 ].errorCount+axis_penalty_amount < thisIndex.errorCount:

                    thisIndex.previous = lastLine[ columnIndex-1 ]
                    thisIndex.errorCount = thisIndex.previous.errorCount+axis_penalty_amount

                    thisIndex.state = STATE_MATCH
                    thisIndex.content = u_intern(char2)

            thisLine.append( thisIndex )
            columnIndex += 1
        rowIndex += 1

    backwardsList = []
    currentNode = thisLine[ len( thisLine )-1 ]
    while not currentNode is None:
        backwardsList.append( currentNode )
        currentNode = currentNode.previous

    backwardsList.reverse()
    return backwardsList


def default_classifier( ch ):
    if ch.isalpha():
        return 'alpha'
    elif ch.isspace():
        return 'space'
    else:
        return 'other'

def tokenize( text, classifier=None ):
    """Split text into tokens based on character class transitions.

    Args:
        text: The input string to tokenize.
        classifier: Optional callable (str) -> Any that takes a single character
            and returns a hashable class label. Consecutive characters with the
            same label form one token. When None, uses default_classifier which
            groups alphabetical, whitespace, and other characters.

    Returns:
        A list of strings. Concatenating them reproduces the original text exactly.
    """
    if classifier is None:
        classifier = default_classifier

    if not text:
        return []

    tokens = []
    current_token = text[0]
    current_class = classifier( text[0] )

    for ch in text[1:]:
        ch_class = classifier( ch )
        if ch_class == current_class:
            current_token += ch
        else:
            tokens.append( current_token )
            current_token = ch
            current_class = ch_class

    tokens.append( current_token )
    return tokens


def flatten_diff( diff_nodes ):
    """Generator that expands multi-character content nodes into single-character nodes.

    Single-character and empty nodes pass through unchanged. For multi-character
    nodes (from token-level diffs), yields one lineCompIndex per character,
    preserving the parent node's state.

    Safe to call on any diff output -- for character-level diffs this is a
    transparent passthrough with zero overhead.
    """
    for node in diff_nodes:
        if len( node.content ) <= 1:
            yield node
        else:
            for ch in node.content:
                expanded = lineCompIndex()
                expanded.state = node.state
                expanded.content = ch
                yield expanded


def compute_diff_by_words( file1, file2, talk=True, axis_penalty=False, classifier=None ):
    """Tokenize two strings and compute a token-level diff.

    This is a convenience function that tokenizes both inputs, runs compute_diff
    on the token lists, and returns the token-level diff result (unflattened).
    Each node's content will be a full token string.

    Use flatten_diff() on the result to expand back to character-level nodes
    for use with printDiffs, or inspect the token-level nodes directly for
    word-level analysis.

    Args:
        file1: First input string.
        file2: Second input string.
        talk: If True, print progress to stdout.
        axis_penalty: If True, apply axis penalty in diff algorithm.
        classifier: Optional callable (str) -> Any for tokenization.
            See tokenize() for details.

    Returns:
        A list of lineCompIndex nodes with token-level content.
    """
    tokens1 = tokenize( file1, classifier )
    tokens2 = tokenize( file2, classifier )
    return compute_diff( tokens1, tokens2, talk=talk, axis_penalty=axis_penalty )


def printDiffs( nodesToPrint, outputFile ):
    isblack = True
    isred = False
    isgreen = False

    def escape( inputStr ):
        answer = ""
        if inputStr == " ":
            answer = "&nbsp;"
        elif inputStr == "\t":
            answer = "&nbsp;&nbsp;&nbsp;"
        else:
            answer = cgi_escape( inputStr )
        return answer


    for nodeToPrint in flatten_diff( nodesToPrint ):
        if nodeToPrint.content == "\n":
            outputFile.write( "<br>\n" )
        else:
            if(nodeToPrint.state == STATE_MATCH):
                if not isblack:
                    outputFile.write( "</span>" )
                    isblack = True
                    isred = False
                    isgreen = False
            elif(nodeToPrint.state == STATE_PASSING_2ND ):
                if not isred:
                    if not isblack:
                        outputFile.write( "</span>" )
                    outputFile.write( "<span class='new'>" )
                    isblack = False
                    isred = True
                    isgreen = False
            else:
                if not isgreen:
                    if not isblack:
                        outputFile.write( "</span>" )
                    outputFile.write( "<span class='old'>" )
                    isblack = False
                    isred = False
                    isgreen = True

            outputFile.write( escape( nodeToPrint.content ) )

    if not isblack:
        outputFile.write( "</span>" )
        isblack = True
        isred = False
        isgreen = False

def main( argv ):

    filename1 = None
    filename2 = None
    output =    None
    same_size = False
    word_level = False

    for arg in argv:
        if arg.startswith( "-" ):
            if arg == "--same_size":
                same_size = True
            elif arg == "--word_level":
                word_level = True
            else:
                raise Exception( "Unknown arg " + arg )
        else:
            if not filename1:
                filename1 = arg
            elif not filename2:
                filename2 = arg
            elif not output:
                output = arg
            else:
                raise Exception( "Extra argument " + arg )


    if not filename1 or not filename2 or not output:
        print( "Usage: JLDiff file1 file2 resultFile [--same_size] [--word_level]" )
        exit(1)

    with codecs.open( filename1, 'r', 'utf-8', errors='ignore' ) as fileHandle1:
        with codecs.open( filename2, 'r', 'utf-8', errors='ignore' ) as fileHandle2:
            file1 = fileHandle1.read()
            file2 = fileHandle2.read()

            if word_level:
                result = compute_diff_by_words( file1, file2 )
            else:
                result = compute_diff( file1, file2 )

    with codecs.open( output, 'w', 'utf-8', errors='ignore' ) as outFile:
        outFile.write( "<!DOCTYPE html>\n" )
        outFile.write( "<html>\n" )
        outFile.write( "<head>\n" )
        outFile.write( "<meta charset='utf-8'>\n" )
        outFile.write( "<title>diff of " + cgi_escape( filename1 ) + " and " + cgi_escape( filename2 ) + "</title>\n" )
        outFile.write( "<style>\n" )
        if same_size:
            outFile.write( ".new{color:darkgreen}\n" )
            outFile.write( ".old{color:red}\n" )
        else:
            outFile.write( ".new{color:darkgreen;font-size: 25px;}\n" )
            outFile.write( ".old{color:red;font-size: 25px;}\n" )
        outFile.write( "</style>\n" )
        outFile.write( "</head>\n" )
        outFile.write( "<body>\n" )

        printDiffs( result, outFile )

        outFile.write( "</body>\n" )
        outFile.write( "</html>\n" )


def main_cli():
    main(sys.argv[1:])

if __name__ == "__main__":
    main_cli()
