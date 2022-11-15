import tkinter as tk
from PIL import Image, ImageTk
import sys


class TableData():
    def __init__(self,rows,columns):
        # create root window
        self.rows = rows
        self.columns = columns
        self.root = tk.Tk()
        self.root.title('Tabela de retorno para aprendizagem por reforço')

        # code for creating table
        for i in range(self.rows):
            for j in range(self.columns):
                self.e = tk.Entry(self.root, width=20, fg='black', justify ='center',
                               font=('Times New Roman', 16, 'bold'))

                self.e.grid(row=i, column=j)
                self.e.insert(tk.END, lst[i][j])

    def run(self):
        while True:
            self.root.update()


# Python program to create a table



# take the data
lst = [(1, 'Raj', 'Mumbai', 19),
       (2, 'Aaryan', 'Pune', 18),
       (3, 'Vaishnavi', 'Mumbai', 20),
       (4, 'Rachna', 'Mumbai', 21),
       (5, 'Shubham', 'Delhi', 21),
       (5,'bla bla','ddd','fff')]

# find total number of rows and
# columns in list
total_rows = len(lst)
total_columns = len(lst[0])

td = TableData(total_rows,total_columns)

td.run()

