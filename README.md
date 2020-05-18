# PyCAM
Dan Heeks's experimental CAD/CAM software built on Dan's PyCAD, not to be confused with the more famous PyCAM ( http://pycam.sourceforge.net/ ).
## To build PyCAM ##
First build PyCAD https://github.com/danheeks/PyCAD/blob/master/README.md
### Fetch sources ###
At the same folder level as PyCAD, so that it can do sys.path.append and import all the PyCAD python files.
```
git clone https://github.com/danheeks/PyCAM.git
```

### build CAM python module ###
```
cd PyCAM/CAM
mkdir build
cd build
cmake ..
make
cd ../../
cp CAM/build/cam.so ./
```

