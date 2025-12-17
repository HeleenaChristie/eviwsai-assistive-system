import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import pytesseract
import numpy as np
import string
import time
import os
import pyttsx3
from gtts import gTTS
import speech_recognition as sr
import threading
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import platform


print("Loading models...")
caption_processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base", use_fast=True
)
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
summarizer = pipeline("summarization", model="C:/Users/HELEENA CHRISTIE/Desktop/bbc_finetuned_distilbart")
print("Models loaded.")


def speak_only(text):
    """Speak immediately, do not save."""          
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("pyttsx3 failed:", e)

def speak_and_save(text):
    """Speak and save the audio as MP3 (final output)."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    audio_filename = f"output_{timestamp}.mp3"
    try:
        tts = gTTS(text, lang='en')
        tts.save(audio_filename)
        print(f"✅ Audio saved as {audio_filename}")
        # Play the audio
        if platform.system() == 'Windows':
            os.system(f'start {audio_filename}')
        elif platform.system() == 'Darwin':
            os.system(f'afplay {audio_filename}')
        else:
            os.system(f'mpg123 {audio_filename}')  # Linux
    except Exception as e:
        print("TTS failed:", e)


def extract_text_from_image(image):
    config = r'--oem 3 --psm 4 -l eng'
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    text = pytesseract.image_to_string(thresh, config=config)
    text = ''.join([c if c in string.printable else '' for c in text])
    return text.strip()

def generate_caption(image):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    inputs = caption_processor(image_pil, return_tensors="pt")
    out = caption_model.generate(**inputs)
    caption = caption_processor.decode(out[0], skip_special_tokens=True)
    return caption

def summarize_text(text):
    if not text or len(text.split()) < 10:
        return text
    summary = summarizer(text, max_length=50, min_length=15, do_sample=False)[0]['summary_text']
    return summary

def process_and_display(frame):
    
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img.thumbnail((300, 300))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk

  
    extracted_text = extract_text_from_image(frame)
    caption = generate_caption(frame)
    summary_input = extracted_text + " " + caption
    summary = summarize_text(summary_input)

   
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Extracted Text:\n{extracted_text}\n\nImage Caption:\n{caption}\n\nSummary:\n{summary}")

   
    if len(extracted_text) < 30:
        final_output = f"Image description: {caption}."
    elif len(extracted_text) < 400:
        final_output = f"Image description: {caption}. Text detected in image: {extracted_text}"
    else:
        final_output = f"Image description: {caption}. Summary: {summary}"
    
  
    speak_and_save(final_output)


def capture_image_auto():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak_only("Camera not found.")
        return
    
    speak_only("Camera is now active. Capturing image in 3 seconds.")
    time.sleep(3)  
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        speak_only("Failed to capture image.")
        return
    
    speak_only("Image captured. Processing now.")
    process_and_display(frame)

def listen_for_voice_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    with mic as source:
        speak_only("Calibrating microphone, please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        speak_only("Calibration complete. Listening for the exact words 'capture' or 'exit'.")

    speak_only("Voice command is active. Say exactly 'capture' to take a picture or 'exit' to close the application.")

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower().strip()
                print("Heard:", command)

                if command == "capture":
                    speak_only("Command received. Capturing image.")
                    capture_image_auto()
                    time.sleep(2)

                elif command == "exit" or command == "close":
                    speak_only("Closing the application. Goodbye!")
                    app.quit()
                    break

                else:
                    speak_only("Command not recognized. Please say exactly 'capture' or 'exit'.")

        except sr.UnknownValueError:
            print("Could not understand audio")
            continue
        except sr.RequestError as e:
            speak_only("Speech recognition service is unavailable.")
            print("API error:", e)
            break



app = tk.Tk()
app.title("Assistive AI Interface")
app.geometry("600x750")
app.configure(bg="#f0f0f0")

title_label = tk.Label(app, text="Assistive AI System", font=("Helvetica", 20, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

image_label = tk.Label(app)
image_label.pack(pady=10)

capture_btn = tk.Button(app, text="📸 Capture Image", font=("Helvetica", 14),
                        command=capture_image_auto, bg="#28a745", fg="white", padx=20, pady=5)
capture_btn.pack(pady=10)

result_text = tk.Text(app, height=15, width=70, wrap=tk.WORD, font=("Helvetica", 12))
result_text.pack(pady=10)


app.after(1000, lambda: speak_only("Welcome to the Assistive AI System. Say 'capture' to take an image."))
threading.Thread(target=listen_for_voice_command, daemon=True).start()
app.mainloop()
