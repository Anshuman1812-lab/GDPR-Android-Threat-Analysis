from UIAutomator import UIAutomator

# Make sure to have an app open with the google login option on screen

def main():
    logged_in = UIAutomator.google_login()

    if logged_in:
        print('Logged In!')
    else:
        print('Not Logged In!')

if __name__=="__main__":
    main()