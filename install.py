#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Double Commander в стиле Total Commander — установщик темы.
https://github.com/mishin/doublecmd-totalcommander-theme

Делает Double Commander (GTK-сборка, Linux) визуально похожим на классический
Total Commander:
  * цвета файловых панелей: белый фон, чёрный текст, жёлтый курсор,
    зелёные выделенные файлы, серый курсор неактивной панели;
  * строка пути: классический серый фон;
  * папки без квадратных скобок (фишка Norton Commander в DC по умолчанию);
  * классическая серая GTK2-тема Raleigh (стиль Windows 95) — опционально;
  * иконка Total Commander для ярлыка — опционально, скачивается с
    Wikimedia Commons (в репозиторий иконка не входит, права принадлежат
    Ghisler Software).

Перед запуском закройте Double Commander — скрипт сам проверит и откажется
работать, если он запущен (или используйте --force на свой страх).

Меняются только настройки пользователя (~/.config/doublecmd), оригиналы
сохраняются рядом как *.bak-ГГГГММДД-ЧЧММСС.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "doublecmd")
COLORS = os.path.join(CONFIG_DIR, "colors.json")
XML = os.path.join(CONFIG_DIR, "doublecmd.xml")
GTKRC = os.path.join(os.path.expanduser("~"), ".gtkrc-2.0")
GTKRC_MARK = "# doublecmd-totalcommander-theme"

ICON_URL = ("https://upload.wikimedia.org/wikipedia/commons/"
            "3/39/Total_Commander_Logo.png")
ICON_PAGE = "https://commons.wikimedia.org/wiki/File:Total_Commander_Logo.png"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
UA = ("doublecmd-totalcommander-theme/1.0 "
      "(https://github.com/mishin/doublecmd-totalcommander-theme)")

# Цвета в формате Delphi TColor (BGR-целые), как их хранит Double Commander:
# белый=16777215, чёрный=0, жёлтый=65535, тёмно-зелёный=32768,
# серебро=12632256, серый=8421504
FILEPANEL = {"ForeColor": 0, "BackColor": 16777215, "BackColor2": 16777215,
             "MarkColor": 32768, "CursorColor": 65535, "CursorText": 0,
             "InactiveCursorColor": 12632256, "InactiveMarkColor": 32768}
COLUMNS = {"TextColor": 0, "Background": 16777215, "Background2": 16777215,
           "MarkColor": 32768, "CursorColor": 65535, "CursorText": 0,
           "InactiveCursorColor": 12632256, "InactiveMarkColor": 32768}
PATH = {"ActiveColor": 12632256, "ActiveFontColor": 0,
        "InactiveColor": 12632256, "InactiveFontColor": 8421504}
SECTIONS = {"FilePanel": FILEPANEL, "Path": PATH, "ColumnSets": COLUMNS}

INT_LINE = re.compile(r"^(\s*)(\w+)\s*:\s*(-?\d+)\s*,?\s*$")
SECTION_OPEN = re.compile(r"^(FilePanel|Path|ColumnSets)\s*:\s*[\[{]")


def check_not_running(force):
    if force:
        return
    try:
        r = subprocess.run(["pgrep", "-x", "doublecmd"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except FileNotFoundError:          # pgrep недоступен — пропускаем проверку
        return
    if r.returncode == 0:
        sys.exit("Ошибка: Double Commander сейчас запущен. Закройте его и "
                 "повторите запуск (он перезаписывает конфиг при выходе), "
                 "либо используйте --force.")


def backup(path):
    if not os.path.exists(path):
        return None
    dst = path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, dst)
    return dst


def patch_colors(text):
    """Перекрашивает блоки FilePanel, Path и колонки ColumnSets.

    colors.json у Double Commander — «ленивый» JSON (ключи без кавычек),
    поэтому правим построчно, отслеживая секции по отступам.
    """
    out, changed = [], 0
    current = None                 # (имя секции, отступ её открывающей скобки)
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if current is not None:
            name, open_indent = current
            if indent <= open_indent:      # блок закрылся
                current = None
            else:
                keys = SECTIONS[name]
                m = INT_LINE.match(line)
                if m and m.group(2) in keys:
                    nl = "\n" if line.endswith("\n") else ""
                    comma = "," if stripped.endswith(",") else ""
                    out.append("%s%s : %d%s%s" % (m.group(1), m.group(2),
                                                  keys[m.group(2)], comma, nl))
                    changed += 1
                    continue
        elif SECTION_OPEN.match(stripped):
            current = (stripped.split(":")[0].strip(), indent)
        out.append(line)
    return "".join(out), changed


def patch_xml(text):
    if "<DirBrackets>True</DirBrackets>" in text:
        return (text.replace("<DirBrackets>True</DirBrackets>",
                             "<DirBrackets>False</DirBrackets>"), True)
    return text, False


def apply(no_icon, no_gtkrc, force):
    if not os.path.isdir(CONFIG_DIR):
        sys.exit("Не найден каталог конфигурации %s.\n"
                 "Запустите Double Commander один раз, чтобы он его создал."
                 % CONFIG_DIR)
    if not os.path.exists(COLORS):
        sys.exit("Не найден файл %s (создаётся Double Commandером при "
                 "настройке цветов). Запустите DC, откройте Настройки → Цвета "
                 "и нажмите ОК." % COLORS)

    check_not_running(force)

    # --- colors.json: цвета панелей и строки пути ---------------------------
    text = open(COLORS, encoding="utf-8").read()
    bak = backup(COLORS)
    new_text, n = patch_colors(text)
    if n:
        open(COLORS, "w", encoding="utf-8").write(new_text)
    print("Цвета панелей и строки пути: изменено значений: %d%s" %
          (n, " (бэкап: %s)" % os.path.basename(bak) if bak else ""))

    # --- doublecmd.xml: папки без скобок ------------------------------------
    if os.path.exists(XML):
        text = open(XML, encoding="utf-8").read()
        bak = backup(XML)
        new_text, changed = patch_xml(text)
        if changed:
            open(XML, "w", encoding="utf-8").write(new_text)
        print("Папки без скобок [DirBrackets]: %s%s" %
              ("включено" if changed else "уже было выключено / нет настройки",
               " (бэкап: %s)" % os.path.basename(bak) if changed else ""))

    # --- GTK2-тема ----------------------------------------------------------
    if no_gtkrc:
        print("GTK2-тема: пропущена (--no-gtkrc)")
    elif os.path.exists(GTKRC):
        print("~/.gtkrc-2.0 уже существует — не трогаю (классическую тему "
              'можно включить вручную: gtk-theme-name="Raleigh")')
    else:
        open(GTKRC, "w", encoding="utf-8").write(
            "%s: классическая серая тема GTK2 (стиль Windows 95 / TC)\n"
            "# Откат: удалите этот файл\n"
            'gtk-theme-name="Raleigh"\n' % GTKRC_MARK)
        print("GTK2-тема Raleigh включена (~/.gtkrc-2.0 создан)")

    # --- иконка -------------------------------------------------------------
    if no_icon:
        print("Иконка: пропущена (--no-icon)")
    else:
        install_icon()

    print("\nГотово. Запустите Double Commander.")
    print("Если иконка в меню приложений не обновилась: на Wayland нужен "
          "выход из сеанса и вход, на X11 — перезапуск оболочки.")


def install_icon():
    base = os.path.join(os.path.expanduser("~"), ".local", "share", "icons",
                        "hicolor")
    dst = os.path.join(base, "256x256", "apps", "doublecmd.png")
    if os.path.exists(dst):
        print("Иконка TC уже установлена — пропускаю")
        return
    print("Скачиваю иконку Total Commander с Wikimedia Commons…")
    req = urllib.request.Request(ICON_URL, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=30).read()
    if not data.startswith(b"\x89PNG"):
        raise RuntimeError("скачанный файл не является PNG — иконка не "
                           "установлена")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "wb").write(data)
    try:
        from PIL import Image                     # необязательная зависимость
        im = Image.open(dst).convert("RGBA")
        for s in ICON_SIZES[:-1]:
            d = os.path.join(base, "%dx%d" % (s, s), "apps")
            os.makedirs(d, exist_ok=True)
            im.resize((s, s), Image.LANCZOS).save(
                os.path.join(d, "doublecmd.png"), "PNG")
        print("Иконка установлена (%d размеров)" % len(ICON_SIZES))
    except ImportError:
        print("PIL не найден — установлена только 256px, GTK отмасштабирует "
              "сам (pip install pillow — для всех размеров)")
    subprocess.run(["gtk-update-icon-cache", "-f", "-t", base],
                   capture_output=True)
    print("Источник: %s (© Ghisler Software, используется локально)" % ICON_PAGE)


def restore(force):
    check_not_running(force)
    for path in (COLORS, XML):
        baks = sorted(glob.glob(path + ".bak-*"))
        if baks:
            shutil.copy2(baks[-1], path)
            print("Восстановлен %s из %s" % (path, os.path.basename(baks[-1])))
        else:
            print("Бэкапы для %s не найдены" % path)
    if os.path.exists(GTKRC):
        with open(GTKRC, encoding="utf-8") as f:
            if f.readline().startswith(GTKRC_MARK):
                os.remove(GTKRC)
                print("~/.gtkrc-2.0 удалён (создан этим скриптом)")
            else:
                print("~/.gtkrc-2.0 не создан этим скриптом — не трогаю")
    print("Иконку, если ставили, можно убрать: python3 install.py "
          "--remove-icon")


def remove_icon():
    base = os.path.join(os.path.expanduser("~"), ".local", "share", "icons",
                        "hicolor")
    removed = 0
    for s in ICON_SIZES:
        p = os.path.join(base, "%dx%d" % (s, s), "apps", "doublecmd.png")
        if os.path.exists(p):
            os.remove(p)
            removed += 1
    subprocess.run(["gtk-update-icon-cache", "-f", "-t", base],
                   capture_output=True)
    print("Удалено файлов иконки: %d" % removed)


def main():
    ap = argparse.ArgumentParser(
        description="Double Commander в стиле Total Commander",
        epilog="Полное описание: см. README.md")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--restore", action="store_true",
                   help="восстановить конфиг из последнего бэкапа и убрать "
                        "GTK2-тему")
    g.add_argument("--remove-icon", action="store_true",
                   help="удалить установленную иконку TC")
    ap.add_argument("--no-icon", action="store_true",
                    help="не менять иконку ярлыка")
    ap.add_argument("--no-gtkrc", action="store_true",
                    help="не включать GTK2-тему Raleigh")
    ap.add_argument("--force", action="store_true",
                    help="не проверять, что Double Commander закрыт")
    args = ap.parse_args()
    if args.restore:
        restore(args.force)
    elif args.remove_icon:
        remove_icon()
    else:
        apply(no_icon=args.no_icon, no_gtkrc=args.no_gtkrc, force=args.force)


if __name__ == "__main__":
    main()
