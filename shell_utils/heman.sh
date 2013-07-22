#!/bin/sh
man $@ || (shift $(($#-1)) && $1 --help)
