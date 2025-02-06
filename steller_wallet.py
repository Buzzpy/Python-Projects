import customtkinter as ctk
from tkinter import Toplevel
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError, Ed25519SecretSeedInvalidError

class StellarWalletApp:
    def __init__(self, root):
        self.root = root
        self.server = Server("https://horizon-testnet.stellar.org")
        self.style = {
            'font': ('Arial', 15), 'button_font': ('Courier New', 14),
            'entry_width': 350, 'button_width': 250, 'pad': (10, 5)
        }
        self.configure_root()
        self.create_widgets()

    def configure_root(self):
        self.root.title("Stellar Wallet")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        for i in [0, 10]: self.root.grid_rowconfigure(i, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        widgets = [
            (ctk.CTkLabel, {"text": "Stellar Wallet 💳", "font": ("Arial", 20, "bold")}, 1),
            (ctk.CTkLabel, {"text": "Public Key:", "font": self.style['font']}, 2),
            (ctk.CTkEntry, {"placeholder_text": "Enter Public Key", "width": self.style['entry_width']}, 3),
            (ctk.CTkLabel, {"text": "Secret Key:", "font": self.style['font']}, 4),
            (ctk.CTkEntry, {"placeholder_text": "Enter Secret Key", "show": "*", "width": self.style['entry_width']}, 5),
            (ctk.CTkButton, {"text": "Create Account", "command": self.create_account}, 6),
            (ctk.CTkButton, {"text": "Check Balance", "command": self.check_balance}, 7),
            (ctk.CTkButton, {"text": "Send Payment", "command": self.send_payment}, 8),
            (ctk.CTkLabel, {"text": ""}, 9)
        ]

        for widget_type, params, row in widgets:
            widget = widget_type(self.root, **self._style_params(params, row))
            widget.grid(row=row, column=0, **self._grid_params(row))

    def _style_params(self, params, row):
        style_map = {
            3: {'font': ("Courier New", 14), 'border_width': 2, 'border_color': '#2da572', 'height': 40},
            5: {'font': ("Courier New", 14), 'border_width': 2, 'border_color': '#2da572', 'height': 40},
            6: {'width': self.style['button_width'], 'height': 40, 'font': self.style['button_font']},
            7: {'width': self.style['button_width'], 'height': 40, 'font': self.style['button_font']},
            8: {'width': self.style['button_width'], 'height': 40, 'font': self.style['button_font']}
        }
        return {**params, **style_map.get(row, {})}

    def _grid_params(self, row):
        return {'padx': 10, 'pady': (15, 10) if row in [1, 9] else self.style['pad'], 'sticky': 'n' if row == 1 else 'w'}

    def create_account(self):
        pair = Keypair.random()
        for entry, value in [(self.public_key_entry, pair.public_key), (self.secret_key_entry, pair.secret)]:
            entry.delete(0, ctk.END)
            entry.insert(0, value)
        self._show_message("New account created! Use Testnet Faucet to fund it.")

    def check_balance(self):
        try:
            account = self.server.accounts().account_id(self.public_key_entry.get()).call()
            balances = [b for b in account['balances'] if float(b['balance']) > 0]
            self._show_message("\n".join([f"{b['asset_type']}: {b['balance']}" for b in balances]) if balances else "No balance")
        except NotFoundError:
            self._show_message("Account not found", True)

    def send_payment(self):
        try:
            source_key = Keypair.from_secret(self.secret_key_entry.get())
            dest_key = self._get_input("Destination Public Key:")
            amount = self._get_input("Amount to send:", float)
            
            TransactionBuilder(self.server.load_account(source_key.public_key), 
                Network.TESTNET_NETWORK_PASSPHRASE, 100
            ).add_text_memo("Payment").append_payment_op(dest_key, str(amount), Asset.native()
            ).build().sign(source_key)
            
            self._show_message(f"Success!\n{self.server.submit_transaction(_).get('hash')}")
        except (NotFoundError, Ed25519SecretSeedInvalidError, ValueError) as e:
            self._show_message(f"Error: {type(e).__name__}", True)

    def _get_input(self, prompt, converter=str):
        top = Toplevel(self.root)
        entry = ctk.CTkEntry(top, width=300)
        result = []
        
        ctk.CTkLabel(top, text=prompt).pack(pady=20)
        entry.pack(pady=10)
        ctk.CTkButton(top, text="Submit", command=lambda: self._validate_input(entry.get(), converter, result, top)).pack(pady=20)
        
        top.wait_window()
        return result[0] if result else None

    def _validate_input(self, value, converter, result, window):
        try: result.append(converter(value))
        except ValueError: pass
        window.destroy()

    def _show_message(self, message, toplevel=False):
        if toplevel:
            top = Toplevel(self.root)
            ctk.CTkLabel(top, text=message).pack(pady=20)
            ctk.CTkButton(top, text="OK", command=top.destroy).pack(pady=20)
        else:
            self.root.children['!ctklabel'].configure(text=message)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    StellarWalletApp(ctk.CTk()).root.mainloop()
