from UIAutomator import UIAutomator

def main():
    logged_in = UIAutomator.playstore_login()
    if logged_in:
        print('Logged In!')
    else:
        print('Not Logged In!')

if __name__=="__main__":
    main()