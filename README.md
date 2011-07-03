# Code Bag

I think most developers end up with an assortment of random code -- each piece too small to be a "project" but large enough to want to keep around as an example or something useful.

I'm collecting some of the random scripts or bits of code that I've shared into one repository.

## Organization

I'm using the word pretty loosely.  Things are piled into directories roughly organized the kind of code it is -- either purpose or language.

This README may not inventory all of it.

## Dependencies

This code does not represent a single, coherent project nor is it a polished, documented library.  A given bit of code will depend on whatever was conveniently handy to help get a job done.

## Python

[Python][] is a handy programming language.

### libraries and tools

Some libraries that these scripts may depend on when convenient:

   - [Python Imaging Library][PIL]: Image manipulation supporting lots of image types.  Very handy and also free.  There's a commercial version of this library which has some more features, but I have never used it.
   - [pygame][]: Game development library for Python.  It is built on top of [SDL][].  Most of my use of pygame has been as a very convenient way to show full screen images on Windows.
   - [pyrex][]: A tool for writing C Python extension modules in a Python-like language.
   - [ReportLab][]: Library for creating PDFs.


### Scripts

   - python/rounded-corners -- generate rounded corners for use with CSS to roundify boxes; obsolete with modern browsers using PIL.
   - python/mergeframe -- Merge a framing image with another image using PIL.
   - python/uuids.pyx -- A poor binding of libuuid to Python using Pyrex; written to play with Pyrex.
   - python/imagepdf.py -- Assemble a bunch of images into a PDF using ReportLab (to make the PDF) and Singleshot (to read IPTC tags for captions).

[Python]: http://www.python.org/
[PIL]: http://www.pythonware.com/products/pil/
[pygame]: http://www.pygame.org/
[SDL]: http://www.libsdl.org/
[pyrex]: http://www.cosc.canterbury.ac.nz/~greg/python/Pyrex/
[reportlab]: http://www.reportlab.org/
