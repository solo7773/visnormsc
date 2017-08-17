echo "Your working directory is"
echo ""
pwd
echo ""
echo "Beware this is where the program will save temporary data to."
echo ""
echo -n "When you are ready, press [ENTER] to proceed."
read nouse_var
echo ""

if ~/anaconda3/bin/python ../ncgui.py; then
    echo ""
    echo "Everything is ok. Quit program."
else
    echo ""
    echo "python cannot be found, please make sure you have installed python correctly and the path to python has been added to the environment variable PATH."
fi
