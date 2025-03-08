import time
import requests
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style, Back

# Inicializar colorama
init()

# Limpiar pantalla según sistema operativo
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Tema de colores - Estilo minimalista
class Theme:
    PRIMARY = Fore.CYAN
    SECONDARY = Fore.BLUE
    ACCENT = Fore.MAGENTA
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    INFO = Fore.WHITE
    TITLE = Fore.CYAN + Style.BRIGHT
    SUBTITLE = Fore.BLUE + Style.BRIGHT
    INPUT = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL
    HIGHLIGHT = Back.CYAN + Fore.BLACK

# Monedas soportadas con símbolos
CURRENCIES = {
    "CRC": {"name": "Colones", "symbol": "₡"},
    "USD": {"name": "Dólares", "symbol": "$"},
    "EUR": {"name": "Euros", "symbol": "€"}
}

# Obtener tasas de cambio desde exchangerate-api
def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        return data["rates"][to_currency]
    except:
        print(Theme.ERROR + "⚠ Error: No se pudo obtener tasas de cambio. Usando 1:1 como fallback." + Theme.RESET)
        return 1.0

# Función para convertir monto
def convert_amount(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate

# Función para mostrar líneas separadoras
def print_separator_double(color=Theme.PRIMARY):
    print(color + "═" * 60 + Theme.RESET)

def print_separator_single(color=Theme.PRIMARY):
    print(color + "─" * 60 + Theme.RESET)

# Efecto de carga con mejor diseño
def loading_effect(text, duration=1.0):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    iterations = int(duration * 10)
    
    print(Theme.INFO + text + " ", end="", flush=True)
    for i in range(iterations):
        print(f"\r{Theme.INFO}{text} {Theme.ACCENT}{chars[i % len(chars)]}", end="", flush=True)
        time.sleep(duration / iterations)
    print(f"\r{Theme.INFO}{text} {Theme.SUCCESS}✓{Theme.RESET}")
    time.sleep(0.3)

# Mostrar título
def show_title(title, subtitle=None):
    print("\n" + Theme.TITLE + f" {title} ".center(60, "═") + Theme.RESET)
    if subtitle:
        print(Theme.SUBTITLE + subtitle.center(60) + Theme.RESET)

# Función para entrada con validación
def get_input(prompt, validator=None, error_msg=None, default=None):
    while True:
        print(Theme.INFO + prompt, end="")
        value = input(Theme.INPUT)
        print(Theme.RESET, end="")
        
        if value == "" and default is not None:
            return default
        
        if validator is None or validator(value):
            return value
        
        print(Theme.ERROR + f"⚠ {error_msg}" + Theme.RESET)

# Validadores
def validate_currency(value):
    return value.upper() in CURRENCIES

def validate_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_int_range(min_val, max_val):
    def validator(value):
        try:
            val = int(value)
            return min_val <= val <= max_val
        except ValueError:
            return False
    return validator

# Progreso de pasos
def show_progress(current, total):
    width = 30
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    print(f"\n{Theme.PRIMARY}Progreso: {current}/{total} [{Theme.ACCENT}{bar}{Theme.PRIMARY}]{Theme.RESET}")

# Inicio del programa
clear_screen()
show_title("GESTOR DE PRESUPUESTO DE BECA")
loading_effect("Iniciando aplicación", 1.5)

# Paso 1: Moneda y monto
show_progress(1, 6)
show_title("DATOS DE LA BECA", "Paso 1 de 6")

print(f"\n{Theme.INFO}Monedas disponibles:{Theme.RESET}")
for code, details in CURRENCIES.items():
    print(f" {Theme.ACCENT}•{Theme.RESET} {code} ({details['name']} - {details['symbol']})")

print()
scholarship_currency = get_input(
    "¿En qué moneda está su beca? (CRC/USD/EUR): ", 
    validate_currency, 
    "Moneda inválida. Use CRC, USD o EUR.", 
    "CRC"
).upper()

scholarship = float(get_input(
    f"Monto recibido ({CURRENCIES[scholarship_currency]['name']}): ", 
    validate_float, 
    "Ingrese un número válido."
))

result_currency = get_input(
    f"\n¿En qué moneda desea ver los resultados? (CRC/USD/EUR): ", 
    validate_currency, 
    "Moneda inválida. Use CRC, USD o EUR.", 
    scholarship_currency
).upper()

# Paso 2: Período
clear_screen()
show_progress(2, 6)
show_title("PERÍODO DE LA BECA", "Paso 2 de 6")

today = datetime.now().strftime("%Y-%m-%d")
print(f"\n{Theme.INFO}Ingrese las fechas en formato YYYY-MM-DD{Theme.RESET}")
print(f"{Theme.INFO}Fecha actual: {Theme.ACCENT}{today}{Theme.RESET}")

start_date_str = get_input(
    "Fecha de inicio: ", 
    validate_date, 
    "Formato inválido. Use YYYY-MM-DD."
)

end_date_str = get_input(
    "Fecha de fin: ", 
    validate_date, 
    "Formato inválido. Use YYYY-MM-DD."
)

# Convertir fechas a objetos datetime
start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

if start_date > end_date:
    print(Theme.ERROR + "\n⚠ Error: La fecha de inicio debe ser anterior o igual al fin." + Theme.RESET)
    exit()

# Paso 3: Días de asistencia
clear_screen()
show_progress(3, 6)
show_title("DÍAS DE ASISTENCIA", "Paso 3 de 6")

print(f"\n{Theme.INFO}¿Cuántos días por semana asiste a la universidad?{Theme.RESET}")
attending_days_per_week = int(get_input(
    "Días por semana (1-7): ", 
    validate_int_range(1, 7), 
    "Ingrese un número entre 1 y 7."
))

# Calcular total de días y días de asistencia
total_days = (end_date - start_date).days + 1
total_weeks = total_days / 7
attending_days = int(total_weeks * attending_days_per_week)

# Paso 4: Transporte
clear_screen()
show_progress(4, 6)
show_title("GASTOS DIARIOS", "Paso 4 de 6")

print(f"\n{Theme.INFO}¿Cuánto gasta en transporte por día de asistencia?{Theme.RESET}")
daily_transportation = float(get_input(
    f"Transporte diario ({CURRENCIES[scholarship_currency]['symbol']}): ", 
    validate_float, 
    "Ingrese un número válido."
))

# Paso 5: Gastos fijos mensuales
clear_screen()
show_progress(5, 6)
show_title("GASTOS FIJOS", "Paso 5 de 6")

fixed_expenses = []
print(f"\n{Theme.INFO}¿Tiene gastos fijos mensuales como gimnasio o suscripciones?{Theme.RESET}")
has_fixed = get_input(
    "¿Agregar gastos fijos? (s/n): ", 
    lambda x: x.lower() in ['s', 'n'], 
    "Ingrese 's' para sí o 'n' para no.", 
    "n"
).lower()

if has_fixed == "s":
    print(f"\n{Theme.INFO}Ingrese sus gastos fijos uno por uno.{Theme.RESET}")
    print(f"{Theme.INFO}Escriba '{Theme.ACCENT}fin{Theme.INFO}' en el nombre para terminar.{Theme.RESET}")
    
    while True:
        name = input(f"\n{Theme.INFO}Nombre del gasto: {Theme.INPUT}")
        print(Theme.RESET, end="")
        
        if name.lower() == "fin":
            break
            
        amount = float(get_input(
            f"Monto ({CURRENCIES[scholarship_currency]['symbol']}): ", 
            validate_float, 
            "Ingrese un número válido."
        ))
        
        fixed_expenses.append((name, amount))
        print(Theme.SUCCESS + f"✓ {name} agregado" + Theme.RESET)

total_fixed_expenses = sum(amount for _, amount in fixed_expenses)

# Paso 6: Priorizar ahorros
clear_screen()
show_progress(6, 6)
show_title("AHORROS", "Paso 6 de 6")

print(f"\n{Theme.INFO}¿Desea reservar una parte de su beca para ahorros?{Theme.RESET}")
want_savings = get_input(
    "¿Guardar para ahorros? (s/n): ", 
    lambda x: x.lower() in ['s', 'n'], 
    "Ingrese 's' para sí o 'n' para no.", 
    "n"
).lower()

if want_savings == "s":
    savings = float(get_input(
        f"Monto a ahorrar ({CURRENCIES[scholarship_currency]['symbol']}): ", 
        validate_float, 
        "Ingrese un número válido."
    ))
else:
    savings = 0

# Calcular presupuesto automático
clear_screen()
loading_effect("Calculando presupuesto", 1.5)

total_transportation = attending_days * daily_transportation
scholarship_converted = convert_amount(scholarship, scholarship_currency, result_currency)
total_transportation_converted = convert_amount(total_transportation, scholarship_currency, result_currency)
total_fixed_expenses_converted = convert_amount(total_fixed_expenses, scholarship_currency, result_currency)
savings_converted = convert_amount(savings, scholarship_currency, result_currency)

remaining_after_fixed = scholarship_converted - total_transportation_converted - total_fixed_expenses_converted
remaining_after_savings = remaining_after_fixed - savings_converted

suggested_food = (remaining_after_savings * 0.6) / total_days  # 60% para comida
suggested_minor = (remaining_after_savings * 0.4) / total_days  # 40% para gastos menores

# Mostrar sugerencia
show_title("SUGERENCIA AUTOMÁTICA", "Basado en su información")

print(f"\n{Theme.INFO}Con base en su beca y gastos, le sugerimos:{Theme.RESET}")
print(f"{Theme.ACCENT}•{Theme.RESET} Comida: {Theme.SUCCESS}{CURRENCIES[result_currency]['symbol']}{suggested_food:,.0f}{Theme.RESET} por día")
print(f"{Theme.ACCENT}•{Theme.RESET} Gastos menores: {Theme.SUCCESS}{CURRENCIES[result_currency]['symbol']}{suggested_minor:,.0f}{Theme.RESET} por día")

accept_suggestion = get_input(
    "\n¿Acepta estos valores? (s/n): ", 
    lambda x: x.lower() in ['s', 'n'], 
    "Ingrese 's' para sí o 'n' para no.", 
    "s"
).lower()

if accept_suggestion == "s":
    daily_food_budget = convert_amount(suggested_food, result_currency, scholarship_currency)
    daily_minor_expenses_budget = convert_amount(suggested_minor, result_currency, scholarship_currency)
else:
    print(f"\n{Theme.INFO}Ingrese sus propios valores diarios:{Theme.RESET}")
    daily_food_budget = float(get_input(
        f"Comida diaria ({CURRENCIES[scholarship_currency]['symbol']}): ", 
        validate_float, 
        "Ingrese un número válido."
    ))
    daily_minor_expenses_budget = float(get_input(
        f"Gastos menores diarios ({CURRENCIES[scholarship_currency]['symbol']}): ", 
        validate_float, 
        "Ingrese un número válido."
    ))

# Calcular costos totales
total_food = daily_food_budget * total_days
total_minor_expenses = daily_minor_expenses_budget * total_days
total_expenses = total_transportation + total_food + total_minor_expenses + total_fixed_expenses + savings

total_transportation_converted = convert_amount(total_transportation, scholarship_currency, result_currency)
total_food_converted = convert_amount(total_food, scholarship_currency, result_currency)
total_minor_expenses_converted = convert_amount(total_minor_expenses, scholarship_currency, result_currency)
total_expenses_converted = convert_amount(total_expenses, scholarship_currency, result_currency)
remaining_converted = scholarship_converted - total_expenses_converted

# Mostrar resumen con animación y tabla
clear_screen()
loading_effect("Generando resumen", 1.5)

symbol = CURRENCIES[result_currency]['symbol']
is_deficit = total_expenses_converted > scholarship_converted

show_title("RESUMEN DEL PRESUPUESTO", f"Período: {start_date_str} → {end_date_str}")

print(f"\n{Theme.HIGHLIGHT} INFORMACIÓN GENERAL {Theme.RESET}")
print(f"{Theme.ACCENT}•{Theme.RESET} Beca: {Theme.SUCCESS}{symbol}{scholarship_converted:,.0f}{Theme.RESET}")
print(f"{Theme.ACCENT}•{Theme.RESET} Días totales: {Theme.SUCCESS}{total_days}{Theme.RESET}")
print(f"{Theme.ACCENT}•{Theme.RESET} Días en universidad: {Theme.SUCCESS}{attending_days}{Theme.RESET} ({attending_days_per_week}/semana)")

print(f"\n{Theme.HIGHLIGHT} PRESUPUESTO {Theme.RESET}")
print_separator_single(Theme.SECONDARY)
print(f"{Theme.INFO} Categoría            │ {Theme.SUCCESS}Monto{Theme.RESET}")
print_separator_single(Theme.SECONDARY)
print(f"{Theme.INFO} Transporte           │ {Theme.SUCCESS}{symbol}{total_transportation_converted:,.0f}{Theme.RESET}")
print(f"{Theme.INFO} Comida               │ {Theme.SUCCESS}{symbol}{total_food_converted:,.0f}{Theme.RESET}")
print(f"{Theme.INFO} Gastos menores       │ {Theme.SUCCESS}{symbol}{total_minor_expenses_converted:,.0f}{Theme.RESET}")
if fixed_expenses:
    print(f"{Theme.INFO} Gastos fijos         │ {Theme.SUCCESS}{symbol}{total_fixed_expenses_converted:,.0f}{Theme.RESET}")
    for name, amount in fixed_expenses:
        print(f"{Theme.INFO}  - {name:<17} │ {Theme.SUCCESS}{symbol}{convert_amount(amount, scholarship_currency, result_currency):,.0f}{Theme.RESET}")
if savings > 0:
    print(f"{Theme.INFO} Ahorros reservados   │ {Theme.SUCCESS}{symbol}{savings_converted:,.0f}{Theme.RESET}")
print_separator_single(Theme.SECONDARY)
print(f"{Theme.INFO} Total gastos         │ {Theme.WARNING}{symbol}{total_expenses_converted:,.0f}{Theme.RESET}")
print(f"{Theme.INFO} Resultado            │ {(Theme.ERROR + '✘ Déficit' if is_deficit else Theme.SUCCESS + '✔ Ahorros')}: {Theme.SUCCESS}{symbol}{abs(remaining_converted):,.0f}{Theme.RESET}")
print_separator_single(Theme.SECONDARY)

# Guardar en archivo
with open("resumen_presupuesto.txt", "w", encoding="utf-8") as f:
    f.write("═" * 60 + "\n")
    f.write("Gestor de Presupuesto de Beca\n")
    f.write("═" * 60 + "\n")
    f.write(f"Período: {start_date_str} → {end_date_str}\n")
    f.write(f"Beca: {symbol}{scholarship_converted:,.0f}\n")
    f.write(f"Días totales: {total_days}\n")
    f.write(f"Días en universidad: {attending_days} ({attending_days_per_week}/semana)\n")
    f.write("\nPRESUPUESTO\n")
    f.write("─" * 60 + "\n")
    f.write(f"Transporte: {symbol}{total_transportation_converted:,.0f}\n")
    f.write(f"Comida: {symbol}{total_food_converted:,.0f}\n")
    f.write(f"Gastos menores: {symbol}{total_minor_expenses_converted:,.0f}\n")
    if fixed_expenses:
        f.write(f"Gastos fijos: {symbol}{total_fixed_expenses_converted:,.0f}\n")
        for name, amount in fixed_expenses:
            f.write(f" - {name}: {symbol}{convert_amount(amount, scholarship_currency, result_currency):,.0f}\n")
    if savings > 0:
        f.write(f"Ahorros reservados: {symbol}{savings_converted:,.0f}\n")
    f.write("─" * 60 + "\n")
    f.write(f"Total gastos: {symbol}{total_expenses_converted:,.0f}\n")
    f.write(f"Resultado: {'Déficit' if is_deficit else 'Ahorros'}: {symbol}{abs(remaining_converted):,.0f}\n")
    f.write("═" * 60 + "\n")

print(f"\n{Theme.SUCCESS}✓ Resumen guardado en 'resumen_presupuesto.txt'{Theme.RESET}")
time.sleep(0.5)