import ctypes
import os
import shutil
import time
import winreg
import glob

def get_reg_value(path, name, hive=winreg.HKEY_CURRENT_USER):
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except:
        return None

def set_reg_value(path, name, value, hive=winreg.HKEY_CURRENT_USER, value_type=winreg.REG_SZ):
    try:
        winreg.CreateKey(hive, path)
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, name, 0, value_type, value)
        winreg.CloseKey(key)
        print(f"Set Registry: {path}\\{name} = {value}")
        return True
    except Exception as e:
        print(f"Error setting registry {name}: {e}")
        return False

def find_local_image():
    # Look in the folder above 'scripts' (the project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    for ext in extensions:
        files = glob.glob(os.path.join(base_dir, ext))
        if files:
            return files[0]
    return None

def set_wallpaper(image_path):
    if not image_path:
        print("No image found.")
        return

    print(f"Applying wallpaper: {image_path}")
    
    # 1. Registry (WallPaper)
    set_reg_value(r"Control Panel\Desktop", "Wallpaper", image_path)
    set_reg_value(r"Control Panel\Desktop", "WallpaperStyle", "10") # Fill

    # 2. TranscodedWallpaper (The Cache / GPO Bypass)
    appdata = os.environ['APPDATA']
    transcoded_path = os.path.join(appdata, r"Microsoft\Windows\Themes\TranscodedWallpaper")
    
    # Try to overwrite the cache file directly
    try:
        # Clear permissions if needed (simple try)
        if os.path.exists(transcoded_path):
            os.chmod(transcoded_path, 0o777)
        
        # Copy file
        shutil.copyfile(image_path, transcoded_path)
        print(f"Overwrote TranscodedWallpaper cache at {transcoded_path}")
    except Exception as e:
        print(f"Failed to overwrite TranscodedWallpaper: {e}")

    # 3. SPI Call
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    
    # Force refresh
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 0)

if __name__ == "__main__":
    img = find_local_image()
    if img:
        set_wallpaper(img)
    else:
        print("Kein Bild gefunden! Bitte lege ein JPG/PNG in den Ordner WAK-Desktop-fixes.")
        # Only pause if run interactively (not easy to detect perfect, but good enough)
        # We don't pause here to avoid hanging autostart
