import os
from time import sleep
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from services.file_service import save_data_to_file, load_data_from_file
from services.encryption_service import encrypt, decrypt

console = Console()


def add_password(password_object, acc_list):
    new_list = acc_list.copy()
    new_list.append(password_object)
    return new_list


def prompt_add_password():
    website_name = Prompt.ask("Enter website name").lower()
    username = Prompt.ask("Enter username for {}".format(website_name))
    password = Prompt.ask("Enter password")
    return {"website_name": website_name, "username": username, "password": password}


def handle_add_account(acc_list, master_password):
    account_object = prompt_add_password()
    new_acc_list = add_password(account_object, acc_list)
    save_account_list(new_acc_list, master_password)
    console.print("Your new account and password have been saved \n")
    console.print("Returning...")
    return new_acc_list



def load_account_list(password):
    """Load the account list from the encrypted vault"""
    ciphered_data = load_data_from_file("./ciphered_vault")
    return decrypt(ciphered_data, password)


def save_account_list(acc_list, password):
    """Save the account list in the encrypted vault"""
    ciphered_list = encrypt(acc_list, password)
    save_data_to_file("./ciphered_vault", ciphered_list)


def handle_login_existing_account():
    password = input("Enter your master password: ")
    console.print("")

    # Try and decipher the vault to check master password
    try:
        acc_list = load_account_list(password)
        return acc_list, password
    except Exception:
        console.print("WRONG PASSWORD !\n")
        exit(1)


def handle_register_new_account():
    console.print("This is a new account !\n")
    password = Prompt.ask("Please enter a master password")
    console.print("")
    save_account_list([], password)
    return [], password

def prompt_account_name():
    account_name=Prompt.ask("Enter account website name").lower()
    console.print("\n")
    return account_name

def handle_show_account(acc_list):
    account_name=prompt_account_name()

    selected_accounts=[account for account in acc_list if account["website_name"] == account_name]
    if selected_accounts==[]:
        console.print("No accounts were found matching this website name!")
    else:
        print_accounts(selected_accounts)

def delete_account_from_list(acc_list,acc_name):
    return [account for account in acc_list if account["website_name"] !=acc_name]

def handle_delete_account(acc_list,password):

    nbr_accounts = len(acc_list)
    account_name = prompt_account_name()

    acc_list=delete_account_from_list(acc_list,account_name)

    if len(acc_list) == nbr_accounts:
        console.print("No accounts were found matching this website name!")
    else:
        save_account_list(acc_list, password)
        console.print("Account {} successfully deleted from vault".format(account_name))

    return acc_list


def handle_exit():
    console.print("Quitting...")
    quit()

def handle_delete_all_accounts(password):
    save_account_list([],password)
    return []

def handle_reused_passwords(acc_list):
    p_list=[account['password'] for account in acc_list]
    usedp_list=[]
    res=[]
    for password in p_list:
        if not (password in usedp_list):
            usedp_list.append(password)
            l=[account['website_name'] for account in acc_list if account['password']==password]
            if len(l)>=2:
                res.append(l)

    console.print(res)

def show_options():
    table = Table(title="Options")

    table.add_column("Option", style="cyan")
    table.add_column("Name", style="magenta")

    # adding the rows
    table.add_row("1", "Store new website account")
    table.add_row("2", "Retrieve website account")
    table.add_row("3", "Delete website account")
    table.add_row("4", "Quit the program")
    table.add_row("5", "Show all saved accounts")
    table.add_row("6", "Delete everything")
    table.add_row("7", "Show reused passwords")

    console.print(table, justify="center")

def print_accounts(acc_list):
    table = Table(title="Accounts")

    table.add_column("Website name", style="cyan")
    table.add_column("Username", style="red")
    table.add_column("Password", style="magenta")
    for acc in acc_list:
        table.add_row(acc['website_name'],acc['username'],acc['password'])
    console.print(table, justify="center")


def main():
    files = os.listdir()
    console.clear()
    console.print("[blue underline]WELCOME TO PASSKEEP", justify="center")

    # Account already exists
    if "ciphered_vault" in files:
       account_list, master_password = handle_login_existing_account()

    # Account creation phase
    else:
       account_list, master_password = handle_register_new_account()

    while True:
        console.rule()

        show_options()

        option = Prompt.ask("What do you want to do ? ")

        if option == "1":
           account_list = handle_add_account(account_list, master_password)
        elif option == "2":
            handle_show_account(account_list)

        elif option == "3":
           account_list=handle_delete_account(account_list,master_password)

        elif option == "4":
            handle_exit()
        elif option == "5":
            #console.print(account_list)
            print_accounts(account_list)
        elif option == "6":
            account_list=handle_delete_all_accounts(master_password)
        elif option=="7":
            handle_reused_passwords(account_list)
        else:
            print("Invalid command...")
            print("Restarting...")
            sleep(1)


if __name__ == "__main__":
    main()
