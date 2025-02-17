import customtkinter as ctk
from tkinter import Toplevel
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError  # for better error descriptions


class StellarWalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stellar Wallet")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        self.root.grid_columnconfigure(0, weight=1)

        # Style configurations
        self.style_config = {
            "label": {"font": ("Arial", 15, "bold")},
            "entry": {"font": ("Courier New", 14), "border_width": 2, "border_color": '#2da572', "height": 40,
                      "width": 350},
            "button": {"text_color": "black", "font": ("Courier New", 14, "bold"), "width": 250, "height": 40},
        }

        # Grid layout configuration
        self.grid_config = {
            "padx": 10,
            "pady": (10, 5),

        }

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = ctk.CTkLabel(self.root, text="Stellar Wallet 💳", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, pady=(20, 30), sticky="n")

        # Public Key Section
        self.public_key_entry = self._create_labeled_entry("Public Key:", row=1)

        # Secret Key Section
        self.secret_key_entry = self._create_labeled_entry("Secret Key:", row=3, show="*")

        # Buttons
        buttons_info = [
            ("Create Account", self.create_account),
            ("Check Balance", self.check_balance),
            ("Send Payment", self.send_payment),
        ]
        for idx, (btn_text, btn_command) in enumerate(buttons_info):
            button = ctk.CTkButton(self.root, text=btn_text, command=btn_command, **self.style_config["button"])
            button.grid(row=5 + idx, column=0, pady=(15, 10))

        # Result Label
        self.result_label = ctk.CTkLabel(self.root, text="", font=("Arial", 14))
        self.result_label.grid(row=8, column=0, pady=(20, 20))

    def _create_labeled_entry(self, label_text, row, show=None):
        """Helper method to create labeled entry widgets."""
        label = ctk.CTkLabel(self.root, text=label_text, **self.style_config["label"])
        label.grid(row=row, column=0, **self.grid_config)

        entry = ctk.CTkEntry(self.root, **self.style_config["entry"], show=show)
        entry.grid(row=row + 1, column=0, padx=(10, 0), pady=(5, 15))

        return entry

    def _get_input(self, prompt_text, input_type=str):
        """Unified method to get user input with type conversion."""
        input_window = Toplevel(self.root)
        input_window.title(prompt_text)
        input_window.geometry("400x200")
        input_window.resizable(False, False)

        prompt_label = ctk.CTkLabel(input_window, text=prompt_text, font=("Arial", 15, "bold"))
        prompt_label.pack(pady=(20, 10))

        input_entry = ctk.CTkEntry(input_window, font=("Arial", 15, "bold"), width=300)
        input_entry.pack(pady=10)

        input_value = []

        def submit_input():
            try:
                value = input_type(input_entry.get())
                input_value.append(value)
            except ValueError:
                input_value.append(None)
            input_window.destroy()

        submit_button = ctk.CTkButton(input_window, text="Submit", command=submit_input, font=("Arial", 15, "bold"),
                                      width=150)
        submit_button.pack(pady=10)

        input_window.wait_window()
        return input_value[0] if input_value else None

    def create_account(self):
        """Generate a new Stellar account and display the keys."""
        pair = Keypair.random()
        self.public_key_entry.delete(0, ctk.END)
        self.public_key_entry.insert(0, pair.public_key)
        self.secret_key_entry.delete(0, ctk.END)
        self.secret_key_entry.insert(0, pair.secret)
        self.result_label.configure(text="New account created! Use Testnet Faucet to fund it.")

    def check_balance(self):
        """Check and display the balance of the account."""
        public_key = self.public_key_entry.get()
        if not public_key:
            self.show_toplevel_message("Public key is required.")
            return

        try:
            server = Server("https://horizon-testnet.stellar.org")
            account = server.accounts().account_id(public_key).call()
            balances = account['balances']
            if not balances or all(float(b['balance']) == 0 for b in balances):
                self.show_toplevel_message("No balance found.")
            else:
                balance_text = "\n".join([f"Asset Type: {b['asset_type']}, Balance: {b['balance']}" for b in balances])
                self.result_label.configure(text=balance_text)
        except NotFoundError:
            self.show_toplevel_message("Account not found.")
        except Exception as e:
            self.show_toplevel_message(f"Failed to retrieve balance: {str(e)}")

    def send_payment(self):
        """Send a payment to another Stellar account."""
        source_secret = self.secret_key_entry.get()
        if not source_secret:
            self.show_toplevel_message("Payment unsuccessful: Secret key is required.")
            return

        destination_public = self._get_input("Enter destination public key:")
        amount = self._get_input("Enter amount to send:", float)

        if not destination_public or not amount:
            self.show_toplevel_message("Payment unsuccessful: All fields are required.")
            return

        try:
            source_keypair = Keypair.from_secret(source_secret)
            server = Server("https://horizon-testnet.stellar.org")

            # Check if source account exists
            try:
                source_account = server.load_account(source_keypair.public_key)
            except NotFoundError:
                self.show_toplevel_message("Payment unsuccessful: Source account not found.")
                return

            # Check if destination account exists
            try:
                server.accounts().account_id(destination_public).call()
            except NotFoundError:
                self.show_toplevel_message("Payment unsuccessful: Destination account not found.")
                return

            transaction = (
                TransactionBuilder(
                    source_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=100
                )
                .add_text_memo("Stellar Payment")
                .append_payment_op(
                    destination=destination_public,
                    amount=str(amount),
                    asset=Asset.native()  # Specify that the asset is the native XLM
                )
                .build()
            )
            transaction.sign(source_keypair)
            response = server.submit_transaction(transaction)
            self.result_label.configure(text=f"Payment sent!\nTransaction Hash:\n{response['hash']}",
                                        font=("Courier New", 10))
        except Exception as e:
            self.show_toplevel_message(f"Payment unsuccessful: {str(e)}")

    def show_toplevel_message(self, message):
        """Display a top-level window with a message."""
        top = Toplevel(self.root)
        top.title("Notification")
        top.geometry("400x200")
        top.resizable(False, False)

        msg = ctk.CTkLabel(top, text=message, font=("Arial", 15, "bold"))
        msg.pack(pady=20)

        button = ctk.CTkButton(top, text="OK", command=top.destroy, font=("Arial", 15, "bold"), width=150)
        button.pack(pady=20)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Use system theme
    ctk.set_default_color_theme("green")  # Default color theme without customization
    root = ctk.CTk()
    app = StellarWalletApp(root)
    root.mainloop()
