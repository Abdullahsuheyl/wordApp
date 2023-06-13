import tkinter as tk
import sqlite3 as sql
from tkinter import messagebox
wordsDb="Words.db"
wrongDb="WrongWords.db"
class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AnaSayfa")
        self.root.geometry("900x400")

        self.addWords_button = tk.Button(self.root, text="Kelime Ekle", font=20, fg="black", command=self.add_words)
        self.addWords_button.place(x=100, y=150)

        self.learnWords_button = tk.Button(self.root, text="Kelime Çalış", font=20, fg="black", command=self.learn_words)
        self.learnWords_button.place(x=250, y=150)

        self.wrongWords_button = tk.Button(self.root, text="Yanlış Kelimelere Çalış", font=20, fg="black", command=self.wrong_words)
        self.wrongWords_button.place(x=400, y=150)

        self.delete_wrongWords_button = tk.Button(self.root, text="Yanlış Kelimeleri Sil", font=20, fg="black", command=self.delete_wrong_words)
        self.delete_wrongWords_button.place(x=650, y=150)

        # Alt pencerelerin varsayılan olarak atanması
        self.addPage = None
        self.learnPage = None
        self.wrongPage = None
        self.deletePage = None

    def run(self):
        self.root.mainloop()

    def add_words(self):
        self.root.withdraw()  # Ana pencereyi gizle
        if not self.addPage:
            self.addPage = tk.Toplevel()
            self.addPage.title("Kelime Ekle")
            self.addPage.geometry("900x400")
        
            # Türkçe Kelime için Girdi
            trLabel = tk.Label(self.addPage,font=20, text="Türkçe:")
            trLabel.pack()
            self.trEntry = tk.Entry(self.addPage)
            self.trEntry.pack()

            # İngilizce Kelime için Girdi
            enLabel = tk.Label(self.addPage,font=20, text="İngilizce:")
            enLabel.pack()
            self.enEntry = tk.Entry(self.addPage)
            self.enEntry.pack()

            # Ekle Butonu
            addbutton = tk.Button(self.addPage,font=20, text="Ekle", command=lambda: self.addWord(self.trEntry.get(), self.enEntry.get()))
            addbutton.pack()

            #Ana Menüye Dönüş Butonu
            backpage=tk.Button(self.addPage, text="AnaMenüye Dön", font=20, fg="black", command=self.back_main)
            backpage.pack()
        else:
            self.addPage.deiconify()  # Eğer varsa, alt pencereyi yeniden göster
    
    def addWord(self,trWord,enWord):
        with sql.connect(wordsDb) as db:
            cursor= db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS Words (tr,en)")
            cursor.execute("SELECT * FROM Words WHERE tr=? and en=?",(trWord,enWord))
            control=cursor.fetchone()

            if control is None:  
                query= "INSERT INTO Words (tr,en) VALUES (?,?)"
                cursor.execute(query,(trWord,enWord))
                db.commit()
                self.trEntry.delete(0, tk.END)
                self.enEntry.delete(0, tk.END)
            else:
                messagebox.showerror("Bu kelime Zaten Mevcut")
                self.trEntry.delete(0, tk.END)
                self.enEntry.delete(0, tk.END)

    def learn_words(self):
        self.true=0
        self.false=0
        self.root.withdraw()  # Ana pencereyi gizle
        if not self.learnPage:
            self.learnPage = tk.Toplevel()
            self.learnPage.title("Kelime Çalış")
            self.learnPage.geometry("900x400")
            backpage=tk.Button(self.learnPage, text="AnaMenüye Dön", font=20, fg="black", command=self.back_main)
            backpage.place(x=350,y=200)
            true=tk.Label(self.learnPage,text="Doğru Sayısı", font=30)
            true.place(x=300,y=250)
            false=tk.Label(self.learnPage,text="Yanlış Sayısı", font=30)
            false.place(x=430,y=250)
            self.trueLabel= tk.Label(self.learnPage,text=self.true,font=40)
            self.trueLabel.place(x=350,y=280)
            self.falseLabel= tk.Label(self.learnPage,text=self.false,font=20)
            self.falseLabel.place(x=480,y=280)

        else:
            self.learnPage.deiconify()  # Eğer varsa, alt pencereyi yeniden göster
        with sql.connect(wordsDb) as db:
            cursor= db.cursor()
            cursor.execute("SELECT * FROM Words ORDER BY RANDOM() LIMIT 1")
            self.word= cursor.fetchone()
            selectWord= self.word[0]

            self.label= tk.Label(self.learnPage,font=30,text=selectWord)
            self.label.place(x=400,y=50)
            self.enReply=tk.Entry(self.learnPage)
            self.enReply.place(x=370,y=90)
            self.replyButton=tk.Button(self.learnPage,font=20,text="Cevapla",command=lambda: self.control(self.enReply.get()))
            self.replyButton.place(x=390,y=130)
    
    def control(self,enWord):
        with sql.connect(wordsDb) as db:
            cursor= db.cursor()
            cursor.execute("SELECT * FROM Words WHERE en=:enWord ",{"enWord":enWord})
            word= cursor.fetchone()
            
           
            if word is None:
                self.false +=1
                self.falseLabel.config(text=self.false)
                print("Düşmedi")
                with sql.connect(wrongDb) as db:
                    cursor=db.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS WrongWords (tr,en)")
                    query= "INSERT INTO WrongWords (tr,en) VALUES (?,?)"
                    cursor.execute(query,(self.word[0], self.word[1]))
                    db.commit()
            else:  
                reply=word[1]
                if reply == self.word[1]:
                    self.true+=1
                    self.trueLabel.config(text=self.true)
                    
                
                else:
                    self.false +=1
                    self.falseLabel.config(text=self.false)
                    print("Düştü")
                    with sql.connect(wrongDb) as db:
                        cursor=db.cursor()
                        cursor.execute("CREATE TABLE IF NOT EXISTS WrongWords (tr,en)")
                        query= "INSERT INTO WrongWords (tr,en) VALUES (?,?)"
                        cursor.execute(query,(self.word[0],self.word[1]))
                        db.commit()
                
            with sql.connect(wordsDb) as db:
                cursor=db.cursor()
                cursor.execute("SELECT * FROM Words ORDER BY RANDOM() LIMIT 1")
                self.word= cursor.fetchone()
                selectWord= self.word[0]
                
                self.label.config(text=selectWord) # etiketin metnini güncelle
                self.enReply.delete(0, tk.END  ) 

    def wrong_words(self):
        self.root.withdraw()  # Ana pencereyi gizle
        if not self.wrongPage:
            self.wrongPage = tk.Toplevel()
            self.wrongPage.title("Yanlış Kelimelere Çalış")
            self.wrongPage.geometry("900x400")
            backpage=tk.Button(self.wrongPage, text="AnaMenüye Dön", font=20, fg="black", command=self.back_main)
            backpage.place(x=100,y=150)
        else:
            self.wrongPage.deiconify()  # Eğer varsa, alt pencereyi yeniden göster

    def delete_wrong_words(self):
        self.root.withdraw()  # Ana pencereyi gizle
        if not self.deletePage:
            self.deletePage = tk.Toplevel()
            self.deletePage.title("Yanlış Kelimeleri Sil")
            self.deletePage.geometry("900x400")
            backpage=tk.Button(self.deletePage, text="AnaMenüye Dön", font=20, fg="black", command=self.back_main)
            backpage.place(x=100,y=150)
        else:
            self.deletePage.deiconify()  

    def back_main(self):
    # Alt pencerelerin var olup olmadığını kontrol et
        if self.addPage:
            self.addPage.destroy()
            self.addPage = None
        if self.learnPage:
            self.learnPage.destroy()
            self.learnPage = None
        if self.wrongPage:
            self.wrongPage.destroy()
            self.wrongPage = None
        if self.deletePage:
            self.deletePage.destroy()
            self.deletePage = None
        self.root.deiconify()  # Ana pencereyi tekrar göster

app = Application()
app.run()


