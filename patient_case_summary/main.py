import os
import sys
sys.path.append(os.getcwd())
import subprocess
CURRENT_PATH = os.getcwd()
STREAMLIT_PATH = os.path.join(CURRENT_PATH, "streamlit.py")


if __name__=="__main__":
    #asyncio.run(main())
    subprocess.run(["streamlit", "run", STREAMLIT_PATH])