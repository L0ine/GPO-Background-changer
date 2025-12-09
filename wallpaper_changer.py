import ctypes
import os
import argparse
import sys
import time
import winreg

def get_reg_value(key_path, value_name, hive=winreg.HKEY_CURRENT_USER):
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None
    except Exception as e:
        return str(e)

def set_reg_value(key_path, value_name, value, hive=winreg.HKEY_CURRENT_USER, reg_type=winreg.REG_SZ):
    try:
        key = winreg.CreateKey(hive, key_path)
        winreg.SetValueEx(key, value_name, 0, reg_type, value)
        winreg.CloseKey(key)
        print(f"[OK] Registry key set: {key_path}\\{value_name} = {value}")
        return True
    except Exception as e:
        print(f"[ERR] Failed to set registry {key_path}\\{value_name}: {e}")
        return False

def check_gpo():
    print("\n--- Diagnostic: Checking GPO/Registry ---")
    u_pol = get_reg_value(r"Software\Policies\Microsoft\Windows\System", "Wallpaper")
    print(f"User Policy (HKCU): {u_pol}")
    m_pol = get_reg_value(r"Software\Policies\Microsoft\Windows\System", "Wallpaper", winreg.HKEY_LOCAL_MACHINE)
    print(f"Machine Policy (HKLM): {m_pol}")
    return u_pol, m_pol

def restart_explorer():
    print("Restarting Explorer to force update...")
    os.system("taskkill /f /im explorer.exe")
    time.sleep(1)
    os.system("start explorer.exe")

def set_wallpaper(path, force_restart=False):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return False
        
    abs_path = os.path.abspath(path)
    print(f"Target Wallpaper: {abs_path}")
    
    # --- BRUTE FORCE STRATEGY ---
    appdata = os.getenv('APPDATA')
    if appdata:
        themes_path = os.path.join(appdata, r"Microsoft\Windows\Themes")
        if not os.path.exists(themes_path):
            os.makedirs(themes_path)
            
        transcoded_file = os.path.join(themes_path, "TranscodedWallpaper")
        
        try:
            with open(abs_path, 'rb') as src:
                data = src.read()
            if os.path.exists(transcoded_file):
                try:
                    os.chmod(transcoded_file, 0o777)
                    os.system(f'attrib -r "{transcoded_file}"')
                except:
                    pass
            with open(transcoded_file, 'wb') as dst:
                dst.write(data)
            print("[SUCCESS] TranscodedWallpaper overwritten.")
        except Exception as e:
            print(f"[ERROR] Could not overwrite TranscodedWallpaper: {e}")

    # Registry Settings
    u_pol, m_pol = check_gpo()
    if u_pol:
        set_reg_value(r"Software\Policies\Microsoft\Windows\System", "Wallpaper", abs_path)
    set_reg_value(r"Control Panel\Desktop", "Wallpaper", abs_path)
    set_reg_value(r"Control Panel\Desktop", "WallpaperStyle", "10") # Fill
    set_reg_value(r"Control Panel\Desktop", "TileWallpaper", "0")

    # API Call
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    
    try:
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        # Broadcast setting change
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, 0)
        
        if force_restart:
            restart_explorer()
        return True
    except Exception as e:
        print(f"Exception during API call: {e}")
        return False

def find_local_image():
    exts = ['.jpg', '.jpeg', '.png', '.bmp']
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir) # Check one level up (project root)
    
    # Check project root first (where run.bat is)
    if os.path.exists(root_dir):
        for file in os.listdir(root_dir):
            base, ext = os.path.splitext(file)
            if ext.lower() in exts:
                return os.path.join(root_dir, file)

    # Check script dir
    for file in os.listdir(script_dir):
        base, ext = os.path.splitext(file)
        if ext.lower() in exts:
            return os.path.join(script_dir, file)
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", nargs='?', help="Path to image")
    parser.add_argument("--loop", type=int, default=0, help="Loop interval")
    parser.add_argument("--restart-explorer", action="store_true", help="Force restart")
    
    args = parser.parse_args()
    image_path = args.image_path
    
    if not image_path:
        image_path = find_local_image()
        if not image_path:
            return # Silent exit if no image found

    if args.loop > 0:
        try:
            while True:
                set_wallpaper(image_path, args.restart_explorer)
                time.sleep(args.loop)
        except KeyboardInterrupt:
            pass
    else:
        set_wallpaper(image_path, args.restart_explorer)

if __name__ == "__main__":
    main()
