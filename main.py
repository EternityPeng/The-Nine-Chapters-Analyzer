from app import create_app
import webbrowser
#自动全屏
#import pyautogui

app = create_app()

    
if __name__ == "__main__":
    #this is to open the browser automatically
    webbrowser.open_new('http://127.0.0.1:8080/user/homepage')
    #pyautogui.sleep(2)
    #pyautogui.hotkey('f11')
    #run our application
    # app.run(debug=False, host='127.0.0.1', port=8080)
    app.run(debug=False, host='0.0.0.0', port=8080)