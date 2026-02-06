import PyInstaller.__main__
import os
import shutil

# Clean up previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("Starting Build Process...")

PyInstaller.__main__.run([
    'app.py',
    '--name=BillingApp',
    '--onefile',
    '--clean',
    '--noconsole',  # Hide console window
    '--icon=assets/icon.ico', # Add Icon
    '--collect-all=ttkbootstrap', # Important for themes
    '--hidden-import=pkg_resources.py2_warn', # Sometimes needed
    '--add-data=ui;ui', # Add UI package if needed as data, though import usually works
    # We generally don't bundle 'data' folder as it should be created on run
    # We do need exports and logs folder to exist, or app should create them (app does create them)
])

print("Build Complete. Check 'dist' folder.")
