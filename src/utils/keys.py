import RPi.GPIO as GPIO
import time
import sys

# Определение пинов в соответствии с подключением
col_pins = [24, 25, 8, 7]  # Пины, соответствующие столбцам на матрице клавиатуры
row_pins = [12, 16, 20, 21]  # Пины, соответствующие строкам

# Настройка пинов GPIO
GPIO.setmode(GPIO.BCM)  # Использование BCM нумерации пинов

# Настройка пинов строк на вывод, установка в HIGH
for pin in row_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

# Настройка пинов столбцов на ввод с подтяжкой к питанию
for pin in col_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Матрица соответствия клавиш
key_map = [
    ["D", "#", "0", "*"],
    ["C", "9", "8", "7"],
    ["B", "6", "5", "4"],
    ["A", "3", "2", "1"]
]

# Функция для чтения клавиатуры
def read_keypad():
    for row_pin in row_pins:
        GPIO.output(row_pin, GPIO.LOW)
        for col_pin in col_pins:
            if GPIO.input(col_pin) == 0:
                key = key_map[row_pins.index(row_pin)][col_pins.index(col_pin)]
                GPIO.output(row_pin, GPIO.HIGH)  # Возврат пина строки в HIGH перед выходом
                while GPIO.input(col_pin) == 0:
                    pass  # Дождаться отпускания клавиши
                time.sleep(0.1)  # Задержка для предотвращения дребезга
                return key
        GPIO.output(row_pin, GPIO.HIGH)

# Основной цикл программы
try:
    while True:
        key = read_keypad()
        if key:
            print("Вы нажали: " + key)
            time.sleep(0.3)  # Пауза для предотвращения множественных срабатываний
except KeyboardInterrupt:
    GPIO.cleanup()  # Очистка состояния GPIO при выходе
    sys.exit()
