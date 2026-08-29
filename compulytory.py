import os
import sys
import subprocess
import shutil
from pathlib import Path
import time
import json

# =============================================
# НАСТРОЙКИ
# =============================================
WATCH_FOLDER = r"C:\Users\SoftFire\Desktop\reserch"
OUTPUT_FOLDER = os.path.join(WATCH_FOLDER, "compiled_exe")
ICON_PATH = r"C:\Users\SoftFire\Desktop\reserch\icon.png"

# Выбор компилятора: 'pyinstaller' или 'nuitka'
COMPILER = 'pyinstaller'  # По умолчанию PyInstaller

# =============================================
# ПРОВЕРКА НАЛИЧИЯ КОМПИЛЯТОРОВ
# =============================================
def check_pyinstaller():
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                               capture_output=True, 
                               check=False,
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return result.returncode == 0
    except:
        return False

def check_nuitka():
    try:
        result = subprocess.run(['nuitka', '--version'], 
                               capture_output=True, 
                               check=False,
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return result.returncode == 0
    except:
        return False

def install_nuitka():
    print("[*] Устанавливаю Nuitka...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=False)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'nuitka', '--user'], check=True)
        print("[✓] Nuitka установлен!")
        return True
    except Exception as e:
        print(f"[✗] Ошибка установки Nuitka: {e}")
        return False

def install_pyinstaller():
    print("[*] Устанавливаю PyInstaller...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--user'], check=True)
        print("[✓] PyInstaller установлен!")
        return True
    except Exception as e:
        print(f"[✗] Ошибка установки: {e}")
        return False

# =============================================
# КОНВЕРТАЦИЯ PNG В ICO
# =============================================
def convert_png_to_ico():
    """Конвертирует PNG в ICO с помощью PIL"""
    try:
        from PIL import Image
        ico_path = os.path.join(WATCH_FOLDER, "icon.ico")
        img = Image.open(ICON_PATH)
        img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"[✓] Иконка сконвертирована: {ico_path}")
        return ico_path
    except ImportError:
        print("[!] PIL не установлен. Устанавливаю...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow', '--user'], check=True)
        try:
            from PIL import Image
            ico_path = os.path.join(WATCH_FOLDER, "icon.ico")
            img = Image.open(ICON_PATH)
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"[✓] Иконка сконвертирована: {ico_path}")
            return ico_path
        except:
            print("[✗] Не удалось конвертировать иконку")
            return None
    except Exception as e:
        print(f"[✗] Ошибка конвертации иконки: {e}")
        return None

# =============================================
# КОМПИЛЯЦИЯ ЧЕРЕЗ NUITKA
# =============================================
def compile_nuitka(py_file_path):
    """Компилирует .py файл через Nuitka"""
    try:
        if not os.path.exists(py_file_path):
            print(f"[✗] Файл не найден: {py_file_path}")
            return False
        
        filename = os.path.basename(py_file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"\n[*] Компиляция Nuitka: {filename}")
        
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
        
        # Конвертируем иконку
        ico_path = convert_png_to_ico() if os.path.exists(ICON_PATH) else None
        
        # Команда для Nuitka
        cmd = [
            'python', '-m', 'nuitka',
            '--standalone',
            '--onefile',
            '--windows-disable-console',
            f'--output-dir={OUTPUT_FOLDER}',
            f'--output-filename={name_without_ext}.exe'
        ]
        
        # Добавляем иконку если есть
        if ico_path and os.path.exists(ico_path):
            cmd.append(f'--windows-icon-from-ico={ico_path}')
        
        # Добавляем файл
        cmd.append(py_file_path)
        
        # Запускаем компиляцию
        print(f"[*] Команда: {' '.join(cmd)}")
        print("[*] Это может занять несколько минут...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if result.returncode == 0:
            exe_file = os.path.join(OUTPUT_FOLDER, f"{name_without_ext}.exe")
            if os.path.exists(exe_file):
                print(f"[✓] УСПЕШНО! {filename} -> {exe_file}")
                return True
            else:
                print(f"[✗] .exe не создан: {exe_file}")
                return False
        else:
            print(f"[✗] Ошибка компиляции Nuitka:")
            if result.stderr:
                print(f"    {result.stderr[:500]}")
            return False
            
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        return False

# =============================================
# КОМПИЛЯЦИЯ ЧЕРЕЗ PYINSTALLER (С ИКОНКОЙ)
# =============================================
def compile_pyinstaller(py_file_path):
    """Компилирует .py файл через PyInstaller с иконкой"""
    try:
        if not os.path.exists(py_file_path):
            print(f"[✗] Файл не найден: {py_file_path}")
            return False
        
        filename = os.path.basename(py_file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"\n[*] Компиляция PyInstaller: {filename}")
        
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
        
        # Конвертируем иконку
        ico_path = convert_png_to_ico() if os.path.exists(ICON_PATH) else None
        
        # Команда для PyInstaller
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            f'--distpath={OUTPUT_FOLDER}',
            f'--workpath={os.path.join(WATCH_FOLDER, "build_temp")}',
            f'--specpath={os.path.join(WATCH_FOLDER, "build_temp")}',
            '--noconfirm',
            '--noupx',
        ]
        
        if ico_path and os.path.exists(ico_path):
            cmd.append(f'--icon={ico_path}')
        
        cmd.append(py_file_path)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if result.returncode == 0:
            exe_file = os.path.join(OUTPUT_FOLDER, f"{name_without_ext}.exe")
            if os.path.exists(exe_file):
                print(f"[✓] УСПЕШНО! {filename} -> {exe_file}")
                cleanup_temp_files()
                return True
            else:
                print(f"[✗] .exe не создан: {exe_file}")
                return False
        else:
            print(f"[✗] Ошибка компиляции PyInstaller:")
            if result.stderr:
                print(f"    {result.stderr[:500]}")
            return False
            
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        return False

# =============================================
# КОМПИЛЯЦИЯ ОТДЕЛЬНОГО ФАЙЛА
# =============================================
def compile_single_file(py_file_path):
    """Компилирует один .py файл выбранным компилятором"""
    
    if COMPILER == 'nuitka':
        if not check_nuitka():
            print("[!] Nuitka не найден!")
            if install_nuitka():
                print("[✓] Nuitka установлен!")
            else:
                print("[✗] Не удалось установить Nuitka")
                return False
        return compile_nuitka(py_file_path)
    else:
        if not check_pyinstaller():
            print("[!] PyInstaller не найден!")
            if install_pyinstaller():
                print("[✓] PyInstaller установлен!")
            else:
                print("[✗] Не удалось установить PyInstaller")
                return False
        return compile_pyinstaller(py_file_path)

# =============================================
# ОЧИСТКА ВРЕМЕННЫХ ФАЙЛОВ
# =============================================
def cleanup_temp_files():
    try:
        temp_folders = ['build_temp', '__pycache__', 'dist']
        for folder in temp_folders:
            folder_path = os.path.join(WATCH_FOLDER, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        
        for file in os.listdir(WATCH_FOLDER):
            if file.endswith('.spec'):
                os.remove(os.path.join(WATCH_FOLDER, file))
    except:
        pass

# =============================================
# ПОИСК .PY ФАЙЛОВ
# =============================================
def find_py_files():
    py_files = []
    exclude_dirs = ['build_temp', '__pycache__', 'dist', 'compiled_exe']
    
    for root, dirs, files in os.walk(WATCH_FOLDER):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                py_files.append(full_path)
    
    return py_files

# =============================================
# КОМПИЛЯЦИЯ ВСЕХ ФАЙЛОВ
# =============================================
def compile_all():
    print("\n" + "="*70)
    print(f"  📦 КОМПИЛЯТОР PYTHON -> EXE ({COMPILER.upper()})")
    print(f"  📁 Папка: {WATCH_FOLDER}")
    print("="*70 + "\n")
    
    if not os.path.exists(WATCH_FOLDER):
        print(f"[✗] Папка не найдена: {WATCH_FOLDER}")
        return
    
    py_files = find_py_files()
    script_name = os.path.basename(__file__)
    py_files = [f for f in py_files if os.path.basename(f) != script_name]
    
    if not py_files:
        print("[!] .py файлов не найдено!")
        return
    
    print(f"[*] Найдено .py файлов: {len(py_files)}")
    print("="*70 + "\n")
    
    success = 0
    errors = 0
    
    for py_file in py_files:
        filename = os.path.basename(py_file)
        exe_file = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + '.exe')
        
        if os.path.exists(exe_file):
            py_mtime = os.path.getmtime(py_file)
            exe_mtime = os.path.getmtime(exe_file)
            if exe_mtime > py_mtime:
                print(f"[ ] Пропущено (уже есть .exe): {filename}")
                continue
            else:
                print(f"[*] Файл изменён, перекомпиляция: {filename}")
        
        if compile_single_file(py_file):
            success += 1
        else:
            errors += 1
        
        time.sleep(0.5)
    
    print("\n" + "="*70)
    print("  📊 РЕЗУЛЬТАТЫ")
    print("="*70)
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибок: {errors}")
    print(f"📁 .exe файлы в: {OUTPUT_FOLDER}")
    print("="*70)
    
    if success > 0:
        try:
            os.startfile(OUTPUT_FOLDER)
        except:
            pass

# =============================================
# ПЕРЕКЛЮЧЕНИЕ КОМПИЛЯТОРА
# =============================================
def switch_compiler():
    """Переключает компилятор между PyInstaller и Nuitka"""
    global COMPILER
    if COMPILER == 'pyinstaller':
        COMPILER = 'nuitka'
        print("[✓] Компилятор переключён на: NUITKA")
    else:
        COMPILER = 'pyinstaller'
        print("[✓] Компилятор переключён на: PYINSTALLER")

# =============================================
# ГЛАВНОЕ МЕНЮ
# =============================================
def main():
    while True:
        print("\n" + "="*70)
        print(f"  🔧 КОМПИЛЯТОР PYTHON -> EXE")
        print(f"  📁 Папка: {WATCH_FOLDER}")
        print(f"  🛠️  Компилятор: {COMPILER.upper()}")
        print("="*70)
        print("1. Скомпилировать все .py файлы")
        print("2. Скомпилировать конкретный .py файл")
        print("3. Очистить временные файлы")
        print("4. Открыть папку с результатами")
        print("5. Переключить компилятор")
        print("6. Выход")
        print("="*70)
        
        choice = input("\nВыберите действие (1-6): ").strip()
        
        if choice == '1':
            compile_all()
        elif choice == '2':
            compile_specific_file()
        elif choice == '3':
            cleanup_temp_files()
            print("[✓] Очистка завершена!")
        elif choice == '4':
            if os.path.exists(OUTPUT_FOLDER):
                os.startfile(OUTPUT_FOLDER)
            else:
                print("[!] Папка с результатами не найдена")
        elif choice == '5':
            switch_compiler()
        elif choice == '6':
            print("[✓] Выход")
            break
        else:
            print("[!] Неверный выбор!")

def compile_specific_file():
    py_files = find_py_files()
    script_name = os.path.basename(__file__)
    py_files = [f for f in py_files if os.path.basename(f) != script_name]
    
    if not py_files:
        print("[!] .py файлов не найдено!")
        return
    
    print("\nНайденные .py файлы:")
    for i, file in enumerate(py_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
    
    try:
        choice = int(input("\nВыберите номер файла: ")) - 1
        if 0 <= choice < len(py_files):
            compile_single_file(py_files[choice])
        else:
            print("[!] Неверный номер!")
    except:
        print("[!] Введите число!")

# =============================================
# ЗАПУСК
# =============================================
if __name__ == "__main__":
    try:
        # Проверяем наличие Pillow для конвертации иконок
        try:
            import PIL
        except ImportError:
            print("[*] Устанавливаю Pillow для работы с иконками...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow', '--user'], check=False)
        
        main()
    except KeyboardInterrupt:
        print("\n[!] Программа остановлена")
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nНажмите Enter для выхода...")
        input()