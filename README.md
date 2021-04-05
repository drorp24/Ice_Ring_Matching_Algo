# rafazonscale

Large-scale Drone Delivery Planning System 

## Development environment setup
1. Install python 3.8 
2. Install Latest Pycharm IDE and open it.
3. Open project directory.
4. Create Virtual Environment:  
Go to File | Settings | Project: rafazonscale | Python Interpreter. Click the Configure project interpreter icon and select Add.  
https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html
4. Go to Terminal tab and run: python setup.py install 
5. Install Cartopy:  
   Instructions: https://scitools.org.uk/cartopy/docs/latest/installing.html#installing  
   Windows:  
   Download "Cartopy-0.18.0-cp38-cp38-win_amd64.whl" from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#cartopy  
   Run: pip install Cartopy-0.18.0-cp38-cp38-win_amd64.whl
6. Run tests:   
   Right click on any tests directory and choose "Run 'Unittests in tests'".  
   **Make sure that the working directory in the test configuration is the project's root directory.**
