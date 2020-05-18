/*  
 *  Copyright 2010 Anders Wallin (anders.e.e.wallin "at" gmail.com)
 *  Copyright 2015      Kazuyasu Hamada (k-hamada@gifu-u.ac.jp)
 *  
 *  This file is part of cutsim.
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

#ifndef GLVERTEX_H
#define GLVERTEX_H

#include <cassert>
#include <cmath>

#include <cutsim_def.hpp>

/// a vertex/point in 3D, with (x,y,z) coordinates of type GLfloat
/// normal is (nx,ny,nz)
/// color is (r,g,b)
struct GLVertex {
    /// default (0,0,0) ctor
    GLVertex() : x(0), y(0), z(0), col(0) {}
    /// ctor with given (x,y,z)
    GLVertex(GLfloat x, GLfloat y, GLfloat z) 
         : x(x), y(y), z(z), col(0) {}
    /// ctor with given (x,y,z) and (r,g,b)
	GLVertex(GLfloat x, GLfloat y, GLfloat z, HeeksColor c)
         : x(x), y(y), z(z), col(c) {}
    /// set the vertex color
	void setColor(HeeksColor c) {
		col = c;
    }
    /// set the vertex color
    void setColor(GLfloat red, GLfloat green, GLfloat blue) {
		col = HeeksColor((unsigned char)(red * 255), (unsigned char)(green * 255), (unsigned char)(blue * 255));
    }

	/// string output
	std::string str() { static char s[128]; sprintf(s, "(%f, %f, %f )", x, y, z); return std::string(s); }
    
// DATA
    /// x-coordinate
    GLfloat x;
    /// y-coordinate
    GLfloat y;
    /// z-coordinate
    GLfloat z; 
	HeeksColor col;
    
// Operators etc
    /// return length
    GLfloat norm() const {
        return sqrt( x*x + y*y + z*z );
    }
    /// set length to 1
    void normalize() {
        if (this->norm() != 0.0)
            *this *= (1/this->norm());
    }
    /// multiplication by scalar
    GLVertex& operator*=(const double &a) {
        x *= (float)a;
        y *= (float)a;
        z *= (float)a;
        return *this;
    }
    /// multiplication by scalar
    GLVertex  operator*(const double &a) const {
        return GLVertex(*this) *= a;
    }
    /// vector addition
    GLVertex& operator+=( const GLVertex& p) {
        x += p.x;
        y += p.y;
        z += p.z;
        return *this;
    }
    /// vector addition
    const GLVertex operator+( const GLVertex &p) const {
        return GLVertex(*this) += p;
    }
    /// vector subtraction
    GLVertex& operator-=( const GLVertex& p) {
        x -= p.x;
        y -= p.y;
        z -= p.z;
        return *this;
    }
    /// vector subtraction
    const GLVertex operator-( const GLVertex &p) const {
        return GLVertex(*this) -= p;
    }
    /// cross product
    GLVertex cross(const GLVertex &p) const {
        GLfloat xc = y * p.z - z * p.y;
        GLfloat yc = z * p.x - x * p.z;
        GLfloat zc = x * p.y - y * p.x;
        return GLVertex(xc, yc, zc);
    }
    /// dot product
    GLfloat dot(const GLVertex &p) const {
        return x*p.x + y*p.y + z*p.z;
    }
    /// the closest point on p1-p2 line
    GLVertex closestPoint(const GLVertex &p1, const GLVertex &p2) const {
        GLVertex v = p2 - p1;
        assert( v.norm() > 0.0 );
        double u = (*this - p1).dot(v) / v.dot(v);  // u = (p3-p1) dot v / (v dot v)
        return p1 + v*u;
    }
    /// distance from this vertex to p1-p2 line, in the XY plane (used??)
    GLfloat xyDistanceToLine(const GLVertex &p1, const GLVertex &p2) const {
        // see for example
        // http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
        if ((p1.x == p2.x) && (p1.y == p2.y)) {// no line in xy plane
            std::cout << "point.cpp: xyDistanceToLine ERROR!: can't calculate distance from \n";
            //std::cout << "point.cpp: xyDistanceToLine ERROR!: *this ="<<*this <<" to line through\n";
            //std::cout << "point.cpp: xyDistanceToLine ERROR!: p1="<<p1<<" and \n";
            //std::cout << "point.cpp: xyDistanceToLine ERROR!: p2="<<p2<< "\n";
            //std::cout << "point.cpp: xyDistanceToLine ERROR!: in the xy-plane\n";
            return -1;
        }
        else {
            GLVertex v( p2.y-p1.y, -(p2.x-p1.x), 0 );
            v.normalize();
            GLVertex r(p1.x - x, p1.y - y, 0);
            return fabs( v.dot(r));
        }
    }
    /// rotate vertex by amount alfa around o->v axis 
    void rotate(const GLVertex& origin, const GLVertex& v, GLfloat alfa) {
        // rotate point p by alfa deg/rad around vector o->v
        // p = o + M*(p-o)
        GLfloat M[3][3];
        GLfloat c = cos(alfa);
        GLfloat D = 1.0f - c;
        GLfloat s = sin(alfa);
        M[0][0] = v.x*v.x*D+c; 
        M[0][1] = v.y*v.x*D+v.z*s; 
        M[0][2] = v.z*v.x*D-v.y*s;
        M[1][0] = v.x*v.y*D-v.z*s;
        M[1][1] = v.y*v.y*D+c;
        M[1][2] = v.z*v.y*D+v.x*s;
        M[2][0] = v.x*v.z*D+v.y*s;
        M[2][1] = v.y*v.z*D-v.x*s;
        M[2][2] = v.z*v.z*D+c;
        // matrix multiply
        GLfloat vector[3];
        vector[0] = x - origin.x;
        vector[1] = y - origin.y;
        vector[2] = z - origin.z;
        GLfloat result[3];
        for (int i=0; i < 3; i++) {
            result[i]=0;
            for (int j=0; j < 3; j++) {
                result[i]+=vector[j]*M[i][j];
            }
        }
        x = origin.x + result[0];
        y = origin.y + result[1];
        z = origin.z + result[2];
    }
    /// rotate vertex around A and C axis
    GLVertex rotateAC(const GLfloat a, const GLfloat c) {
        GLfloat M[3][3];
        GLfloat zC = cos(c);
        GLfloat zS = sin(c);
        GLfloat xC = cos(a);
        GLfloat xS = sin(a);
        M[0][0] =  zC;       M[0][1] = -zS;       M[0][2] = 0.0;
        M[1][0] =  zS * xC;  M[1][1] =  zC * xC;  M[1][2] = -xS;
        M[2][0] =  zS * xS;  M[2][1] =  zC * xS;  M[2][2] =  xC;
        // matrix multiply
        GLVertex result;
        result.x = x * M[0][0] + y * M[0][1];
        result.y = x * M[1][0] + y * M[1][1] + z * M[1][2];
        result.z = x * M[2][0] + y * M[2][1] + z * M[2][2];
        return result;
    }
    /// rotate vertex by A and C rotation matrix
    GLVertex rotateAC(const GLfloat M[3][3]) {
        // matrix multiply
        GLVertex result;
        result.x = x * M[0][0] + y * M[0][1];
        result.y = x * M[1][0] + y * M[1][1] + z * M[1][2];
        result.z = x * M[2][0] + y * M[2][1] + z * M[2][2];
        return result;
    }
};

#endif
