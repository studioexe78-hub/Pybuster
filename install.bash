#!/bin/bash
pip install requests
chmod +x pybuster.py
cp pybuster.py $PREFIX/bin/pybuster
echo "The tool has been installed! Just type 'pybuster' to run it."
