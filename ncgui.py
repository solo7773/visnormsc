import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import font as tkFont
from tkinter import messagebox
import pandas as pd
import numpy as np
from multiprocessing import freeze_support
import time
import os
import sys
import io

class StdRedirector(object):
    """
    Redirect standard output to tkinter text widget
    Credit: https://www.reddit.com/r/learnprogramming/comments/3vq0dm/python_how_can_i_print_text_out_in_the_gui_rather/
    """
    def __init__(self, text_widget):
        self.text_space = text_widget
        self.flush = sys.stdout.flush

    def write(self, string):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert("end", string)
        self.text_space.see("end")
        self.text_space.config(state=tk.DISABLED)

class mainApp():
    """Create GUI application"""
    def setMasterLook(self):
        self.root.title('VisNormSC')
        self.root.geometry('1000x640+30+30')
        self.root.minsize(1000, 640)
        # for resize
        for r in range(5):
            if r == 0:
                self.root.rowconfigure(r, weight=0)
            else:
                self.root.rowconfigure(r, weight=1)
        for c in range(2):
            self.root.columnconfigure(c, weight=1)
        # set default font, 13 pixel
        tkFont.nametofont('TkDefaultFont').configure(size=-13)
        # set panel appearance
        s = ttk.Style()
        ## osx cannot set style under theme aqua
        #if sys.platform == 'darwin':
        s.theme_use('classic')
        s.configure('tb.TFrame', borderwidth=1, relief='raised')
        s.configure('tv.TFrame', background='white')
        s.configure('op.TFrame', background='red')
        # s.configure('res.TFrame', background='blue')
        # s.configure('resNB.TFrame', background='yellow')
        s.configure('log.TFrame', background='#d9d9d9')
        ## notebook style
        s.configure('op.TNotebook', borderwidth=0)
        #s.configure('TNotebook.Tab', borderwidth=0)
        s.configure('res.TNotebook', tabposition='n')
        s.configure('res.TNotebook.Tab', padding='4 2')
        ## toorbar icon
        s.configure('icon.TButton', borderwidth=0, padding='10 0 0 0', highlightthickness=0)
        ## op, condition button
        s.layout("cond.TButton",
                 [("Button.focus", None),  # this removes the focus ring
                  ("Button.background", {
                      "children":
                          # [("Button.button", {
                          #     "children":
                                  [("Button.padding", {
                                      "children":
                                          [("Button.label", {
                                              "sticky": "nswe"
                                          })]
                                  })]
                          # })]
                  })
                  ]
                 )
        s.configure('cond.TButton', background='white', padding='2 0')
        ## op, do analysis button
        s.configure('analysis.TButton', borderwidth=1, relief='raise', padding='4 2', highlightthickness=0)
        # print(s.layout('TButton'))
        # print(s.element_options('Button.button'))

    # functions for function areas

    def makeMenubar(self, master):
        menubar = tk.Menu(master)
        fileMenu = tk.Menu(master, tearoff=0)
        fileMenu.add_command(label='Open', command=self.openFileDialog)
        fileMenu.add_command(label='Save')
        fileMenu.add_separator()
        fileMenu.add_command(label='Quit', command=self.quitApp)
        helpMenu = tk.Menu(master, tearoff=0)
        helpMenu.add_command(label='About VisNormSc')
        helpMenu.add_command(label='User guidance')
        menubar.add_cascade(label='File', menu=fileMenu)
        menubar.add_cascade(label='Help', menu=helpMenu)
        self.root.configure(menu=menubar)

    def makeToolbar(self, master):
        toolbarFrame = ttk.Frame(master, width=1000, height=40, padding='5 1 5 1', style='tb.TFrame') # left top right bottom
        toolbarFrame.grid(row=0, column=0, columnspan=2, sticky='NSEW')
        toolbarFrame.grid_propagate(0)
        imgDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'freeIcons/gif/24x24')
        # open file icon
        self.openIcon = tk.PhotoImage(file=os.path.join(imgDir, '52.gif'))
        openButton = ttk.Button(toolbarFrame, command=self.openFileDialog, compound=tk.LEFT, image=self.openIcon, text='Open', padding='10 0 0 0', style='icon.TButton')
        openButton.grid(row=0, column=0, sticky='WENS')
        # save data icon
        self.saveIcon = tk.PhotoImage(file=os.path.join(imgDir, '22.gif'))
        saveButton = ttk.Button(toolbarFrame, compound=tk.LEFT, image=self.saveIcon, text='Save', style='icon.TButton')
        saveButton.grid(row=0, column=1, sticky='WENS')
        saveButton.state(['disabled'])
        sepLine = ttk.Separator(toolbarFrame, orient=tk.VERTICAL)
        sepLine.grid(row=0, column=2, sticky='NS')
        # exit icon
        self.exitIcon = tk.PhotoImage(file=os.path.join(imgDir, '33.gif'))
        exitButton = ttk.Button(toolbarFrame, command=self.quitApp, compound=tk.LEFT, image=self.exitIcon, text='Quit', style='icon.TButton')
        exitButton.grid(row=0, column=3, sticky='WENS')

    def makeDataView(self, master):
        self.tableViewFrame = ttk.LabelFrame(master, width=500, height=400, padding=2, text='Unnormalized data', labelanchor='n', relief='groove')
        self.tableViewFrame.grid(row=1, column=0, rowspan=3, sticky='NSEW')
        self.tableViewFrame.grid_propagate(0)
        self.tableViewFrame.grid_columnconfigure(0, weight=1)

    def makeOps(self, master):
        opFrame = ttk.Frame(master, width=500, height=200, padding=2)#, style='op.TFrame')
        opFrame.grid(row=4, column=0, rowspan=2, sticky='NSEW')
        opFrame.grid_propagate(0)
        opFrame.columnconfigure(0, weight=1)
        opFrame.rowconfigure(0, weight=1)
        ops = ttk.Notebook(opFrame, padding='4 0', style='op.TNotebook')
        ops.grid(row=0, column=0, sticky='WENS')
        op1 = ttk.Frame(ops)
        op1Text = tk.Text(op1, width=70, height=12, wrap=tk.WORD, highlightbackground='#d9d9d9', bg='#d9d9d9')
        op1Text.grid(row=0, column=0, sticky='WEN')
        op1Text.insert('1.0', 'Quick guidance:\n  1. Use check to check the count-depth relationship of your (un-)normalized data.\n  2. Use normalize to normalize your data.\n  3. From the count-depth figure:\n    (1) If all genes within your un-normalized data have a similar relationship then a global stratagy such as DESeq and TMM can be used to normalize your data;\n    (2) Otherwise you should use this tool to normalize you data;\n    (3) Once well normalized, all genes should show a similar count-depth relationship.')
        op1Text['state'] = 'disabled'
        # check count and depth portal
        opCheck = ttk.Frame(ops)
        ttk.Label(opCheck, text='Check the count-depth relationship of (un-)normalized data').grid(row=0, column=0, columnspan=8)
        ttk.Label(opCheck, text='Data').grid(row=1, column=0, columnspan=2, sticky='wns')
        self.dataFile = tk.StringVar(value='Open data file')
        dataEntry = ttk.Entry(opCheck, textvariable=self.dataFile)
        dataEntry.state(['disabled'])
        dataEntry.grid(row=1, column=2, columnspan=5, sticky='wns')
        ttk.Label(opCheck, text='Normalized data').grid(row=1, column=7, columnspan=3, sticky='ens')
        self.isNormData = tk.IntVar()
        self.checkBtStatus = tk.StringVar(value='No')
        isNormDataCheckBt = ttk.Checkbutton(opCheck, textvariable=self.checkBtStatus, variable=self.isNormData, command=lambda: self.checkBtStatus.set('Yes') if self.isNormData.get() else self.checkBtStatus.set('No'))
        isNormDataCheckBt.grid(row=1, column=10, columnspan=2, sticky='wns')
        ttk.Button(opCheck, text='Conditions', command=self.openConditionFile, cursor='hand2', style='cond.TButton').grid(row=2, column=0, columnspan=2, sticky='wns')
        self.conditionFile = tk.StringVar(value='Click to choose file')
        conditionEntry = ttk.Entry(opCheck, textvariable=self.conditionFile)
        conditionEntry.state(['disabled'])
        conditionEntry.grid(row=2, column=2, columnspan=5, sticky='wns')
        ttk.Label(opCheck, text='Tau').grid(row=2, column=7, columnspan=3, sticky='ens')
        self.tau = tk.StringVar(value='0.5')
        tauEntry = ttk.Entry(opCheck, width=6, textvariable=self.tau)
        tauEntry.grid(row=2, column=10, columnspan=2, sticky='wns')
        ttk.Label(opCheck, text='Filter cell proportion').grid(row=3, column=0, columnspan=5, sticky='wns')
        self.filterCellProportion = tk.StringVar(value='0.1')
        filterCellProportionEntry = ttk.Entry(opCheck, width=6, textvariable=self.filterCellProportion)
        filterCellProportionEntry.grid(row=3, column=5, columnspan=2, sticky='wns')
        ttk.Label(opCheck, text='Filter expression').grid(row=3, column=7, columnspan=3, sticky='ens')
        self.filterExpression = tk.StringVar(value='0')
        filterExpressionEntry = ttk.Entry(opCheck, width=6, textvariable=self.filterExpression)
        filterExpressionEntry.grid(row=3, column=10, columnspan=2, sticky='wns')
        ttk.Label(opCheck, text='No. expression groups').grid(row=4, column=0, columnspan=5, sticky='wns')
        self.numExpressionGroups = tk.StringVar(value='10')
        numExpressionGroupsEntry = ttk.Entry(opCheck, width=6, textvariable=self.numExpressionGroups)
        numExpressionGroupsEntry.grid(row=4, column=5, columnspan=2, sticky='wns')
        ttk.Label(opCheck, text='CPU cores').grid(row=4, column=7, columnspan=3, sticky='ens')
        self.cpuCores = tk.StringVar(value='None')
        cpuCoresEntry = ttk.Entry(opCheck, width='6', textvariable=self.cpuCores)
        cpuCoresEntry.grid(row=4, column=10, columnspan=2, sticky='wns')
        ttk.Button(opCheck, text='Analyze', command=self.doCheckCountDepth, style='analysis.TButton').grid(row=5, column=11)
        # normalization portal
        opNormalize = ttk.Frame(ops)
        ttk.Label(opNormalize, text='Normalize data using quantile regression').grid(row=0, column=0, columnspan=9, sticky='wns')
        ttk.Label(opNormalize, text='Data').grid(row=1, column=0, columnspan=2, sticky='wns')
        normDataEntry = ttk.Entry(opNormalize, textvariable=self.dataFile)
        normDataEntry.state(['disabled'])
        normDataEntry.grid(row=1, column=2, columnspan=5)
        ttk.Label(opNormalize, text='Tau').grid(row=1, column=9, sticky='ens')
        self.normTau = tk.StringVar(value='0.5')
        ttk.Entry(opNormalize, textvariable=self.normTau, width=6).grid(row=1, column=10, columnspan=2)
        ttk.Button(opNormalize, text='Conditions', command=self.openConditionFile, cursor='hand2', style='cond.TButton').grid(row=2, column=0, columnspan=2, sticky='wns')
        normConditionsEntry = ttk.Entry(opNormalize, textvariable=self.conditionFile)
        normConditionsEntry.state(['disabled'])
        normConditionsEntry.grid(row=2, column=2, columnspan=5)
        ttk.Label(opNormalize, text='CPU cores').grid(row=2, column=8, columnspan=2, sticky='ens')
        self.normCpuCores = tk.StringVar(value='None')
        ttk.Entry(opNormalize, textvariable=self.normCpuCores, width=6).grid(row=2, column=10, columnspan=2)
        ttk.Label(opNormalize, text='Save evaluation plots').grid(row=3, column=0, columnspan=3, sticky='wns')
        self.normSavePlots = tk.IntVar()
        self.normCheckBtStatus = tk.StringVar(value='No')
        ttk.Checkbutton(opNormalize, textvariable=self.normCheckBtStatus, variable=self.normSavePlots, command=lambda: self.normCheckBtStatus.set('Yes') if self.normSavePlots.get() else self.normCheckBtStatus.set('No')).grid(row=3, column=3, columnspan=2, sticky='ens')
        ttk.Label(opNormalize, text='Proportion of genes').grid(row=3, column=7, columnspan=3, sticky='ens')
        self.normPropToUse = tk.StringVar(value='0.25')
        ttk.Entry(opNormalize, textvariable=self.normPropToUse, width=6).grid(row=3, column=10, columnspan=2)
        ttk.Label(opNormalize, text='Filter cell number').grid(row=4, column=0, columnspan=3, sticky='wns')
        self.normFilterCellNum = tk.StringVar(value='10')
        ttk.Entry(opNormalize, textvariable=self.normFilterCellNum, width=6).grid(row=4, column=3, columnspan=2)
        ttk.Label(opNormalize, text='Number gene groups (k)').grid(row=4, column=6, columnspan=4, sticky='ens')
        self.normNumGeneGroups = tk.StringVar(value='None')
        ttk.Entry(opNormalize, textvariable=self.normNumGeneGroups, width=6).grid(row=4, column=10, columnspan=2)
        ttk.Label(opNormalize, text='Filter expression').grid(row=5, column=0, columnspan=3, sticky='wns')
        self.normFilterExpression = tk.StringVar(value='0')
        ttk.Entry(opNormalize, textvariable=self.normFilterExpression, width=6).grid(row=5, column=3, columnspan=2)
        ttk.Label(opNormalize, text='Threshold').grid(row=5, column=7, sticky='ens')
        self.normThresh = tk.StringVar(value='0.1')
        ttk.Entry(opNormalize, textvariable=self.normThresh, width=6).grid(row=5, column=8, columnspan=2)
        ttk.Button(opNormalize, text='Normalize', command=self.doNormalization, style='analysis.TButton').grid(row=5, column=11)
        # ttk.Button(opNormalize, text='empty result', command=self.clearResultView).grid(row=6, column=0)
        # ttk.Button(opNormalize, text='fire result1', command=self.fireResultViewStep1).grid(row=6, column=3)
        # ttk.Button(opNormalize, text='fire result2', command=lambda: self.fireResultViewStep2(self.normResData)).grid(row=6, column=5)
        ops.add(op1, text='Quick start')
        ops.add(opCheck, text='Check')
        ops.add(opNormalize, text='Normalize')

    def makeEmptyResultView(self, master):
        # for start up of the GUI app
        self.resFrame = ttk.Frame(master, width=500, height=400, padding=2)#, style='res.TFrame')
        self.resFrame.grid(row=1, column=1, rowspan=3, sticky='NSEW')
        self.resFrame.grid_propagate(0)
        self.resFrame.columnconfigure(0, weight=1)
        self.resFrame.rowconfigure(0, weight=1)
        # result notebook
        results = ttk.Notebook(self.resFrame, style='res.TNotebook')
        results.grid(row=0, column=0, sticky='ewns')
        result1 = ttk.Frame(results)#, style='resNB.TFrame')
        result2 = ttk.Frame(results)
        result3 = ttk.Frame(results)
        # bind notebook tabls
        results.add(result1, text='Normalized data')
        results.add(result2, text='Scale factors')
        results.add(result3, text='Filtered genes')

    def clearResultView(self):
        # destroy all and rebuild notebook widget
        for x in self.resFrame.winfo_children():
            x.destroy()
        self.resFrame.destroy()
        self.makeEmptyResultView(self.root)

    def fireResultViewStep1(self):
        # destroy all children widgets and then recreate
        for x in self.resFrame.winfo_children():
            x.destroy()
        # result notebook
        results = ttk.Notebook(self.resFrame, style='res.TNotebook')
        results.grid(row=0, column=0, sticky='ewns')
        ## 1
        result1 = ttk.Frame(results)#, style='resNB.TFrame')
        self.result1Text = tk.Text(result1, width=50, height=12, state='disabled', font=tkFont.Font(family='Helvetica', size=-12), wrap=tk.NONE)
        self.result1Text.grid(row=0, column=0)
        result1Vscroll = ttk.Scrollbar(result1, orient='vertical', command=self.result1Text.yview)
        result1Vscroll.grid(row=0, column=1, sticky='NS')
        self.result1Text['yscrollcommand'] = result1Vscroll.set
        result1Hscroll = ttk.Scrollbar(result1, orient='horizontal', command=self.result1Text.xview)
        result1Hscroll.grid(row=1, column=0, sticky='EW')
        self.result1Text['xscrollcommand'] = result1Hscroll.set
        ## 2
        result2 = ttk.Frame(results)
        self.result2Text = tk.Text(result2, width=50, height=12, state='disabled', font=tkFont.Font(family='Helvetica', size=-12), wrap=tk.NONE)
        self.result2Text.grid(row=0, column=0)
        result2Vscroll = ttk.Scrollbar(result2, orient='vertical', command=self.result2Text.yview)
        result2Vscroll.grid(row=0, column=1, sticky='NS')
        self.result2Text['yscrollcommand'] = result2Vscroll.set
        result2Hscroll = ttk.Scrollbar(result2, orient='horizontal', command=self.result2Text.xview)
        result2Hscroll.grid(row=1, column=0, sticky='EW')
        self.result2Text['xscrollcommand'] = result2Hscroll.set
        ## 3
        result3 = ttk.Frame(results)
        self.result3Text = tk.Text(result3, width=50, height=12, state='disabled', font=tkFont.Font(family='Helvetica', size=-12), wrap=tk.NONE)
        self.result3Text.grid(row=0, column=0)
        result3Vscroll = ttk.Scrollbar(result3, orient='vertical', command=self.result3Text.yview)
        result3Vscroll.grid(row=0, column=1, sticky='NS')
        self.result3Text['yscrollcommand'] = result3Vscroll.set
        result3Hscroll = ttk.Scrollbar(result3, orient='horizontal', command=self.result3Text.xview)
        result3Hscroll.grid(row=1, column=0, sticky='EW')
        self.result3Text['xscrollcommand'] = result3Hscroll.set
        # bind notebook tabls
        results.add(result1, text='Normalized data')
        results.add(result2, text='Scale factors')
        results.add(result3, text='Filtered genes')
        # fine-tune text area size
        def setNBTextArea(event):
            fHeight = results.winfo_height()
            fWidth = results.winfo_width()
            # height - extra (23 or 2) - text border - text top and bottom space - scrollbar height
            lines = int((fHeight - 23 - 2 - 2 - 1 - 1 - 16) / (12 + 1 + 1))
            columns = int((fWidth - 2 - 2 - 2 - 1 - 1 - 16) / tkFont.Font(family='Helvetica', size=-12).measure('a'))
            self.result1Text.configure(width=columns, height=lines)
            self.result2Text.configure(width=columns, height=lines)
            self.result3Text.configure(width=columns, height=lines)
        results.bind('<Configure>', setNBTextArea)

    def fireResultViewStep2(self, resData):
        # insert data
        ## 1 resData[0]['NormalizedData'], dict, df
        self.result1Text.config(state=tk.NORMAL)
        rowColNames = ' , ' + ', '.join([str(x) for x in resData[0]['NormalizedData'].columns.values.tolist()]) + '\n'
        self.result1Text.insert('end', rowColNames)
        colRowNames = resData[0]['NormalizedData'].index.values.tolist()
        for iii in range(len(resData[0]['NormalizedData'])):
            if iii >= 500:
                break
            rowContent = str(colRowNames[iii]) + ', ' + ', '.join([str(x) for x in resData[0]['NormalizedData'].iloc[iii,:].tolist()]) + '\n'
            self.result1Text.insert('end', rowContent)
        self.result1Text.see("1.0")
        self.result1Text.config(state=tk.DISABLED)
        ## 2 resData[0]['ScaleFactors'], dict, df
        self.result2Text.config(state=tk.NORMAL)
        rowColNames = ' , ' + ', '.join([str(x) for x in resData[0]['ScaleFactors'].columns.values.tolist()]) + '\n'
        self.result2Text.insert('end', rowColNames)
        colRowNames = resData[0]['ScaleFactors'].index.values.tolist()
        for iii in range(len(resData[0]['ScaleFactors'])):
            if iii >= 500:
                break
            rowContent = str(colRowNames[iii]) + ', ' + ', '.join([str(x) for x in resData[0]['ScaleFactors'].iloc[iii,:].tolist()]) + '\n'
            self.result2Text.insert('end', rowContent)
        self.result2Text.see("1.0")
        self.result2Text.config(state=tk.DISABLED)
        ## 3 dict resData[1], df
        self.result3Text.config(state=tk.NORMAL)
        # geneFilteredOutDF = pd.concat([pd.Series(resData[1][x], name=x) for x in resData[1]], axis=1)
        rowColNames = ' , ' + ', '.join([str(x) for x in resData[1].columns.values.tolist()]) + '\n'
        self.result3Text.insert('end', rowColNames)
        for iii in range(len(resData[1])):
            if iii >= 500:
                break
            rowContent = str(iii) + ', ' + ', '.join([str(x) for x in resData[1].iloc[iii,:].tolist()]) + '\n'
            self.result3Text.insert('end', rowContent)
        self.result3Text.see("1.0")
        self.result3Text.config(state=tk.DISABLED)

    def makeInfoBoard(self, master):
        logFrame = ttk.Frame(master, width=500, height=200, padding=2, style='log.TFrame')
        logFrame.grid(row=4, column=1, sticky='NSEW')
        logFrame.grid_propagate(0)
        self.logBoard = tk.Text(logFrame, bg='#e0e0e0', highlightbackground='#e0e0e0', state='disabled', width=79, height=13, wrap=tk.WORD, font=tkFont.Font(family='Helvetica', size=-12))
        self.logBoard.grid(row=0, column=0)
        # fine-tune text area size
        def setTextAreaSize(event):
            fHeight = logFrame.winfo_height()
            fWidth = logFrame.winfo_width()
            # height - frame padding - text border - text top and bottom space - scrollbar height
            lines = int((fHeight - 2 - 2 - 2 - 2 - 1 - 1) / (12 + 1 + 1))
            columns = int((fWidth - 2 - 2 - 2 - 2 - 1 - 1 - 16) / tkFont.Font(family='Helvetica', size=-12).measure('a'))
            self.logBoard.configure(width=columns, height=lines)
        logFrame.bind('<Configure>', setTextAreaSize)
        # redirect stdout here
        # sys.stdout = StdRedirector(logBoard)
        sys.stderr = StdRedirector(self.logBoard)
        # vertical scroll bar
        logVscroll = ttk.Scrollbar(logFrame, orient='vertical', command=self.logBoard.yview)
        logVscroll.grid(row=0, column=1, sticky='NS')
        self.logBoard['yscrollcommand'] = logVscroll.set

    # utilities
    def print2Text(self, *args):
        outStr = ' '.join([str(x) for x in args]) + '\n'
        self.logBoard.config(state=tk.NORMAL)
        self.logBoard.insert("end", outStr)
        self.logBoard.see("end")
        self.logBoard.config(state=tk.DISABLED)

    def quitApp(self):
        self.root.quit()
        self.root.destroy()

    def openFileDialog(self):
        # empty old content
        self.dataFile.set('')
        for x in self.tableViewFrame.winfo_children():
            x.destroy()
        # proceed
        fileIN = filedialog.askopenfilename()
        ## check file selected
        if fileIN:
            self.dataFile.set(fileIN)
            self.showDataText(filename=fileIN)
        else:
            self.dataFile.set('Please open data')

    def showDataText(self, filename=None):
        textArea = tk.Text(self.tableViewFrame, width=79, height=26, state='disabled', wrap=tk.NONE, font=tkFont.Font(family='Helvetica', size=-12))
        textArea.grid(row=0, column=0, sticky='WE')
        # fine-tune text area size
        def setTextAreaSize(event):
            fHeight = self.tableViewFrame.winfo_height()
            fWidth = self.tableViewFrame.winfo_width()
            # height - label height - frame padding - text border - text top and bottom space - scrollbar height
            lines = int((fHeight - 15 - 2 - 2 - 2 - 2 - 1 - 1 - 16) / (12 + 1 + 1))
            columns = int((fWidth - 2 - 2 - 2 - 2 - 1 - 1 - 16) / tkFont.Font(family='Helvetica', size=-12).measure('a'))
            textArea.configure(width=columns, height=lines)
        textArea.bind('<Configure>', setTextAreaSize)
        # scroll bars
        vScroll = ttk.Scrollbar(self.tableViewFrame, orient=tk.VERTICAL, command=textArea.yview)
        vScroll.grid(row=0, column=1, sticky='NS')
        xScroll = ttk.Scrollbar(self.tableViewFrame, orient=tk.HORIZONTAL, command=textArea.xview)
        xScroll.grid(row=1, column=0, sticky='WE')
        textArea.configure(xscrollcommand=xScroll.set, yscrollcommand=vScroll.set)
        # insert data
        textArea.config(state=tk.NORMAL)
        with open(filename, 'r') as dataIN:
            lll = 0
            while lll < 500:
                aLine = dataIN.readline()
                textArea.insert('end', aLine)
                lll += 1
        textArea.see("1.0")
        textArea.config(state=tk.DISABLED)

    def openConditionFile(self):
        # empty entry
        self.conditionFile.set('')
        conditionFileIN = filedialog.askopenfilename()
        if conditionFileIN:
            self.conditionFile.set(conditionFileIN)
        else:
            self.conditionFile.set('Please choose file')

    def doCheckCountDepth(self):
        userToken = messagebox.askokcancel(title='Analyze', message='Are you sure you want to start analyzing?', icon='question', default='cancel')
        if userToken:
            passCheck = True
            # check parameters
            try:
                if os.path.exists(self.dataFile.get()):
                    checkParData = self.dataFile.get()
                else:
                    self.print2Text('Please open the data you need to analyze')
                    passCheck = False
                if self.isNormData.get():
                    checkParNormalizedData = self.dataFile.get()
                else:
                    checkParNormalizedData = None
                if os.path.exists(self.conditionFile.get()):
                    checkParCondition = self.conditionFile.get()
                else:
                    self.print2Text('Please select the condition file')
                    passCheck = False
                if 0 < float(self.tau.get()) < 1:
                    checkParTau = float(self.tau.get())
                else:
                    self.print2Text('Tau shold be > 0 and < 1')
                    passCheck = False
                if 0 <= float(self.filterCellProportion.get()) <= 1:
                    checkParFilterCellProp = float(self.filterCellProportion.get())
                else:
                    self.print2Text('Filter cell proportion should be >= 0 and <= 1')
                checkParFilterExpression = float(self.filterExpression.get())
                if int(self.numExpressionGroups.get()) > 0:
                    checkParNumExpressionGroups = int(self.numExpressionGroups.get())
                else:
                    self.print2Text('Please correctly set the number of gene expression groups')
                    passCheck = False
                if self.cpuCores.get() == 'None':
                    checkParCpu = None
                else:
                    checkParCpu = int(self.cpuCores.get())
                    if checkParCpu <= 0:
                        self.print2Text('CPU cores should be > 0')
                        passCheck = False
            except Exception:
                self.print2Text('Please set parameters correctly!')
                passCheck = False
            # do analysis
            if passCheck:
                from pyNormsc.scnorm import checkCountDepth
                self.print2Text('Following arguments were used:')
                self.print2Text('Data:', checkParData)
                self.print2Text('Normalized data:', checkParNormalizedData)
                self.print2Text('Condition file:', checkParCondition)
                self.print2Text('Tau:', checkParTau)
                self.print2Text('Filter cell proportion:', checkParFilterCellProp)
                self.print2Text('Filter expression:', checkParFilterExpression)
                self.print2Text('Num expression grps:', checkParNumExpressionGroups)
                self.print2Text('nCPU:', checkParCpu)
                ## analyze
                dataIN = pd.read_csv(checkParData, header=0, index_col=0)
                if checkParNormalizedData is not None:
                    checkParNormalizedData = dataIN
                Conditions = pd.read_csv(checkParCondition, header=None).iloc[:, 0].values
                figInstance = checkCountDepth.checkCountDepth(dataIN, checkParNormalizedData, Conditions,
                                                              checkParTau, checkParFilterCellProp,
                                                              checkParFilterExpression,
                                                              checkParNumExpressionGroups, checkParCpu)
                ## make figure window
                figWindow = tk.Toplevel(self.root)
                figWindow.title('Check data')
                canvas = FigureCanvasTkAgg(figInstance, master=figWindow)
                canvas.show()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
                toolbar = NavigationToolbar2TkAgg(canvas, figWindow)
                toolbar.update()
                canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def doNormalization(self):
        userToken = messagebox.askokcancel(title='Normalize', message='Are you sure you want to start normalizing?', icon='question', default='cancel')
        if userToken:
            passCheck = True
            # check parameters
            try:
                if os.path.exists(self.dataFile.get()):
                    normParData = self.dataFile.get()
                else:
                    self.print2Text('Please open the data you need to normalize')
                    passCheck = False
                if 0 < float(self.normTau.get()) < 1:
                    normParTau = float(self.normTau.get())
                else:
                    self.print2Text('Tau shold be > 0 and < 1')
                    passCheck = False
                if os.path.exists(self.conditionFile.get()):
                    normParCondition = self.conditionFile.get()
                else:
                    self.print2Text('Please select the condition file')
                    passCheck = False
                if self.normCpuCores.get() == 'None':
                    normParCPUs = None
                else:
                    normParCPUs = int(self.normCpuCores.get())
                    if normParCPUs <= 0:
                        self.print2Text('CPU cores should be > 0')
                        passCheck = False
                if self.normSavePlots.get():
                    normParSavePlots = True
                else:
                    normParSavePlots = False
                if 0 < float(self.normPropToUse.get()) < 1:
                    normParPropToUse = float(self.normPropToUse.get())
                else:
                    self.print2Text('Proportion of genes should be > 0 and < 1')
                    passCheck = False
                if int(self.normFilterCellNum.get()) > 0:
                    normParFilterCellNum = int(self.normFilterCellNum.get())
                else:
                    self.print2Text('Filter cell number should be > 0')
                    passCheck = False
                if self.normNumGeneGroups.get() == 'None':
                    normPar_K = None
                else:
                    dict_K = self.normNumGeneGroups.get().strip().replace(' ', '')
                    normPar_K = {x.split(':')[0]: int(x.split(':')[1]) for x in dict_K.split(',')}
                    for y in normPar_K.values():
                        if y <= 0:
                            self.print2Text('Number of gene groups should be an integer > 0')
                            passCheck = False
                            break
                normParFilterExpression = float(self.normFilterExpression.get())
                normParThresh = float(self.normThresh.get())
            except Exception:
                self.print2Text('Please set parameters correctly!')
                passCheck = False
            # pass and start normalizing
            if passCheck:
                ## clear previous result
                self.clearResultView()
                ## initialize result view container, in case of event binding error
                self.fireResultViewStep1()
                ## doing
                from pyNormsc.scnorm import SCnorm
                self.print2Text('Following arguments were used:')
                self.print2Text('Data:', normParData)
                self.print2Text('Condition file:', normParCondition)
                self.print2Text('Save plots:', normParSavePlots)
                self.print2Text('Proportion of genes to use:', normParPropToUse)
                self.print2Text('Tau:', normParTau)
                self.print2Text('Filter cell number:', normParFilterCellNum)
                self.print2Text('Num gene groups (K):', normPar_K)
                self.print2Text('nCPU:', normParCPUs)
                self.print2Text('Filter expression', normParFilterExpression)
                self.print2Text('Threshold:', normParThresh)
                ## normalize
                dataIN = pd.read_csv(normParData, header=0, index_col=0)
                Conditions = pd.read_csv(normParCondition, header=None).iloc[:, 0].values
                normResData, normResFig = SCnorm.SCnorm(dataIN, Conditions, normParSavePlots, normParPropToUse,
                                    normParTau, True, normParFilterCellNum,
                                    normPar_K, normParCPUs, normParFilterExpression, normParThresh)
                ## show result data in GUI
                self.fireResultViewStep2(normResData)
                ## make figure window
                figWindow = tk.Toplevel(self.root)
                figWindow.title('Normalization result')
                canvas = FigureCanvasTkAgg(normResFig, master=figWindow)
                canvas.show()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
                toolbar = NavigationToolbar2TkAgg(canvas, figWindow)
                toolbar.update()
                canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def __init__(self, master):
        self.root = master
        self.setMasterLook()
        self.makeMenubar(master)
        self.makeToolbar(master)
        self.makeDataView(master)
        self.makeOps(master)
        self.makeEmptyResultView(master)
        self.makeInfoBoard(master)
        # self.normResData = [{'NormalizedData': pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]}), 'ScaleFactors': pd.DataFrame({'a': [.1, .2, .3], 'b': [.4, .5, .6]})}, {'a': [1, 2], 'b': ['no']}]


if __name__ == '__main__':
    freeze_support()
    root = tk.Tk()
    app = mainApp(root)
    root.mainloop()
