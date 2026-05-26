import os
import sys
import subprocess

# Перевіряємо, чи ми всередині Unreal Engine
try:
    import unreal
    IN_UNREAL = True
except ImportError:
    IN_UNREAL = False

def get_blueprint_structures():
    """Збирає інформацію про Блупрінти (змінні, функції, класи) через Unreal API"""
    bp_context = []
    if not IN_UNREAL:
        return ""

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    # Шукаємо всі Блупрінти в папці Game (Content)
    asset_data_list = asset_registry.get_assets_by_path("/Game", recursive=True)
    
    bp_context.append("=== UNREAL BLUEPRINT STRUCTURES ===")
    
    for asset_data in asset_data_list:
        # Відфільтровуємо лише Блупрінти (включаючи AnimBP)
        if asset_data.asset_class_path.asset_name in ["Blueprint", "AnimBlueprint"]:
            bp_name = asset_data.asset_name
            bp_path = asset_data.package_name
            
            bp_context.append(f"\nBlueprint: {bp_name} ({bp_path})")
            
            try:
                # Завантажуємо ассет для аналізу об'єкта
                bp_generated_class = unreal.EditorAssetLibrary.load_blueprint_class(str(bp_path))
                if bp_generated_class:
                    default_obj = unreal.get_default_object(bp_generated_class)
                    
                    # 1. Збираємо змінні (Properties)
                    bp_context.append("  Properties:")
                    for prop in bp_generated_class.get_editor_property("property_names"):
                        try:
                            val = default_obj.get_editor_property(prop)
                            bp_context.append(f"    - {prop} (Default Value: {val})")
                        except Exception:
                            bp_context.append(f"    - {prop}")
                            
                    # 2. Збираємо функції (Functions)
                    bp_context.append("  Functions/Functions Names:")
                    for func in bp_generated_class.get_editor_property("function_names"):
                        bp_context.append(f"    - {func}")
            except Exception as e:
                bp_context.append(f"  (Could not read details: {str(e)})")
                
    return "\n".join(bp_context)

def get_cpp_context(root_dir):
    """Збирає текст з усіх C++ та конфіг файлів"""
    allowed_extensions = ('.h', '.cpp', '.cs', '.ini')
    context = []
    
    for folder in ['Source', 'Config']:
        full_path = os.path.join(root_dir, folder)
        if not os.path.exists(full_path):
            continue
            
        for root, dirs, files in os.walk(full_path):
            if 'Intermediate' in root or 'Binaries' in root:
                continue
            for file in files:
                if file.endswith(allowed_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            relative_path = os.path.relpath(file_path, root_dir)
                            context.append(f"--- FILE: {relative_path} ---\n{f.read()}\n")
                    except Exception:
                        pass
    return "\n".join(context)

def start_interactive_chat(context_data):
    """Ця частина запускається в ОКРЕМОМУ вікні cmd для спілкування з Gemini"""
    from google import genai
    from google.genai import types

    print("[VibeCoding] Контекст проекту отримано. Ініціалізую Gemini...")
    
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Помилка ініціалізації клієнта: {e}. Перевірте змінну GEMINI_API_KEY.")
        input("Натисніть Enter для виходу...")
        return

    system_instruction = (
        "Ти — AI-напарник для вайбкодінгу в Unreal Engine. Тобі надано структуру Блупрінтів "
        "(змінні, функції) та весь вихідний код C++/Config проекту. "
        "Допомагай писати код, зв'язувати C++ з Блупрінтами та вирішувати архітектурні та анімаційні задачі."
    )

    chat = client.chats.create(
        model="gemini-1.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )
    )

    print("\n--- GEMINI ВАЙБКОДІНГ АКТИВОВАНО ---")
    print("Я бачу твої C++ файли та структуру Блупрінтів (змінні/функції)!")
    print("Задавай питання (для виходу напиши 'exit'):\n")

    # Передаємо весь згенерований гіга-контекст першим повідомленням
    chat.send_message(f"Ось поточний стан мого проекту (C++ та Блупрінти):\n\n{context_data}\n\nПроаналізуй його і коротко напиши 'Я готовий до вайбкодінгу!'")

    while True:
        user_input = input("User > ")
        if user_input.lower() in ['exit', 'quit']:
            break
        if not user_input.strip():
            continue

        response = chat.send_message(user_input)
        print(f"\nGemini > {response.text}\n")

if __name__ == "__main__":
    # Якщо скрипт викликано всередині Unreal Engine (через ноду Execute Python Command)
    if IN_UNREAL:
        project_root = unreal.Paths.project_dir()
        project_root = os.path.abspath(project_root)
        
        # 1. Збираємо C++ контекст
        cpp_ctx = get_cpp_context(project_root)
        # 2. Збираємо Blueprint контекст через Unreal API
        bp_ctx = get_blueprint_structures()
        
        full_context = f"{cpp_ctx}\n\n{bp_ctx}"
        
        # Зберігаємо тимчасовий файл з контекстом, щоб передати його в нове вікно cmd
        temp_path = os.path.join(unreal.Paths.project_saved_dir(), "vibe_context.tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(full_context)
            
        # Запускаємо цей же скрипт, але вже в окремому вікні консолі Windows
        script_path = os.path.abspath(__file__)
        subprocess.Popen(
            f'start cmd /k "python \\"{script_path}\\" --chat"', 
            shell=True,
            cwd=os.path.dirname(script_path)
        )
        
    # Якщо скрипт запущено в окремому вікні консолі (параметр --chat)
    elif len(sys.argv) > 1 and sys.argv[1] == "--chat":
        # Шукаємо тимчасовий файл з контекстом у папці Saved проекту
        # Оскільки ми в папці Content/GeminiVibe, піднімаємось на рівень проекту
        script_dir = os.path.dirname(os.path.abspath(__file__))
        saved_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "Saved"))
        temp_path = os.path.join(saved_dir, "vibe_context.tmp")
        
        if os.path.exists(temp_path):
            with open(temp_path, 'r', encoding='utf-8') as f:
                full_context = f.read()
            # Видаляємо тимчасовий файл після зчитування
            try: os.remove(temp_path) 
            except: pass
        else:
            full_context = "Не вдалося завантажити контекст автоматично."

        start_interactive_chat(full_context)