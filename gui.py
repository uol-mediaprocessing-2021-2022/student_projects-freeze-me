from audioop import avg
from cgitb import text
import imghdr
from multiprocessing.sharedctypes import Value
from tkinter import *
import tkinter
from tkinter import filedialog
from tkinter import ttk
from turtle import bgcolor, color, window_height, window_width
import urllib.request
import cv2
from cv2 import detail_DpSeamFinder
from cv2 import resize
import numpy as np
from random import random as rand
from PIL import ImageTk,Image, ImageEnhance

#url = 'https://previews.customer.envatousercontent.com/h264-video-previews/0888dd36-1a5b-4e5b-9fbf-e7bca069d213/16602591.mp4'
#url2 = 'https://media.istockphoto.com/videos/male-dancer-in-studio-shows-ballerina-spin-video-id929138872'
url3 = 'https://media.istockphoto.com/videos/baseball-batter-hitting-ball-during-game-video-id640837234'
url4 = 'https://media.istockphoto.com/videos/modern-dancer-girl-in-white-dress-starts-dancing-contemporary-on-video-id516645076'
#url5 = Geometry
#url5 = 'https://media.istockphoto.com/videos/abstract-logo-promo-pattern-of-circles-with-the-effect-of-white-video-id1220546660'
def createFile(str):
    global file
    file = 'test2_video.mp4'
    urllib.request.urlretrieve(str, file)

def average_images(images, opacity):
    avg_img = np.ma.average(images, axis=0)
    avg_img = avg_img.astype(np.uint8)
    avg_img_bgra = cv2.cvtColor(avg_img, cv2.COLOR_BGR2BGRA)
    alpha_channel = avg_img_bgra[:, :, 3]
    alpha_channel[np.all(avg_img_bgra[:, :, 0:3] == (0, 0, 0), 2)] = 0
    avg_img_bgra = avg_img_bgra.astype(np.float64)
    avg_img_bgra[:, :, 3] *= opacity
    avg_img_bgra = avg_img_bgra.astype(np.uint8)

    # final_img = cv.add(avg_img_bgra, cv.cvtColor(firstframe, cv.COLOR_RGB2BGRA))
    return avg_img_bgra

def background_substraction(stream, noise_reduction=False, limiter=0):
    ret, frame = stream.read()
    images = []
    fgbg = cv2.createBackgroundSubtractorKNN()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    limiter_count = 1
    while ret:
        if limiter_count <= limiter:
            limiter_count += 1
            ret, frame = stream.read()
            continue
        limiter_count = 1
        fgmask = fgbg.apply(frame)
        if noise_reduction:
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        testcolor = cv2.bitwise_and(frame, cv2.cvtColor(fgmask, cv2.COLOR_GRAY2RGB))
        masked = np.ma.masked_equal(testcolor, 0)
        images.append(masked)
        ret, frame = stream.read()
    return images

def optical_flow(stream, int_threshold=150, noise_reduction=False, limiter=0):
    ret, frame1 = stream.read()
    prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255
    images = []
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    limiter_count = 1
    while (1):
        ret, frame2 = stream.read()
        if not ret:
            break
        if limiter_count <= limiter:
            limiter_count += 1
            continue
        limiter_count = 1
        next = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        intensity = hsv[:, :, 2]
        intensity_mask = (np.logical_not(intensity < int_threshold) * 255).astype(np.uint8)
        mask = np.dstack((intensity_mask, intensity_mask, intensity_mask))
        if noise_reduction:
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        masked_img = cv2.bitwise_and(frame2, mask)
        masked = np.ma.masked_equal(masked_img, 0)
        images.append(masked)
        prvs = next
    return images

def video_to_freeze_picture(mode, blur_motion=False, opacity=0.5, noise_reduction=False, limit=None):
    global img
    global output
    stream = cv2.VideoCapture(file)
    max_frames = stream.get(cv2.CAP_PROP_POS_FRAMES)
    if limit is None:
        limit_val = max_frames + 3
    else:
        limit_val = int(max_frames/(max_frames/limit))
    if mode.lower() == 'bgs':
        images = background_substraction(stream)
    elif mode.lower() == 'of':
        images = optical_flow(stream, noise_reduction=noise_reduction)
    elif mode.lower() == 'both':
        print("Not implemented yet")
        quit()
    else:
        print("No valid mode provided")
        quit()
    avg_image = average_images(images, opacity=opacity)
    if blur_motion:
        avg_image = cv2.blur(avg_image,(3,3))
    stream.set(cv2.CAP_PROP_POS_FRAMES,0)
    ret, img = stream.read()
    avg_img_to_gray = cv2.cvtColor(avg_image, cv2.COLOR_BGR2GRAY)
    motion_mask_inv = (np.logical_not(avg_img_to_gray > 1) * 255).astype(np.uint8)
    firstframe_masked = cv2.bitwise_and(img, img, mask=motion_mask_inv)
    final_img = cv2.add(avg_image, cv2.cvtColor(firstframe_masked, cv2.COLOR_BGR2BGRA))
    final_img = cv2.resize(final_img, (960, 540))
    img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGRA2RGBA)), master=fenster)
    output = img
    label.image = img
    label.config(image=img)
    global bild
    bild=True

def openFile():
    global file
    file = filedialog.askopenfilename()

def button_action():
    global file
    if(methode_box.get() == "Background Subtraction"):
        methode = 'bgs'
    else:
        methode = 'of'
    url_text = video_url.get()
    if(url_text == "" and file == ""):
        url_fehler_label.config(text="Gib bitte zuerst eine gültige URL ein oder wähle eine Video Datei aus.")
    elif(url_text == "" and file != ""):
        if(file.lower().endswith('.mp4')):
            url_fehler_label.config(text="")
            video_to_freeze_picture(methode)
            createOptions()
            fenster.update()
        else: 
            url_fehler_label.config(text="Bitte wähle eine gültige Video Datei aus.")
            if(bild==True):
                delete_img()
                url_fehler_label.config(text="Bitte wähle eine gültige Video Datei aus.")

    else:
        createFile(video_url.get())
        video_to_freeze_picture(methode)
        createOptions()
        fenster.update()

def createOptions():
    global delete_button
    global sharpeness_button_entry
    global sharpeness_button
    global sharpeness_button_label
    global kontrast_button
    global kontrast_button_entry
    global kontrast_button_label
    global reset_button
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
    global output
    img = output
    #img = ImageTk.PhotoImage(Image.fromarray(output), master=fenster)
    label.image = img
    label.config(image=img)

fenster = Tk()
fenster.title("Freeze Me!")
fenster.geometry("1200x1000")
global bild
bild=False
video_url_label = Label(fenster, text="Bitte gib hier die URL eines Videos ein: ")
#video_url_label.grid(row=0, column=0)
video_url_label.pack()
video_url = Entry(fenster, bd=5, width=40)
#video_url.grid(row=0, column=1)
video_url.pack()

upload_video_label = Label(fenster, text="Oder wähle eine Videodatei aus.")
upload_video_label.pack()
upload_button = Button(fenster, text="Öffnen", command=openFile)
upload_button.pack()

methode_label = Label(fenster, text="Wähle eine Methode aus.")
methode_label.pack()
methode_box = ttk.Combobox(fenster, values=['Background Subtraction', 'Optical Flow'])
methode_box.current(0)
methode_box.pack()

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