import os
import time
import webbrowser

# Перейти в папку, где лежит проект
os.chdir("C:/Users/user/desktop/hydro_project")

# Запустить streamlit run
os.system("start cmd /c streamlit run hydro_app.py")

# Подождать 3 секунды и открыть браузер
time.sleep(3)
webbrowser.open("http://localhost:8501")

