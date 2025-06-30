import tkinter as tk
from tkinter import filedialog, messagebox
import speech_recognition as sr
import threading

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodTech Speech Recognition")
        self.root.geometry("500x400")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Speech Recognition System", font=("Arial", 16)).pack(pady=10)
        
        # Output Text
        self.output_text = tk.Text(self.root, height=10, width=50, state='disabled')
        self.output_text.pack(pady=10)
        
        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Microphone Button
        self.mic_btn = tk.Button(
            button_frame, 
            text="🎤 Use Microphone", 
            command=self.start_mic_recognition,
            width=16
        )
        self.mic_btn.pack(side=tk.LEFT, padx=5)
        
        # File Button
        self.file_btn = tk.Button(
            button_frame, 
            text="📁 Open Audio File", 
            command=self.open_audio_file,
            width=16
        )
        self.file_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear Button
        tk.Button(
            button_frame, 
            text="❌ Clear", 
            command=self.clear_output,
            width=16
        ).pack(side=tk.LEFT, padx=5)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(self.root, textvariable=self.status_var).pack(pady=5)
        
    def start_mic_recognition(self):
        self.mic_btn.config(state=tk.DISABLED)
        self.status_var.set("Listening... Speak now!")
        
        # Run in separate thread to prevent GUI freezing
        threading.Thread(target=self.recognize_from_mic, daemon=True).start()
        
    def recognize_from_mic(self):
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                
                self.update_status("Processing...")
                text = recognizer.recognize_google(audio)
                
                self.update_output(f"🎤 You said:\n{text}\n")
                self.update_status("Success! Click to record again")
                
        except sr.WaitTimeoutError:
            self.update_status("Timeout: No speech detected")
        except sr.UnknownValueError:
            self.update_status("Could not understand audio")
        except sr.RequestError as e:
            self.update_status(f"API Error: {str(e)}")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.root.after(0, lambda: self.mic_btn.config(state=tk.NORMAL))
    
    def open_audio_file(self):
        filetypes = [("Audio Files", "*.wav *.aiff *.flac *.mp3")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        
        if filepath:
            self.file_btn.config(state=tk.DISABLED)
            self.status_var.set(f"Processing: {filepath}")
            
            # Run in separate thread
            threading.Thread(
                target=self.recognize_from_file, 
                args=(filepath,), 
                daemon=True
            ).start()
    
    def recognize_from_file(self, filepath):
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(filepath) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                
                self.update_output(f"📁 From file:\n{text}\n")
                self.update_status(f"Success! Processed {filepath}")
                
        except sr.UnknownValueError:
            self.update_status("Could not understand audio in file")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.root.after(0, lambda: self.file_btn.config(state=tk.NORMAL))
    
    def update_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))
    
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()