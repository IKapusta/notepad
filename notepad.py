from tkinter import *

class Location:
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def ispis(self):
        return str(self.row) + " " + str(self.col)

def isLeft(start, end):
    if start.row > end.row or (start.row == end.row and start.col > end.col):
        return -1
    else:
        return 1

class LocationRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def ispis(self):
        self.start.ispis()
        self.end.ispis()


class CursorObserver():
    def updateCursorLocation(self, loc):
        pass

class TextObserver():
    def updateText(self):
        pass

class ClipboardStack:
    def __init__(self):
        self.texts = []
        self.observers = []
    
    def push(self, text):
        self.texts.append(text)
        self.notifyObservers()
    
    def pop(self):
        text = self.texts.pop()
        self.notifyObservers()
        return text
    
    def peek(self):
        return self.texts[-1] if len(self.texts) > 0 else None
    
    def clear(self):
        self.texts.clear()
        self.notifyObservers()
    
    def hasText(self):
        return len(self.texts) > 0
    
    def addObserver(self, observer):
        self.observers.append(observer)
    
    def removeObserver(self, observer):
        self.observers.remove(observer)
    
    def notifyObservers(self):
        for observer in self.observers:
            observer.updateClipboard(self.texts)

class ClipboardObserver:
    def updateClipboard(self):
        pass

class TextEditorModel:
    def __init__(self, text, clipboard):
        self.text = text
        self.lines = text.split("\n")
        self.selectionRange = None
        self.cursorLocation = Location(0, 0)
        self.textObservers = []
        self.cursorObservers = []
        self.clipboard = clipboard
    
    def notifyObservers(self):
        self.lines = self.text.split("\n")
        for observer in self.cursorObservers:
            observer.updateCursorLocation(self.cursorLocation)
        for observer in self.textObservers:
            observer.updateText()

    def addTextObserver(self, observer):
        self.textObservers.append(observer)

    def removeTextObserver(self, observer):
        self.textObservers.remove(observer)
    
    def addCursorObserver(self, observer):
        self.cursorObservers.append(observer)

    def removeCursorObserver(self, observer):
        self.cursorObservers.remove(observer)
    
    def insert(self, c):
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange)
            self.selectionRange = None
            
        row, col = self.cursorLocation.row, self.cursorLocation.col
        index = sum(len(line) + 1 for line in self.lines[:row]) + col
        for character in c:
            if character == '\n':
                
                self.text = self.text[:index] + '\n' + self.text[index:]
                
                self.cursorLocation.row += 1
                self.cursorLocation.col = 0
            else:
                self.text = self.text[:index] + character + self.text[index:]
                self.cursorLocation.col += 1
            self.notifyObservers()

        
    def deleteBefore(self):
        if self.selectionRange is None:
            row, col = self.cursorLocation.row, self.cursorLocation.col
            if col > 0:
                line = self.lines[row]
                self.lines[row] = line[:col-1] + line[col:]
                self.cursorLocation.col -= 1
                self.text = "\n".join(self.lines)
                self.notifyObservers()
        else:
            self.deleteRange(self.selectionRange)

    def deleteAfter(self):
        if self.selectionRange is None:
            row, col = self.cursorLocation.row, self.cursorLocation.col
            line = self.lines[row]
            if col < len(line):
                self.lines[row] = line[:col] + line[col+1:]
                self.text = "\n".join(self.lines)
                self.notifyObservers()
            elif row < len(self.lines) - 1:
                
                self.lines[row] = line + self.lines[row+1]
                self.lines.pop(row+1)
                self.text = "\n".join(self.lines)
                self.notifyObservers()
        else:
            self.deleteRange(self.selectionRange)

    def deleteRange(self, r):
        start_row, start_col = r.start.row, r.start.col
        end_row, end_col = r.end.row, r.end.col
        if start_row == end_row:
            self.lines[start_row] = self.lines[start_row][:start_col] + self.lines[start_row][end_col:]
            self.cursorLocation = Location(start_row, start_col)
        else:
            self.lines[start_row] = self.lines[start_row][:start_col] + self.lines[end_row][end_col:]
            self.lines = self.lines[:start_row+1] + self.lines[end_row+1:]
            self.cursorLocation = Location(start_row, start_col)
        self.selectionRange = None
        self.text = "\n".join(self.lines)
        self.notifyObservers()
    
    def clearSelection(self):
        self.selectionRange = None
        self.notifyObservers()
        
    def getText(self):
        return self.text

    def allLines(self):
        return iter(self.lines)

    def linesRange(self, index1, index2):
        return iter(self.lines[index1:index2])

    def moveCursorLeft(self):
        if self.cursorLocation.col > 0:
            self.cursorLocation.col -= 1
        elif self.cursorLocation.row > 0:
            self.cursorLocation.row -= 1
            self.cursorLocation.col = len(self.lines[self.cursorLocation.row])
            
        self.notifyObservers()

    def moveCursorRight(self):
        if self.cursorLocation.col < len(self.lines[self.cursorLocation.row]):
            self.cursorLocation.col += 1
        elif self.cursorLocation.row < len(self.lines) - 1:
            self.cursorLocation.row += 1
            self.cursorLocation.col = 0
            
        self.notifyObservers()

    def moveCursorUp(self):
        if self.cursorLocation.row > 0:
            self.cursorLocation.row -= 1
            self.cursorLocation.col = min(len(self.lines[self.cursorLocation.row]), self.cursorLocation.col)
            
            self.notifyObservers()

    def moveCursorDown(self):
        if self.cursorLocation.row < len(self.lines) - 1:
            self.cursorLocation.row += 1
            self.cursorLocation.col = min(len(self.lines[self.cursorLocation.row]), self.cursorLocation.col)
            
            self.notifyObservers()

    def setSelectionRange(self, start, end):
        if start.row == end.row and start.col == end.col:
            start.ispis()
            end.ispis()
            print("_____________")
            self.selectionRange.ispis()
            self.selectionRange = None
        else:
            if start.row > end.row or (start.row == end.row and start.col > end.col):
                start, end = end, start
            self.selectionRange = LocationRange(start, end)
        self.notifyObservers()

    def getSelectionRange(self):
        return self.selectionRange
    
    def getSelectedText(self, selectionRange):
        start = selectionRange.start
        end = selectionRange.end
        if start.row == end.row:
            return self.lines[start.row][start.col:end.col]
        else:
            selectedText = []
            selectedText.append(self.lines[start.row][start.col:])
            for i in range(start.row+1, end.row):
                selectedText.append(self.lines[i])
            selectedText.append(self.lines[end.row][:end.col])
            return "\n".join(selectedText)



class TextEditor(Canvas, CursorObserver, TextObserver, ClipboardObserver):
    def __init__(self, master, model):
        super().__init__(master, width=500, height=500)
        self.model = model
        self.stackTop = ""
        self.model.addTextObserver(self)
        self.model.addCursorObserver(self)
        self.model.clipboard.addObserver(self)
        self.bind('<Key>', self.on_key_press)
        self.bind('<Button-1>', self.on_click)

        self.taskbar = Frame(self.master, height=30)
        
        
        self.draw()
        self.focus_set()

    def draw(self):
        self.delete('all')
        self.taskbar.destroy()
        self.taskbar = Frame(self.master, height=30)
        self.taskbar.pack(side=BOTTOM, fill=X)
        self.cursor_location = StringVar()
        self.num_lines = StringVar()
        self.cursor_location.set(self.model.cursorLocation.ispis())
        self.num_lines.set(str(len(self.model.lines)))
        Label(self.taskbar, textvariable=self.cursor_location).pack(side=LEFT)
        Label(self.taskbar, textvariable=self.num_lines).pack(side=RIGHT)


        if self.model.selectionRange is not None:
            start = self.model.selectionRange.start
            end = self.model.selectionRange.end

            if start.row == end.row:
                
                x1 = 10 + start.col * 7
                y1 = 10 + start.row * 20
                x2 = 10 + end.col * 7
                y2 = y1 + 18

                self.create_rectangle(
                    x1, y1, x2, y2,
                    fill="lightblue",
                    stipple="gray50",
                    outline=""
                )

            else:
                for row in range(start.row, end.row + 1):
                    row_y1 = 10 + row * 20
                    row_y2 = row_y1 + 18

                    # If first row
                    if row == start.row:
                        row_x1 = x1 = 10 + start.col * 7
                        row_x2 = 10 + len(self.model.lines[row]) * 7

                    # If last row
                    elif row == end.row:
                        row_x1 = 10
                        row_x2 = x2 = 10 + end.col * 7

                    else:
                        row_x1 = 10
                        row_x2 = 10 + len(self.model.lines[row]) * 7

                    self.create_rectangle(
                        row_x1, row_y1, row_x2, row_y2,
                        fill="lightblue",
                        stipple="gray50",
                        outline=""
                    )

        y = 10
        for line in self.model.allLines():
            x = 10
            for char in line:
                self.create_text(x, y, text=char, anchor=NW)
                x += 7
            y += 20

        cursor_x = 10 + self.model.cursorLocation.col * 7
        cursor_y = 10 + self.model.cursorLocation.row * 20
        self.create_line(cursor_x, cursor_y, cursor_x, cursor_y + 18)

    def updateClipboard(self,texts):
        self.stackTop = texts[-1]

    def updateCursorLocation(self, loc):
        self.draw()
    
    def updateText(self):
        self.draw()

    def on_click(self, event):
        row = (event.y - 10) // 20
        col = (event.x - 10) // 7
        self.model.cursorLocation = Location(row, col)
        self.model.clearSelection()
        self.draw()

    def on_key_press(self, event):
        if event.keysym != "Shift_L":
            print(event.keysym)
        if event.keysym == 'Left':
            currLoc = Location(self.model.cursorLocation.row, self.model.cursorLocation.col)
            self.model.moveCursorLeft()
            if event.state & 0x1:  # Shift key pressed
                print("shiftLeft")
                if self.model.selectionRange == None:
                    print("noneL")
                    self.model.setSelectionRange(self.model.cursorLocation, currLoc)
                else:
                    print("NOTNONEL")
                    if isLeft(self.model.cursorLocation, self.model.selectionRange.start) == 1:
                        self.model.setSelectionRange(self.model.cursorLocation, self.model.selectionRange.end)
                    else:
                        self.model.setSelectionRange(self.model.selectionRange.start, self.model.cursorLocation)      
            else:
                self.model.clearSelection()

        elif event.keysym == 'Right':
            currLoc = Location(self.model.cursorLocation.row, self.model.cursorLocation.col)
            self.model.moveCursorRight()
            if event.state & 0x1:  # Shift key pressed
                if self.model.getSelectionRange() == None:
                    print("noneR")
                    self.model.setSelectionRange(currLoc, self.model.cursorLocation)
                else:
                    print("NOTNONER")
                    if isLeft(self.model.cursorLocation, self.model.selectionRange.start) == 1:
                        self.model.setSelectionRange(self.model.cursorLocation, self.model.selectionRange.end)
                    else:
                        self.model.setSelectionRange(self.model.selectionRange.start, self.model.cursorLocation)
            else:
                self.model.clearSelection()

        elif event.keysym == 'Up':
            currLoc = Location(self.model.cursorLocation.row, self.model.cursorLocation.col)
            self.model.moveCursorUp()
            if event.state & 0x1:  # Shift key pressed
                if self.model.getSelectionRange() == None:
                    print("noneU")
                    self.model.setSelectionRange(self.model.cursorLocation, currLoc)
                else:
                    print("nnotnoneU")
                    if isLeft(self.model.cursorLocation, self.model.selectionRange.start) == 1:
                        self.model.setSelectionRange(self.model.cursorLocation, self.model.selectionRange.end)
                    else:
                        self.model.setSelectionRange(self.model.selectionRange.start, self.model.cursorLocation)
            else:
                self.model.clearSelection()

        elif event.keysym == 'Down':
            currLoc = Location(self.model.cursorLocation.row, self.model.cursorLocation.col)
            self.model.moveCursorDown()
            if event.state & 0x1:  # Shift key pressed
                if self.model.getSelectionRange() == None:
                    print("noned")
                    self.model.setSelectionRange(currLoc, self.model.cursorLocation)
                else:
                    print("notnoned")
                    if isLeft(self.model.cursorLocation, self.model.selectionRange.start) == 1:
                        self.model.setSelectionRange(self.model.cursorLocation, self.model.selectionRange.end)
                    else:
                        self.model.setSelectionRange(self.model.selectionRange.start, self.model.cursorLocation)
            else:
                self.model.clearSelection()

        elif event.keysym == 'BackSpace':
            if self.model.selectionRange is None:
                self.model.deleteBefore()
            else:
                self.model.deleteRange(self.model.selectionRange)

        elif event.keysym == 'Delete':
            if self.model.selectionRange is None:
                self.model.deleteAfter()
            else:
                self.model.deleteRange(self.model.selectionRange)
        elif event.keysym == "Return":
            self.model.insert('\n')
        elif event.keysym == 'c' and event.state & 0x4:
            if self.model.selectionRange != None:
                text = self.model.getSelectedText(self.model.selectionRange)
                self.model.clipboard.push(text)
        elif event.keysym == 'x' and event.state & 0x4:
            if self.model.selectionRange != None:
                text = self.model.getSelectedText(self.model.selectionRange)
                self.model.clipboard.push(text)
                self.model.deleteRange(self.model.selectionRange)
        elif event.keysym == 'v' and event.state & 0x4:
            self.model.insert(self.stackTop)
        elif event.keysym == 'V' and event.state & 0x4 and event.state & 0x1:
            self.model.insert(self.stackTop)
            self.model.clipboard.pop()
        elif event.keysym.isalpha() or event.keysym.isdigit():
            self.model.insert(event.keysym)


        


text = "Ovo je prvi redak.\nOvo je drugi redak.\nOvo je treći redak."
clip = ClipboardStack()
model = TextEditorModel(text, clip)

# Stvaramo primjerak grafičke komponente TextEditor i povezujemo ga s TextEditorModel objektom
root = Tk()
editor = TextEditor(root, model)

# Prikazujemo prozor
editor.pack(fill=BOTH, expand=YES)
root.mainloop()
