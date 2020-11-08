TEMP_FOLDER=/tmp/Heeks2
cd ~/PyCAD
git pull
cd CAD/build
make
cp cad.so ../../
cd ~/PyCAD/Step/build
make
cp step.so ../../
cd ~/PyCAD/Geom/build
make
cp geom.so ../../
cd ~/PyCAM
git pull
cd CAM/build
make
cp cam.so ../../

# make zip file
cd ../../../
rm -r $TEMP_FOLDER
rm Heeks2.zip
mkdir $TEMP_FOLDER
mkdir $TEMP_FOLDER/PyCAD
cp PyCAD/*.py $TEMP_FOLDER/PyCAD
cp PyCAD/heekscad.png $TEMP_FOLDER/PyCAD
cp PyCAD/cad.so $TEMP_FOLDER/PyCAD
cp PyCAD/geom.so $TEMP_FOLDER/PyCAD
cp PyCAD/step.so $TEMP_FOLDER/PyCAD
mkdir $TEMP_FOLDER/PyCAD/bitmaps
mkdir $TEMP_FOLDER/PyCAD/bitmaps/angle
mkdir $TEMP_FOLDER/PyCAD/bitmaps/mirror
mkdir $TEMP_FOLDER/PyCAD/icons
cp PyCAD/bitmaps/*.png $TEMP_FOLDER/PyCAD/bitmaps
cp PyCAD/bitmaps/angle/*.png $TEMP_FOLDER/PyCAD/bitmaps/angle
cp PyCAD/bitmaps/mirror/*.png $TEMP_FOLDER/PyCAD/bitmaps/mirror
cp PyCAD/icons/*.png $TEMP_FOLDER/PyCAD/icons

# copy wx - to do only user what is needed
mkdir $TEMP_FOLDER/lib
mkdir $TEMP_FOLDER/lib/wx
echo 'copying wx files'
SITE_PACKAGES=/home/pi/.local/lib/python3.7/site-packages
cp $SITE_PACKAGES/wx/*.py $TEMP_FOLDER/lib/wx
cp $SITE_PACKAGES/wx/*.so $TEMP_FOLDER/lib/wx
cp $SITE_PACKAGES/wx/*.so.4 $TEMP_FOLDER/lib/wx

# copy reportlab
cd PyCAM
python coppy.py $SITE_PACKAGES/reportlab $TEMP_FOLDER/lib/reportlab
cd ../

# copy boost and opencascade libraries
echo 'copy other libraries'
cp /usr/local/lib/*.so.11 $TEMP_FOLDER/lib
cp /usr/local/lib/libboost_python37.so.1.73.0 $TEMP_FOLDER/lib

echo 'copying PyCAM'
mkdir $TEMP_FOLDER/PyCAM
mkdir $TEMP_FOLDER/PyCAM/icons
mkdir $TEMP_FOLDER/PyCAM/bitmaps
mkdir $TEMP_FOLDER/PyCAM/bitmaps/depthop
mkdir $TEMP_FOLDER/PyCAM/bitmaps/drilling
mkdir $TEMP_FOLDER/PyCAM/bitmaps/pattern
mkdir $TEMP_FOLDER/PyCAM/bitmaps/pocket
mkdir $TEMP_FOLDER/PyCAM/bitmaps/profile
mkdir $TEMP_FOLDER/PyCAM/bitmaps/stock
mkdir $TEMP_FOLDER/PyCAM/bitmaps/surface
mkdir $TEMP_FOLDER/PyCAM/bitmaps/tool
mkdir $TEMP_FOLDER/PyCAM/nc
cp PyCAM/*.py $TEMP_FOLDER/PyCAM
cp PyCAM/cam.so $TEMP_FOLDER/PyCAM
cp PyCAM/default.tooltable $TEMP_FOLDER/PyCAM
cp PyCAM/bitmaps/*.png $TEMP_FOLDER/PyCAM/bitmaps
cp PyCAM/bitmaps/depthop/*.png $TEMP_FOLDER/PyCAM/bitmaps/depthop
cp PyCAM/bitmaps/drilling/*.png $TEMP_FOLDER/PyCAM/bitmaps/drilling
cp PyCAM/bitmaps/pattern/*.png $TEMP_FOLDER/PyCAM/bitmaps/pattern
cp PyCAM/bitmaps/pocket/*.png $TEMP_FOLDER/PyCAM/bitmaps/pocket
cp PyCAM/bitmaps/profile/*.png $TEMP_FOLDER/PyCAM/bitmaps/profile
cp PyCAM/bitmaps/stock/*.png $TEMP_FOLDER/PyCAM/bitmaps/stock
cp PyCAM/bitmaps/surface/*.png $TEMP_FOLDER/PyCAM/bitmaps/surface
cp PyCAM/bitmaps/tool/*.png $TEMP_FOLDER/PyCAM/bitmaps/tool
cp PyCAM/icons/*.png $TEMP_FOLDER/PyCAM/icons
cp PyCAM/nc/*.py $TEMP_FOLDER/PyCAM/nc
cp PyCAM/nc/*.xml $TEMP_FOLDER/PyCAM/nc

# make a run file
touch $TEMP_FOLDER/run.sh
chmod u+x $TEMP_FOLDER/run.sh
echo 'export LD_LIBRARY_PATH="../lib"'>>$TEMP_FOLDER/run.sh
echo 'cd PyCAM'>>$TEMP_FOLDER/run.sh
echo 'python3 test.py'>>$TEMP_FOLDER/run.sh
echo 'read -p "press Enter to finish..."'>>$TEMP_FOLDER/run.sh

cd /tmp
echo 'making zip file...'
zip -r -q /home/pi/Heeks2.zip Heeks2
echo 'finished'

