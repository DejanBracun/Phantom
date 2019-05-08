// Brisi.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "pch.h"
#include <windows.h>
#include <iostream>

typedef int(__stdcall *f_funci)();

int main()
{

	HINSTANCE hGetProcIDDLL = LoadLibrary("C:\\Users\\Dejan\\Source\\Repos\\Phantom\\Phantom\\Debug\\CLib.dll");

	if (!hGetProcIDDLL) {
		std::cout << "could not load the dynamic library" << std::endl;
		return EXIT_FAILURE;
	}

	// resolve function address here
	f_funci funci = (f_funci)GetProcAddress(hGetProcIDDLL, "vrni");
	if (!funci) {
		std::cout << "could not locate the function" << std::endl;
		return EXIT_FAILURE;
	}

	std::cout << "funci() returned " << funci() << std::endl;


	system("pause");

	return EXIT_SUCCESS;
}


// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
