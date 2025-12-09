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
    set_reg_value(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarGlomLevel", 0)

    # 3. Disable GPO lock if possible
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", 0, winreg.KEY_ALL_ACCESS)
        try:
            winreg.DeleteValue(key, "TaskbarLockAll")
        except:
            pass
        winreg.CloseKey(key)
    except:
        pass

    # Broadcast change - often needs explorer restart but we try without as requested
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, 0)
    print("Taskbar settings applied.")

if __name__ == "__main__":
    main()
