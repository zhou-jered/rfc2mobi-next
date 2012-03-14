import re, string
from cStringIO import StringIO
from image import createImage, createCoverFromImage

'''
Created on May 31, 2011
@author: rhuang
'''

class Html():
    input = None
    ouput = None
    toc = []
    rfcElms = ['Info', 'Title', 'Abstract', 'Toc', 'Content']
    rfc = ''
    title = ''
    leftIndent = 0
    textBlock = None
    imageCount = 1
    prevLine = ''
    hasContent=False
    def __init__(self, rfc, input, output):
        self.input = input
        self.output = output
        self.rfc = rfc.lower()
        self.info = StringIO()

    def writeInfo(self, line):
        if not re.match('^\s*$', line):
            self.info.write(line) 
        elif self.info.tell():
            return getattr(self, "writeTitle")
        return getattr(self, "writeInfo")
    
    def writeTitle(self, line):
        if re.match('^\S.*$', line):
            self.output.write('''
<html>
<head>
<title>%s</title>
<link rel="stylesheet" href="../css/rfc.css" type="text/css" />
<meta name="cover" content="%s/cover.png" />
<meta name="Author" content="rfc2kindle" />
</head>
<body>''' % (self.rfc.upper()+" - "+self.title, self.rfc))
            createImage(self.info.getvalue(), '%s/auths.png' % (self.rfc))
            createCoverFromImage('%s/auths.png' % (self.rfc), '%s/cover.png' % (self.rfc))

            self.output.write('<img src="auths.png" />')
            self.output.write("<h1>%s</h1>" % (self.title))
            return self.writeAbstract(line)

        if line.lstrip().rstrip():
            self.title = self.title and (self.title + ' ' + line.lstrip().rstrip()) or line.lstrip().rstrip()
          
        return getattr(self, "writeTitle")

    def writeAbstract(self, line):
	line=sanitizeSpecChars(line)
        if isRFCPageBreaker(line):
            return getattr(self, "writeAbstract")
        
        if re.match(r'table of contents', line.lstrip().rstrip().lower()):
            self.output.write("<mbp:pagebreak/>")
            self.output.write('<p><a name="TOC"><h3>%s</h3></a></p>' % (line))
            return getattr(self, "writeTOC")
        
        if re.match(r'^\S.*', line):
            self.output.write('<h2>%s</h2>' % (line))
        else:
            if self.leftIndent == 0: 
                m = re.match(r'^(\s+)\S.*', line)
                if m: 
                    self.leftIndent = len(m.group(1))
#            if isListItem(line):
#                print "nailed it: %s" % (line)
#                #return getattr(self, "writeTextBlock")
#                self.writeContent(line) # WHAT AM I DOING WRONG HERE!?!??!?!?!!
            else:
                self.output.write(line)
        
        return getattr(self, "writeAbstract")
    
    # Some RFCs lack a TOC
    def writeTOC(self, line):
	line=sanitizeSpecChars(line)
        if isRFCPageBreaker(line) or re.match('^\s*$', line):
            return getattr(self, "writeTOC")
        
        if re.match(r'^\S.*', line) and not re.search(r'\.{3}', line):
            self.output.write("<mbp:pagebreak/>\n")
            self.hasContent=True
            return self.writeContent(line)
        
        m = re.match(r'^\s+([\d.]+)(\s+)([^.]+?)\.+?.*', line)
        if m:
            self.toc.append((m.group(1), m.group(3)))
            lnk = m.group(1)[-1] == '.' and m.group(1)[:-1] or m.group(1)
            self.output.write('<a href="#%s">' % (lnk))
            self.output.write(m.group(1))
            for s in m.group(2):
                self.output.write('&nbsp;')
                
            self.output.write('%s</a><br />\n' % (m.group(3)))
        
        return getattr(self, "writeTOC")
        
    def writeContent(self, line):
	line=sanitizeSpecChars(line)

        if isRFCPageBreaker(line):
            return getattr(self, "writeContent")

        if re.match(r'^\d+\.?\s.*', line):
            m=re.match(r'^(\d+)\.?\s.*', line)
            self.output.write('\n<a name="%s"><h2>%s</h2></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+)\.?\s.*', line)
            self.output.write('\n<a name="%s"><h3>%s</h3></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.\d+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+\.\d+)\.?\s.*', line)
            self.output.write('\n<a name="%s"><h4>%s</h4></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.\d+[\d.]+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+\.\d+[\d.]+)\.?\s.*', line)
            lnk = m.group(1)[-1] == '.' and m.group(1)[:-1] or m.group(1)
            self.output.write('\n<a name="%s"><h5>%s</h5></a>\n<p>\n' %( lnk, line))
        elif re.match(r'^\s*$', line):
            return getattr(self, "newLine")
        elif self.isTextBlockStart(line):
            # detect special lines.
            # special lines require strict line break. figure is one of them.
            self.textBlock = StringIO()
            self.output.write("</p>")
            return self.writeTextBlock(line)
        else:      
            self.output.write(line)
        
        return getattr(self, "writeContent")

    def newLine(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "pageBreakNewLine")
        
        if not re.match(r'^\s*$', line):
            if re.match(r'^\s*\S.*', line):
                self.output.write("</p>\n<p>\n")
                return self.writeContent(line)
            else:
                return self.writeContent(line)
            
        return getattr(self, "newLine")
    
    def pageBreakNewLine(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "pageBreakNewLine")
        
        if not re.match(r'^\s*$', line):
            if re.match(r'^\s*[A-Z0-9].*', line):
                self.output.write("</p>\n<p>\n")
                return self.writeContent(line)
            else:
                return self.writeContent(line)
            
        return getattr(self, "pageBreakNewLine")

    def outputTextBlock(self):
	outputlines = self.textBlock.getvalue().splitlines()[:-1]
	if isImageOutput(outputlines):
	    createImage(self.textBlock.getvalue(), "%s/img%d.png" % (self.rfc, self.imageCount))
	    self.output.write('<img src="img%d.png" />' % (self.imageCount))
	    self.imageCount = self.imageCount + 1
	else:
	    self.output.write("<blockquote> \n")
	    for i in outputlines:
		i=sanitizeSpecChars(i)
		# Remove 2+ initial spaces since we're using blockquote
		i=re.sub(r'^\s\s+','',i)
		# Reduce 3+ consecutive spaces to 2 spaces;
		i=re.sub(r'\s\s\s+','  ',i)
		self.output.write("%s<br/>" %(i))
	    self.output.write("</blockquote> \n")

	self.textBlock.close()
	self.textBlock = None
	self.output.write("<p>\n")

    def writeTextBlock(self, line):
        # rqhuang.... bug here.
        if isRFCPageBreaker(line):
            self.outputTextBlock()
            return getattr(self, "writeContent")

        if re.match(r'^\s+Figure\s.*', line):
            self.textBlock.write(line)
            createImage(self.textBlock.getvalue(), "%s/img%d.png" % (self.rfc, self.imageCount))
            self.output.write('<img src="img%d.png" />' % (self.imageCount))
            self.imageCount = self.imageCount + 1
            self.textBlock.close()
            self.textBlock = None
            self.output.write("<p>\n")
            return getattr(self, "writeContent")
        
        if self.isTextBlockBlockEnd(line):
            self.outputTextBlock()
            return self.writeContent(line)
            
        self.textBlock.write(line)
        return getattr(self, "writeTextBlock")

    def isTextBlockStart(self, line):
        # previous line always empty
        if self.prevLine.lstrip().rstrip():
            return False

        return isTextBlockLine(line, self.leftIndent)
    
    def isTextBlockBlockEnd(self, line):
        return not isTextBlockLine(line, self.leftIndent) and not self.prevLine.lstrip().rstrip()

    def createHTML(self):
        lineProcessor = getattr(self, "write"+self.rfcElms[0])
        for line in self.input:
            lineProcessor = lineProcessor(line)
            self.prevLine = line
        self.output.write("</body></html>")

def isRFCPageBreaker(line):
    # Line ends with [Page \d+] or takes form "RFCblabla1xxx" or "RFCblabla2xxx" or has form feed
    return re.match(r'.*\[Page.*\d+?\]', line) or re.match(r'^RFC.*[1-2]\d\d\d', line) or re.match(r'\s*\f\s*', line)

def isFigureLine(line):
    # If line is an ordered/unordered list, then no
    if isListItem(line):
        return False
    if string.count(line, '---') > 0:
        return True
    if string.count(line, '|') > 1:
	return True
    if string.count(line, '+') > 1:
        return True
    if string.count(line, '>') > 3:
        return True
    if string.count(line, '<') > 3:
        return True

    return False

def isTextBlockLine(line, leftIndent):
    m = re.match(r'^(\s*)\S.*$', line)
    bigindent = m and len(m.group(1)) > leftIndent
    # this is how I detected a text block. It may not be always correct.
    return re.match(r'^\s*$', line) or bigindent or len(' '.join(line.split())) < len(line.rstrip().lstrip()) - 3 or isFigureLine(line)

def isImageOutput(lines):
    if len(lines) > 50:
    # maximum lines allow for image.
        return False

    for i in lines:
        if isFigureLine(i):
            return True

    return False

def sanitizeSpecChars(line):
    # Sanitize &, <, and >
    line=re.sub('&','&amp;',line)
    line=re.sub('<','&lt;',line)
    line=re.sub('>','&gt;',line)
    return line

def isListItem(line):
    # Unordered and ordered lists
    return re.match(r'^\s+(\d+\.|o|\*)\s+\S', line)

