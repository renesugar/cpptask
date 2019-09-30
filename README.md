# About
cpptask searches through all current files and subfolders for TODO, FIXME,
    and NOTE comments and writes a Python program that writes the tasks
    found to standard output. The resulting program can be modified to 
    change the output format.

# Usage
```
Usage: python3 -B ./cpptask.py [FLAGS]
    --path:       Base path of the project to be scanned (Default: .)
    --root:       Root path of the project to be scanned (Default: /)
    --prefix:     Replace root path with this prefix (Default: /)
    --labels:     Labels that are processed (Default: TODO|FIXME|NOTE)
    --author:     Author whose tasks are processed (Default: all)
    --extensions: File extensions that are read (Default: .c.h.hpp.hxx.cc.cpp.c++.cxx.java.cs)
    --output:     Path to output file (Default: ./output.py)

On Mac OS X, if the regex package cannot be imported after installing
with "pip" then install regex with "easy_install".

chmod ugo+x output.py
./output.py > tasks.txt
```
