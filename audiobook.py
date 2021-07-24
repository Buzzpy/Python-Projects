import pyttsx3
import PyPDF2

book = open('mybook.pdf',' rb') # Add path
pdf_reader = PyPDF2.PdfFileReader(book)
num_pages = pdf_reader.numPages
play = pyttsx3.init()
print('Playing Audio Book')

for num in range(0, num_pages): #iterating through all pages
    page = pdf_reader.getPage(num)
    data = page.extractText()  #extracting text

    play.say(data)
    play.runAndWait()

    # Coded with 💙 by Mr. Unity Buddy
