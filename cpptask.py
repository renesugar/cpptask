import regex
import os
import argparse
import sys

#
# MIT License
#
# https://opensource.org/licenses/MIT
#
# Copyright 2017 Rene Sugar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# Description:
#
# This program searches through all current files and subfolders for
# TODO, FIXME, and NOTE comments and writes a Python program that writes
# the tasks found to standard output. The resulting program can be modified
# to change the output format.
#

#
# References:
#
# https://stackoverflow.com/questions/26385984/recursive-pattern-in-regex
# b(?:m|(?R))*e
#
# https://stackoverflow.com/questions/3469080/match-whitespace-but-not-newlines
# /[^\S\x0a\x0d]/
#
# https://stackoverflow.com/questions/2404010/match-everything-except-for-specified-strings
# [\s\S]
#
# http://www.twiki.org/cgi-bin/view/Blog/BlogEntry201109x3
# How to Use Regular Expressions to Parse Nested Structures
#
# http://www.rexegg.com/regex-disambiguation.html#lookarounds
# Negative lookbehind/lookahead before the match
#

def checkExtension(file, exts):
  name, extension = os.path.splitext(file)
  extension = extension.lstrip(".")
  processFile = 0
  if len(extension) == 0:
    processFile = 0
  elif len(exts) == 0:
    processFile = 1
  elif extension in exts:
    processFile = 1
  else:
    processFile = 0
  return processFile

def checkExclusion(dir, rootPath, excludePaths):
  processDir = 0
  if (dir[0:1] == "."):
    processDir = 0
  elif os.path.join(rootPath,dir) in excludePaths:
    processDir = 0
  else:
    processDir = 1
  return processDir

def filelist(dir, excludePaths, exts):
  allfiles = []
  for path, subdirs, files in os.walk(dir):
    files = [os.path.join(path,x) for x in files if checkExtension(x, exts)]
    # "[:]" alters the list of subdirectories walked by os.walk
    # https://stackoverflow.com/questions/10620737/efficiently-removing-subdirectories-in-dirnames-from-os-walk
    subdirs[:] = [os.path.join(path,x) for x in subdirs if checkExclusion(x, path, excludePaths)]
    allfiles.extend(files)
    for x in subdirs:
      allfiles.extend(filelist(x, excludePaths, exts))
  return allfiles

def main():
  parser = argparse.ArgumentParser(description="cpptask")
  parser.add_argument("--path", help="Base path of the project to be scanned", default=".")
  parser.add_argument("--root", help="Root path of the project to be scanned", default="/")
  parser.add_argument("--prefix", help="Replace root path with this prefix", default="/")
  parser.add_argument("--labels", help="Labels that are processed", default="TODO|FIXME|NOTE")
  parser.add_argument("--author", help="Author whose tasks are processed", default="")
  parser.add_argument("--extensions", help="File extensions that are processed", default=".c.h.hpp.hxx.cc.cpp.c++.cxx.java.cs.txt")
  parser.add_argument("--exclude", nargs='*', help="Paths of folders to exclude", default=[])
  parser.add_argument("--output", help="Path to output file", default="./output.py")

  args = vars(parser.parse_args())

  outputFile = os.path.abspath(os.path.expanduser(args['output']))

  if os.path.isfile(outputFile):
    # Don't overwrite existing files in case the output file has the same name
    # as a project file and the output path is in a project directory.
    print("Error: output file '" + outputFile + "' already exists.")
    sys.exit(1)

  basePath = os.path.abspath(os.path.expanduser(args['path']))

  rootPath = args['root']

  rootPrefix = args['prefix']

  authorFilter = args['author']

  fileExtensions = args['extensions'].lstrip(".").split(".")

  excludePaths = args['exclude']

  # Remove trailing path separator from each exclude path
  excludePaths[:] = [x.rstrip(os.sep) for x in excludePaths]

  files = filelist(basePath, excludePaths, fileExtensions)

  labels = args['labels']

  with open(outputFile, "w") as a:
    a.write("#!/usr/bin/python" + str(os.linesep))
    a.write("# -*- coding: utf-8 -*-" + str(os.linesep))
    a.write(os.linesep)
    a.write("def printTask(type, author, line, file, comment):" + str(os.linesep))
    a.write("  print \"Type: \" + type" + str(os.linesep))
    a.write("  print \"Author: \" + author" + str(os.linesep))
    a.write("  print \"Line: \" + line" + str(os.linesep))
    a.write("  print \"File: \" + file" + str(os.linesep))
    a.write("  print \"\"" + str(os.linesep))
    a.write("  print comment" + str(os.linesep))
    a.write("  print \"\"" + str(os.linesep))
    a.write(os.linesep)
    a.write(os.linesep)
    a.write("def main():" + str(os.linesep))

    # Read each file
    for file in files:
      file_canonical = file.replace(rootPath, rootPrefix, 1)

      a.write(os.linesep)
      a.write("  file = \"" + str(file_canonical) + "\"" + str(os.linesep))
      with open(file, 'r') as f:
        lines = f.readlines()
        data=''.join(lines)

        # Get nested C style comments and blocks of single line C++ comments

        pattern = regex.compile(r'(\/\*((?<!\*)(?!\/\*)\/|[^\/]|(?R))*\*\/)|([^\S\x0a\x0d]*\/\/([\s\S]*?)(?:(\r?\n)|$))*', regex.MULTILINE|regex.DOTALL)

        for m in pattern.finditer(data):
          if m.end() > m.start():
            comment = m.group(0)
            comment_offset = m.start()
            # Get tasks in a comment
            task_pattern = regex.compile(r'(' + labels + ')(\([A-Za-z0-9_]*\))*\:(.*$)', regex.MULTILINE|regex.DOTALL)
            offsets = []
            count   = 0
            for mm in task_pattern.finditer(comment):
              offsets.append(mm.start())
              count = count + 1
            offsets.append(None)
            count = 0
            for offset in offsets:
              if offset != None:
                # Write each task to the output file
                task = comment[offset:offsets[count+1]]
                for mm in task_pattern.finditer(task):
                  type = mm.group(1)
                  author = mm.group(2)
                  if author == None:
                    author = "unknown"
                  else:
                    author = author[1:-1]
                  processAuthor = 0
                  if len(authorFilter) == 0:
                    processAuthor = 1
                  elif author == authorFilter:
                    processAuthor = 1
                  else:
                    processAuthor = 0
                  line = data.count('\n', 0, comment_offset + offset) + 1
                  if processAuthor == 1:
                    a.write(str(os.linesep))
                    a.write("  type = \"" + type + "\"" + str(os.linesep))
                    a.write("  author = \"" + author + "\"" + str(os.linesep))
                    a.write("  line = \"" + str(line) + "\"" + str(os.linesep))
                    a.write("  comment = \"\"\"" + comment[offset:offsets[count+1]])
                    a.write("\"\"\"")
                    a.write(str(os.linesep))
                    a.write("  printTask(type, author, line, file, comment)" + str(os.linesep))
                  count = count + 1
    a.write(str(os.linesep))
    a.write("if __name__ == \"__main__\":" + str(os.linesep))
    a.write("  main()" + str(os.linesep))

if __name__ == "__main__":
  main()

