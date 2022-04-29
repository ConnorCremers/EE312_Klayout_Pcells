# EE312 Klayout Pcells
Parametric cell macros (Pcells) for Klayout. Used in the Stanford EE312 class. PCells are useful when you want the same general structure but with a few small changes to sizes.

To use, copy EE312.lym into <klayout_folder>/pymacros and all of the .py files into <klayout_folder>/python. To add new macros, create the file with implementation details and add its declaration to EE312.lym.

This repo contains a set of test structures which can be used to determine properties such as sheet resistivity, contact resistivity, alignment and feature size, as well as device structures like capacitors, diodes, and transistors. 
