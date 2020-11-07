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
rm -r /tmp/Heeks2
rm Heeks2.zip
mkdir /tmp/Heeks2
mkdir /tmp/Heeks2/PyCAD
cp PyCAD/*.py /tmp/Heeks2/PyCAD
cp PyCAD/heekscad.png /tmp/Heeks2/PyCAD
cp PyCAD/cad.so /tmp/Heeks2/PyCAD
cp PyCAD/geom.so /tmp/Heeks2/PyCAD
cp PyCAD/step.so /tmp/Heeks2/PyCAD
mkdir /tmp/Heeks2/PyCAD/bitmaps
mkdir /tmp/Heeks2/PyCAD/bitmaps/angle
mkdir /tmp/Heeks2/PyCAD/bitmaps/mirror
mkdir /tmp/Heeks2/PyCAD/icons
cp PyCAD/bitmaps/*.png /tmp/Heeks2/PyCAD/bitmaps
cp PyCAD/bitmaps/angle/*.png /tmp/Heeks2/PyCAD/bitmaps/angle
cp PyCAD/bitmaps/mirror/*.png /tmp/Heeks2/PyCAD/bitmaps/mirror
cp PyCAD/icons/*.png /tmp/Heeks2/PyCAD/icons
mkdir /tmp/Heeks2/PyCAM
mkdir /tmp/Heeks2/PyCAM/icons
mkdir /tmp/Heeks2/PyCAM/bitmaps
mkdir /tmp/Heeks2/PyCAM/bitmaps/depthop
mkdir /tmp/Heeks2/PyCAM/bitmaps/drilling
mkdir /tmp/Heeks2/PyCAM/bitmaps/pattern
mkdir /tmp/Heeks2/PyCAM/bitmaps/pocket
mkdir /tmp/Heeks2/PyCAM/bitmaps/profile
mkdir /tmp/Heeks2/PyCAM/bitmaps/stock
mkdir /tmp/Heeks2/PyCAM/bitmaps/surface
mkdir /tmp/Heeks2/PyCAM/bitmaps/tool
mkdir /tmp/Heeks2/PyCAM/nc
cp PyCAM/*.py /tmp/Heeks2/PyCAM
cp PyCAM/cam.so /tmp/Heeks2/PyCAM
cp PyCAM/default.tooltable /tmp/Heeks2/PyCAM
cp PyCAM/bitmaps/*.png /tmp/Heeks2/PyCAM/bitmaps
cp PyCAM/bitmaps/depthop/*.png /tmp/Heeks2/PyCAM/bitmaps/depthop
cp PyCAM/bitmaps/drilling/*.png /tmp/Heeks2/PyCAM/bitmaps/drilling
cp PyCAM/bitmaps/pattern/*.png /tmp/Heeks2/PyCAM/bitmaps/pattern
cp PyCAM/bitmaps/pocket/*.png /tmp/Heeks2/PyCAM/bitmaps/pocket
cp PyCAM/bitmaps/profile/*.png /tmp/Heeks2/PyCAM/bitmaps/profile
cp PyCAM/bitmaps/stock/*.png /tmp/Heeks2/PyCAM/bitmaps/stock
cp PyCAM/bitmaps/surface/*.png /tmp/Heeks2/PyCAM/bitmaps/surface
cp PyCAM/bitmaps/*.png /tmp/Heeks2/PyCAM/bitmaps/tool
cp PyCAM/icons/*.png /tmp/Heeks2/PyCAM/icons
cp PyCAM/nc/*.py /tmp/Heeks2/PyCAM/nc
cp PyCAM/nc/*.xml /tmp/Heeks2/PyCAM/nc

# make a run file
touch /tmp/Heeks2/run.sh
chmod u+x /tmp/Heeks2/run.sh
echo 'cd PyCAM'>>/tmp/Heeks2/run.sh
echo 'python3 test.py'>>/tmp/Heeks2/run.sh
echo 'read -p "press Enter to finish..."'>>/tmp/Heeks2/run.sh

cd /tmp
zip -r /home/pi/Heeks2.zip Heeks2

