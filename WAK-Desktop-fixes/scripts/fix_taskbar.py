import winreg
import os
import time
import ctypes

def set_reg_value(key_path, value_name, value, hive=winreg.HKEY_CURRENT_USER, reg_type=winreg.REG_DWORD):
    try:
        key = winreg.CreateKey(hive, key_path)
        winreg.SetValueEx(key, value_name, 0, reg_type, value)
        winreg.CloseKey(key)
        print(f"[OK] {key_path}\\{value_name} = {value}")
        return True
    except Exception as e:
        print(f"[ERR] Failed to set {value_name}: {e}")
        return False

def main():
    # 1. Center Taskbar
    set_reg_value(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", 1)
    
    # 2. Combine Taskbar Buttons / Hide Labels
    # HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
    # TaskbarGlomLevel: 0 = Always combine, hide labels
    #                   1 = Combine when full
    #                   2 = Never combine (shows labels)
    print("Forcing TaskbarGlomLevel to 0 (Always Combine)...")
    set_reg_value(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarGlomLevel", 0)
    
    # Also set MMTaskbarGlomLevel for multi-monitor setups just in case
    set_reg_value(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "MMTaskbarGlomLevel", 0)

    # 3. Disable GPO lock if possible
    # We must look in HKCU\Software\Policies\Microsoft\Windows\Explorer
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", 0, winreg.KEY_ALL_ACCESS)
        
        # List of annoying policies to delete
        policies_to_kill = ["TaskbarLockAll", "TaskbarGlomLevel", "NoTaskGrouping", "LockTaskbar"]
        
        for pol in policies_to_kill:
            try:
                winreg.DeleteValue(key, pol)
                print(f"[OK] Deleted Policy: {pol}")
            except FileNotFoundError:
                pass # Key didn't exist, good
            except Exception as e:
                print(f"[ERR] Could not delete Policy {pol}: {e}")
                
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Could not open Policies key (might not exist): {e}")

    # Verify the value
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "TaskbarGlomLevel")
        print(f"[CHECK] TaskbarGlomLevel is now: {val}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[CHECK] Could not read back TaskbarGlomLevel: {e}")

    # Broadcast change
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, 0)
    
    print("Restarting Explorer (hard)...")
    os.system("taskkill /f /im explorer.exe")
    time.sleep(2)
    # Use Popen to detach properly or just simple start
    os.system("start explorer.exe") 
    
    print("Done. If taskbar is missing, press Win+R and type 'explorer.exe'")

if __name__ == "__main__":
    main()
