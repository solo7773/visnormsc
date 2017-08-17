echo "Your working directory is"
echo ""
pwd
echo ""
echo "Beware this is where the program will save temporary data to."

echo -n "When you are ready, press [ENTER] to proceed"
read nouse_var
echo ""

~/anaconda3/bin/python ../ncgui.py
