import threading
import subprocess
import time

def init_db():
    subprocess.run(["python3", "src/rag/new_chromadb.py"])

def run_app():
    subprocess.run(["streamlit", "run", "src/streamapp.py"])
    
if __name__ == "__main__":
    # subprocess.run(["python3", "-m", "pip", "install", "--no-cache-dir", "-r", "requirements.txt"], check=True)
    db_thread = threading.Thread(target=init_db)
    streamlit_thread = threading.Thread(target=run_app)
    db_thread.start()
    time.sleep(5)
    streamlit_thread.start()
    db_thread.join()
    streamlit_thread.join()