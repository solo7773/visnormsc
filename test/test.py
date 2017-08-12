import sys
import tkinter as tk
from multiprocessing import Pool


class redirectStd():
    def __init__(self, textWidget):
        self.textBoard = textWidget
        # self.flush = sys.stdout.flush
    def write(self, msg):
        self.textBoard.insert('end', msg)

def f(x):
    print('calculate:', x, '** 2')
    return x ** 2

if __name__ == '__main__':

    root = tk.Tk()
    root.geometry('600x400+30+30')

    textArea = tk.Text(root, bg='gray', width=70, height=20)
    textArea.pack()
    tk.Button(root, text='click me', command=lambda: print('Dont touch\n me!')).pack()

    sys.stdout = redirectStd(textArea)
    sys.stderr = redirectStd(textArea)

    def testParallel():
        p = Pool(5)
        print(p.map(f, [10, 2, 3]))

    tk.Button(root, text='test multiprocessing', command=testParallel).pack()

    root.mainloop()