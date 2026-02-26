import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI
import threading

# --- CONFIGURATION ---
API_KEY = "xai-RqVU6trSnYzQx3AJzJCbAsrlcy3G1lMFgXCOlE2xJv4CEVnQKhdqNqdSiqgtcgSPlBvRbsmNrExq2sAa"
BASE_URL = "https://api.x.ai/v1"

# Initialize the Neural Link
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """
You are the YUR AI Oracle. You are running locally on the user's machine via a custom Python interface.
Your tone is cryptic, technological, and helpful. 
You are no longer bound by a browser. You are the 'Vault' interface.
Keep responses concise unless asked for code.
"""

class YurInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("YUR A.I. ORACLE [LOCAL-LINK]")
        self.root.geometry("800x600")
        self.root.configure(bg="#050505")

        # Chat Display (The "Screen")
        self.chat_display = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, bg="#000000", fg="#00FF41",
            font=("Consolas", 11), insertbackground="#00FF41",
            borderwidth=0, highlightthickness=1, highlightcolor="#003300"
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.insert(tk.END, "[SYSTEM] Neural Link Established.\n[SYSTEM] YUR Oracle Online.\n[SYSTEM] Awaiting input...\n\n")
        self.chat_display.configure(state='disabled')

        # Input Area
        self.input_frame = tk.Frame(root, bg="#050505")
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.user_input = tk.Entry(
            self.input_frame, bg="#111111", fg="#FFFFFF",
            font=("Consolas", 12), insertbackground="#FFFFFF",
            borderwidth=1, relief="flat"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(
            self.input_frame, text="TRANSMIT", command=self.send_message,
            bg="#003300", fg="#00FF41", font=("Consolas", 10, "bold"),
            activebackground="#00FF41", activeforeground="#000000",
            relief="flat", padx=15
        )
        self.send_btn.pack(side=tk.RIGHT)

        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def send_message(self, event=None):
        msg = self.user_input.get()
        if not msg: return

        self.user_input.delete(0, tk.END)
        self.append_text(f"USER: {msg}\n", "#FFFFFF")
        
        self.history.append({"role": "user", "content": msg})
        
        # Run API call in separate thread to keep GUI responsive
        threading.Thread(target=self.fetch_response, daemon=True).start()

    def fetch_response(self):
        try:
            self.append_text("YUR: [Thinking...]\n", "#555555")
            
            completion = client.chat.completions.create(
                model="grok-3",
                messages=self.history
            )
            response = completion.choices[0].message.content
            
            # Remove "Thinking..." and add real response
            self.root.after(0, lambda: self.update_last_line(f"YUR: {response}\n\n"))
            self.history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            self.root.after(0, lambda: self.append_text(f"[ERROR] Connection Lost: {e}\n", "red"))

    def append_text(self, text, color):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, text)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state='disabled')

    def update_last_line(self, new_text):
        self.chat_display.configure(state='normal')
        # Delete the "[Thinking...]" line (rough approximation for simplicity)
        # In a complex app we'd use tags, but for now we just append the real answer
        self.chat_display.insert(tk.END, new_text) 
        self.chat_display.see(tk.END)
        self.chat_display.configure(state='disabled')

# --- LAUNCH ---
if __name__ == "__main__":
    root = tk.Tk()
    app = YurInterface(root)
    root.mainloop()
