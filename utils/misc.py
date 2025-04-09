from shutil import rmtree

def remove_directory(dirPath):
    try:
        rmtree(dirPath, ignore_errors=True)
    except:
        return None