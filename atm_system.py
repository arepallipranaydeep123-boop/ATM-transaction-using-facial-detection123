import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
accounts_file = os.path.join(script_dir, 'accounts.json')

DEFAULT_ACCOUNTS = {
    'Pranay': 1000.0,
    'User2': 500.0,
    'User3': 250.0,
}


def load_accounts():
    if os.path.exists(accounts_file):
        with open(accounts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_ACCOUNTS.copy()


def save_accounts(accounts):
    with open(accounts_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2)


def prompt_float(prompt_text):
    while True:
        value = input(prompt_text).strip()
        try:
            amount = float(value)
            if amount <= 0:
                print('Please enter a positive number.')
                continue
            return amount
        except ValueError:
            print('Invalid amount. Please enter a number.')


def run(username):
    balance = 5000
    pin = "1234"
    
    print(f"\n===== Welcome {username} =====")
    
    entered_pin = input("Enter ATM PIN: ")
    
    if entered_pin == pin:
        print("\n✓ PIN Verified - Login Successful")
    
        while True:
            print("\n===== ATM MENU =====")
            print("1. Check Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Change PIN")
            print("5. Exit")
    
            choice = input("Enter your choice: ")
    
            if choice == '1':
                print(f"\n Current Balance: ${balance:.2f}")
    
            elif choice == '2':
                try:
                    amount = float(input("Enter amount to deposit: $"))
                    if amount > 0:
                        balance += amount
                        print(f"✓ Amount Deposited Successfully: ${amount:.2f}")
                        print(f"Updated Balance: ${balance:.2f}")
                    else:
                        print("✗ Please enter a positive amount")
                except ValueError:
                    print("✗ Invalid amount entered")
    
            elif choice == '3':
                try:
                    amount = float(input("Enter amount to withdraw: $"))
                    if amount <= 0:
                        print("✗ Please enter a positive amount")
                    elif amount <= balance:
                        balance -= amount
                        print(f"✓ Please collect your cash: ${amount:.2f}")
                        print(f"Remaining Balance: ${balance:.2f}")
                    else:
                        print(f"✗ Insufficient Balance. Available: ${balance:.2f}")
                except ValueError:
                    print("✗ Invalid amount entered")
    
            elif choice == '4':
                new_pin = input("Enter new PIN: ")
                if len(new_pin) >= 4 and new_pin.isdigit():
                    pin = new_pin
                    print("✓ PIN changed successfully")
                else:
                    print("✗ PIN must be at least 4 digits")
    
            elif choice == '5':
                print(f"\n Thank you for using ATM, {username}")
                break
    
            else:
                print("✗ Invalid Choice. Please try again")
    
    else:
        print("\n✗ Wrong PIN - Access Denied")


if __name__ == '__main__':
    username = input("Enter username: ").strip()
    if username:
        run(username)
    else:
        print("✗ Username cannot be empty")
