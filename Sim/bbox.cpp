/*  
 *  Copyright 2010 Anders Wallin (anders.e.e.wallin "at" gmail.com)
 *  Copyright 2015      Kazuyasu Hamada (k-hamada@gifu-u.ac.jp)
 *  
 *  This file is part of OpenCAMlib.
 *
 *  OpenCAMlib is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  OpenCAMlib is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with OpenCAMlib.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "stdafx.h"

#include <cassert>
#include <sstream>
#include <iostream>

#include "bbox.hpp"

//************* axis-aligned Bounding-Box **************/

Bbox::Bbox() {
    minpt = GLVertex(0,0,0);
    maxpt = GLVertex(0,0,0);
    initialized = false;
}
//              minx       maxx        miny       maxy       minz       maxz
Bbox::Bbox(double b1, double b2, double b3, double b4, double b5, double b6) {
	minpt = GLVertex((float)b1, (float)b3, (float)b5);
	maxpt = GLVertex((float)b2, (float)b4, (float)b6);
    initialized = true;
}

void Bbox::clear() {
    initialized = false;
}

bool Bbox::isInside(GLVertex& p) const {
    assert( initialized );
    if (p.x > maxpt.x)
        return false;
    else if (p.x < minpt.x)
        return false;
    else if (p.y > maxpt.y)
        return false;
    else if (p.y < minpt.y)
        return false;
    else if (p.z > maxpt.z)
        return false;
    else if (p.z < minpt.z)
        return false;
    else
        return true;
}

void Bbox::addPoint(const GLVertex &p) {
    if (!initialized) {
        maxpt = p;
        minpt = p;
        initialized = true;
    } else {
        if (p.x > maxpt.x)
            maxpt.x = p.x;
        if (p.x < minpt.x)
            minpt.x = p.x;
        
        if (p.y > maxpt.y)
            maxpt.y = p.y;
        if (p.y < minpt.y)
            minpt.y = p.y;
        
        if (p.z > maxpt.z)
            maxpt.z = p.z;
        if (p.z < minpt.z)
            minpt.z = p.z;
    }
//#ifdef MULTI_AXIS
    armvec = (maxpt - minpt) * 0.5;
    centerpt = minpt + armvec;
//#endif
}

/// does this Bbox overlap with b?
bool Bbox::overlaps(const Bbox& b) const {
#ifdef MULTI_AXIS
	GLVertex centerpt = b.centerpt;
	centerpt = centerpt.rotateAC(this->angle.x , this->angle.z);
	GLVertex maxpt = centerpt + b.armvec;
	GLVertex minpt = centerpt - b.armvec;;
    if  ( (this->maxpt.x < minpt.x) || (this->minpt.x > maxpt.x) )
        return false;
    else if ( (this->maxpt.y < minpt.y) || (this->minpt.y > maxpt.y) )
        return false;
    else if ( (this->maxpt.z < minpt.z) || (this->minpt.z > maxpt.z) )
        return false;
    else
        return true;
#else
    if  ( (this->maxpt.x < b.minpt.x) || (this->minpt.x > b.maxpt.x) )
        return false;
    else if ( (this->maxpt.y < b.minpt.y) || (this->minpt.y > b.maxpt.y) )
        return false;
    else if ( (this->maxpt.z < b.minpt.z) || (this->minpt.z > b.maxpt.z) )
        return false;
    else
        return true;
#endif
}

// return the bounding box values as a vector:
//  0    1    2    3    4    5
// [minx maxx miny maxy minz maxz]
double Bbox::operator[](const unsigned int idx) const{
    switch(idx) {
        case 0:
            return minpt.x;
            break;
        case 1:
            return maxpt.x;
            break;
        case 2:
            return minpt.y;
            break;
        case 3:
            return maxpt.y;
            break;
        case 4:
            return minpt.z;
            break;
        case 5:
            return maxpt.z;
            break;    
        default:
            assert(0);
            break;
    }
    assert(0);
    return -1;
}

std::ostream &operator<<(std::ostream &stream, const Bbox b) {
  stream << " Bbox \n";
  //stream << " min= "<< b.minpt <<"\n";
  //stream << " max= "<< b.maxpt <<"\n";
  return stream;
}

// end of file volume.cpp
