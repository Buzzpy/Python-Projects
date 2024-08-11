import customtkinter as ctk
from tkinter import Toplevel
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError # for better error descriptions

class StellarWalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stellar Wallet")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # Configure grid layout for basic centering
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(10, weight=1)

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        self.title_label = ctk.CTkLabel(self.root, text="Stellar Wallet 💳", font=("Arial", 20, "bold"))
        self.title_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="n")

        # Public Key Label
        self.public_key_label = ctk.CTkLabel(self.root, text="Public Key:", font=("Arial", 15, "bold"))
        self.public_key_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

        # Public Key Entry
        self.public_key_entry = ctk.CTkEntry(self.root,
                                             placeholder_text="Enter Public Key",
                                             font=("Courier New", 14),
                                             border_width=2,
                                             border_color='#2da572',
                                             height=40,
                                             width=350)
        self.public_key_entry.grid(row=3, column=0, padx=(10, 0), pady=(5, 15))

        # Secret Key Label
        self.secret_key_label = ctk.CTkLabel(self.root, text="Secret Key:", font=("Arial", 15, "bold"))
        self.secret_key_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")

        # Secret Key Entry
        self.secret_key_entry = ctk.CTkEntry(self.root,
                                             placeholder_text="Enter Secret Key",
                                             font=("Courier New", 14),
                                             border_width=2,
                                             border_color='#2da572',
                                             height=40,
                                             show="*",
                                             width=350)
        self.secret_key_entry.grid(row=5, column=0, padx=(10, 0), pady=(5, 15))

        # Create Account Button
        self.create_account_button = ctk.CTkButton(self.root,
                                                   text="Create Account",
                                                   text_color="black",
                                                   font=("Courier New", 14,"bold"),
                                                   width=250,
                                                   height=40,
                                                   command=self.create_account)
        self.create_account_button.grid(row=6, column=0, padx=(10, 0), pady=(10, 10))

        # Check Balance Button
        self.balance_button = ctk.CTkButton(self.root,
                                            text="Check Balance",
                                            text_color="black",
                                            font=("Courier New", 14),
                                            width=250,
                                            height=40,
                                            command=self.check_balance)
        self.balance_button.grid(row=7, column=0, padx=(10, 0), pady=(10, 10))

        # Send Payment Button
        self.send_payment_button = ctk.CTkButton(self.root,
                                                 text="Send Payment",
                                                 text_color="black",
                                                 font=("Courier New", 14),
                                                 width=250,
                                                 height=40,
                                                 command=self.send_payment)
        self.send_payment_button.grid(row=8, column=0, padx=(10, 0), pady=(10, 10))

        # Result Label
        self.result_label = ctk.CTkLabel(self.root, text="", font=("Arial", 14))
        self.result_label.grid(row=9, column=0, padx=(10, 0), pady=(20, 20))



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
        try:
            public_key = self.public_key_entry.get()
            server = Server("https://horizon-testnet.stellar.org")
            account = server.accounts().account_id(public_key).call()
            balances = account['balances']
            if not balances or all(float(b['balance']) == 0 for b in balances):
                self.show_toplevel_message("No balance")
            else:
                balance_text = "\n".join([f"Asset Type: {b['asset_type']}, Balance: {b['balance']}" for b in balances])
                self.result_label.configure(text=balance_text)
        except Exception:
            self.show_toplevel_message("Failed to retrieve balance")

    def send_payment(self):
        """Send a payment to another Stellar account."""
        try:
            source_secret = self.secret_key_entry.get()
            if not source_secret:
                self.show_toplevel_message("Payment unsuccessful: Secret key is required")
                return

            destination_public = self.prompt_input("Enter destination public key:")
            print(f"Destination Public Key: {destination_public}")  # Debugging line
            amount = self.prompt_float_input("Enter amount to send:")
            print(f"Amount to send: {amount}")  # Debugging line

            if not destination_public or not amount:
                self.show_toplevel_message("Payment unsuccessful: All fields are required")
                return

            source_keypair = Keypair.from_secret(source_secret)
            server = Server("https://horizon-testnet.stellar.org")

            # Check if source account exists
            try:
                source_account = server.load_account(source_keypair.public_key)
            except NotFoundError:
                self.show_toplevel_message("Payment unsuccessful: Source account not found")
                return

            # Check if destination account exists
            try:
                server.accounts().account_id(destination_public).call()
            except NotFoundError:
                self.show_toplevel_message("Payment unsuccessful: Destination account not found")
                return

            transaction = TransactionBuilder(
                source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100
            ).add_text_memo("Stellar Payment").append_payment_op(
                destination=destination_public,
                amount=str(amount),
                asset=Asset.native()  # Specify that the asset is the native XLM
            ).build()

            transaction.sign(source_keypair)
            response = server.submit_transaction(transaction)
            self.result_label.configure(text=f"Payment sent!\nTransaction Hash:\n{response['hash']}", font=("Courier New", 10))

        except Exception as e:
            print(f"Exception occurred: {e}")  # Debugging line
            self.show_toplevel_message("Payment unsuccessful")
    def show_toplevel_message(self, message):
        """Display a top-level window with a message."""
        top = Toplevel(self.root)
        top.title("Notification")
        top.geometry("400x400")
        top.resizable(False, False)

        msg = ctk.CTkLabel(top, text=message, font=("Arial", 15, "bold"))
        msg.pack(pady=20)

        button = ctk.CTkButton(top, text="OK", command=top.destroy, font=("Arial", 15, "bold"), width=150)
        button.pack(pady=20)

    def prompt_input(self, prompt_text):
        """Prompt for string input using a custom Toplevel window."""
        input_window = Toplevel(self.root)
        input_window.title(prompt_text)
        input_window.geometry("400x400")
        input_window.resizable(False, False)

        prompt_label = ctk.CTkLabel(input_window, text=prompt_text, font=("Arial", 15, "bold"))
        prompt_label.pack(pady=(40, 20))

        input_entry = ctk.CTkEntry(input_window, font=("Arial", 15, "bold"), width=300)
        input_entry.pack(pady=20)

        input_value = []

        def submit_input():
            input_value.append(input_entry.get())
            input_window.destroy()

        submit_button = ctk.CTkButton(input_window, text="Submit", command=submit_input, font=("Arial", 15, "bold"),
                                      width=150)
        submit_button.pack(pady=20)

        input_window.wait_window()

        return input_value[0] if input_value else None

    def prompt_float_input(self, prompt_text):
        """Prompt for float input using a custom Toplevel window."""
        input_window = Toplevel(self.root)
        input_window.title(prompt_text)
        input_window.geometry("400x400")
        input_window.resizable(False, False)

        prompt_label = ctk.CTkLabel(input_window, text=prompt_text, font=("Arial", 15, "bold"))
        prompt_label.pack(pady=(40, 20))

        input_entry = ctk.CTkEntry(input_window, font=("Arial", 15, "bold"), width=300)
        input_entry.pack(pady=20)

        input_value = []

        def submit_input():
            try:
                input_value.append(float(input_entry.get()))
            except ValueError:
                input_value.append(None)
            input_window.destroy()

        submit_button = ctk.CTkButton(input_window, text="Submit", command=submit_input, font=("Arial", 15, "bold"),
                                      width=150)
        submit_button.pack(pady=20)

        input_window.wait_window()

        return input_value[0] if input_value else None


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Use system theme
    ctk.set_default_color_theme("green")  # Default color theme without customization

    root = ctk.CTk()
    app = StellarWalletApp(root)
    root.mainloop()
