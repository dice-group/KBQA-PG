from tkinter import *
from tkinter import messagebox

root = Tk()


def toReturnAnswer(question):
    return question


def findTheAnswer():
    questionValue = StringVar()
    if questionEntryValue.get() != "":
        questionValue.set(questionEntryValue.get())
        print("Question ", questionValue.get())
        # Answer
        getAnswer = toReturnAnswer(questionValue.get())
        answerValue.set(getAnswer)
        answer = Label(root, text="Answer is :  " + answerValue.get(), bg='lightblue',
                       font=("Times", 13, "bold")).place(x=300, y=220)
    else:
        messagebox.showerror("Error", "Please enter your question", parent=root)
        answer = Label(root, text="", width="150", bg='lightblue').place(x=300, y=220)


questionEntryValue = StringVar()
answerValue = StringVar()
root.state("zoomed")
root.title("Knowledge Base Question Answering System")
root.configure(bg='lightblue')
root.resizable(False, False)
title = Label(root, text="Question Answering System", bg='lightblue', font=("Impact", 25, "bold")).place(x=430, y=30)

# Question
question = Label(root, text="Enter your question : ", bg='lightblue', font=("Times", 14, "bold")).place(x=300, y=100)

questionEntry = Entry(root, font=("Times", 12), textvariable=questionEntryValue)
questionEntry.place(height="30", width="470", x=490, y=100)
questionEntry.focus()

# Button
Button(text="Find the answer", command=findTheAnswer, bd='1', font=("Times", 13, "bold")).place(x=490, y=160)
print(questionEntry.get())
root.mainloop()
