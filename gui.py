from audioop import avg
from cgitb import text
import imghdr
from multiprocessing.sharedctypes import Value
from tkinter import *
import tkinter
from turtle import bgcolor, color, window_height, window_width
import urllib.request
import cv2
from cv2 import detail_DpSeamFinder
import numpy as np
from random import random as rand
from PIL import ImageTk,Image, ImageEnhance


#url = 'https://previews.customer.envatousercontent.com/h264-video-previews/0888dd36-1a5b-4e5b-9fbf-e7bca069d213/16602591.mp4'
#url2 = 'https://media.istockphoto.com/videos/male-dancer-in-studio-shows-ballerina-spin-video-id929138872'
url3 = 'https://media.istockphoto.com/videos/baseball-batter-hitting-ball-during-game-video-id640837234'
url4 = 'https://media.istockphoto.com/videos/modern-dancer-girl-in-white-dress-starts-dancing-contemporary-on-video-id516645076'
#url5 = Geometry
#url5 = 'https://media.istockphoto.com/videos/abstract-logo-promo-pattern-of-circles-with-the-effect-of-white-video-id1220546660'

def backgroundSubtraction(str):
    global avg_img
    global img
    file = 'test2_video.mp4'
    urllib.request.urlretrieve(str, file)
    stream = cv2.VideoCapture(file)
    _, firstframe = stream.read()
    frame_count = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
    images2 = []
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    for i in range(frame_count-1):
        _, frame = stream.read()
        fgmask = fgbg.apply(frame)
        rgba = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)
        rgba[:, :, 3] = fgmask
        images2.append(rgba)
    avg_img = np.mean(images2, axis=0)
    avg_img = avg_img.astype(np.uint8)
    img = ImageTk.PhotoImage(Image.fromarray(avg_img), master=fenster)
    label.image = img
    label.config(image=img)
    global bild
    bild=True

def button_action():
    global delete_button
    global sharpeness_button_entry
    global sharpeness_button
    global sharpeness_button_label
    global kontrast_button
    global kontrast_button_entry
    global kontrast_button_label
    global reset_button
    url_text = video_url.get()
    if(url_text == ""):
        url_fehler_label.config(text="Gib bitte zuerst eine gültige URL ein.")
    else:
        url_text = "Es hat geklappt mit der URL: " + url_text
        url_fehler_label.config(text=url_text)
        backgroundSubtraction(video_url.get())
        kontrast_button_label = Label(fenster, text="Gib hier einen gewünschten Wert für den Kontrast ein:")
        kontrast_button_label.pack()
        kontrast_button_entry = Entry(fenster, bd=5, width=20)
        kontrast_button_entry.pack()
        kontrast_button = Button(fenster, text="Bestätigen", command=wert_anpassen)
        kontrast_button.pack()

        sharpeness_button_label = Label(fenster, text="Gib hier einen Wert für die Schärfe ein:")
        sharpeness_button_label.pack()
        sharpeness_button_entry = Entry(fenster, bd=5, width=20)
        sharpeness_button_entry.pack()
        sharpeness_button = Button(fenster, text="Bestätigen", command=sharpeness_anpassen)
        sharpeness_button.pack()

        reset_button = Button(fenster, text="Reset", command=reset)
        reset_button.pack()

        delete_button = Button(fenster, text="Delete Image", command=delete_img)
        delete_button.pack()
        fenster.update()

def wert_anpassen():
    global img
    if(bild):
        enhancer = ImageEnhance.Contrast(ImageTk.getimage(img))
        factor = int(kontrast_button_entry.get())
        output = enhancer.enhance(factor)
        img = ImageTk.PhotoImage(output, master=fenster)
        label.image = img
        label.config(image=img)
        fenster.update()

def sharpeness_anpassen():
    global img
    if(bild):
        enhancer = ImageEnhance.Sharpness(ImageTk.getimage(img))
        factor = np.double(sharpeness_button_entry.get())
        output = enhancer.enhance(factor)
        img = ImageTk.PhotoImage(output, master=fenster)
        label.image = img
        label.config(image = img)
        fenster.update()

def delete_img():
    global img
    global bild
    img = ""
    label.config(image = "")
    url_fehler_label.config(text="")
    bild=False
    delete_button.destroy()
    sharpeness_button.destroy()
    sharpeness_button_entry.destroy()
    sharpeness_button_label.destroy()
    kontrast_button_entry.destroy()
    kontrast_button.destroy()
    kontrast_button_label.destroy()
    reset_button.destroy()
    fenster.update

def reset():
    global img
    global avg_img
    img = ImageTk.PhotoImage(Image.fromarray(avg_img), master=fenster)
    label.image = img
    label.config(image=img)

fenster = Tk()
fenster.title("Freeze Me!")
fenster.geometry("700x700")
global bild
bild=False
video_url_label = Label(fenster, text="Bitte gib hier die URL ein: ")
#video_url_label.grid(row=0, column=0)
video_url_label.pack()
video_url = Entry(fenster, bd=5, width=40)
#video_url.grid(row=0, column=1)
video_url.pack()

url_button = Button(fenster, text="Bestätigen", command=button_action)
#url_button.grid(row=1, column=1)
url_button.pack()

menuleiste = Menu(fenster)
menuleiste.add_command(label="Exit", command=fenster.quit)
fenster.config(menu=menuleiste)


url_fehler_label = Label(fenster)
#url_fehler_label.grid(row=2, column=0)
url_fehler_label.pack()

label = Label(fenster)
label.pack()

fenster.mainloop()