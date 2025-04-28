# setup.py (in psy_request/)
from setuptools import setup

APP = ['app.py']
DATA_FILES = ['functions']
OPTIONS = {
    'argv_emulation': True,
    'includes': ['streamlit'],
    'packages': [
        'functions',
        'pydantic',
        'langchain',
        'openai',
        'python_docx',
    ],
    'excludes': [
        'modulegraph',
        'PyInstaller',
        'PyQt5',
        'PySide2',
    ],
    'plist': {
        'CFBundleName': 'PsychotherapieAntrag',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)