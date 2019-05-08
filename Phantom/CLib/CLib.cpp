// CLib.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#define LIBDLL extern "C" __declspec(dllexport)

LIBDLL int neki(int st)
{
	return st + 1;
}

LIBDLL int vrni()
{
	return 55;
}