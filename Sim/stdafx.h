

#ifdef WIN32
#include "windows.h"
#endif

extern "C" {
#include <GL/gl.h>
#include <GL/glu.h>
}

#include "geometry.h"
#include "Point.h"
#include "Box.h"
#include "tinyxml.h"
#include "IPoint.h"

extern std::wstring sim_dir;
#include "App.h"
extern CApp* theApp;