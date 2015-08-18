# What Is It? #
rfc2mobi-next downloads and converts RFCs and Internet Drafts to MOBI eBooks for use with the Amazon Kindle and other e-Readers. The resulting eBooks include a cover and table of contents. When possible, ASCII art figures are converted to inline images. Based on rfc2kindle (http://code.google.com/p/rfc2kindle) by rhuang under the GPLv3 license.

## Why not just use rfc2kindle? ##
At the time of this page's writing:

rfc2kindle does not generate book covers, but rfc2mobi-next does;

rfc2kindle does not escape characters that have special meaning to HTML (e.g. less than, greater than), so kindlegen chokes on rfc2kindle's HTML output if an RFC contains those characters;

rfc2kindle mistakenly converts some text to images, disturbing the flow of text;

and since ASCII art figures included in RFCs are by their nature monochrome, rfc2mobi-next uses PNG instead of rfc2kindle's choice of JPEG for better image quality.

## What can't rfc2mobi-next do (yet)? ##
rfc2mobi-next cannot send the resulting MOBI file to your eReader device automatically. If you're using the command line to use this tool, you probably know how to mount your eReader's flash memory anyway.

rfc2mobi-next doesn't let you use a local file as its source; it will always download the desired RFC on your behalf. This will be changed in a future release.

rfc2mobi-next has difficulty recognizing ordered and unordered lists. The regex to detect lists is simple, but I need to understand the original code better before I can implement it properly. This means that lists are annoyingly rendered as a single line, e.g. "o First item hereo Second item hereo Third item here".

## What else do I need? ##
Requires Amazon's free kindlegen (http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000234621) and the Python Imaging Library (http://www.pythonware.com/library/).

## I found a bug or have a bug fix, how can I help? ##
Please open an issue and include details! Python isn't my primary language and this project is based on someone else's code, so I can use all the help I can get :-)