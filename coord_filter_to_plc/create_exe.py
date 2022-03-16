import PyInstaller.__main__

PyInstaller.__main__.run([
    './main.py',
    '--name=Filtro de Coordenadas',
    # '--noconsole',
    '--noconfirm',
    '--specpath=dist',
    "--add-data=../assets/rn.ico;assets/",
    "--add-data=../assets/rn.ico;.",
])
