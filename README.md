# Double Commander в стиле Total Commander

Набор скриптов, который превращает [Double Commander](https://doublecmd.sourceforge.io/)
(GTK-сборка, Linux) в почти классический **Total Commander** — по цветам,
теме и иконке.

Double Commander и так повторяет скелет Total Commander (две панели, диск-бар,
кнопки F3–F10, командная строка, вкладки, горячие клавиши), но выглядит
«по-линуксовому». Этот скрипт возвращает классический вид:

* **Цвета файловых панелей** — как в классическом TC: белый фон, чёрный текст,
  жёлтый курсор, выделенные файлы — тёмно-зелёным, курсор неактивной панели —
  приглушённо-серый. Меняются обе темы (`Light` и `Dark`) и цвета всех колонок.
* **Строка пути** — классическая серая, а не системный цвет выделения темы
  (в тёмных темах она бывает оранжевой/синей).
* **Папки без квадратных скобок** — `[папка]` — это фишка Norton Commander,
  в TC папки показываются без них.
* **Классическая серая GTK2-тема Raleigh** (стиль Windows 95) — меню, кнопки
  и тулбар становятся светло-серыми. Опционально (`--no-gtkrc`). Файл
  `~/.gtkrc-2.0` затрагивает только GTK2-приложения (практически — один DC).
* **Иконка Total Commander** (синяя дискета) для ярлыка в меню приложений.
  Опционально (`--no-icon`). В репозиторий иконка **не входит** — скрипт
  скачивает её с Wikimedia Commons: права на логотип принадлежат
  Ghisler Software, используйте локально на свой страх.

> **Скриншоты:** TODO — добавьте свои (или пришлите PR).

## Требования

* Linux, Double Commander **GTK-сборка** (проверено на 1.1.32 / doublecmd-gtk)
* `python3` (только стандартная библиотека; `pillow` — опционально, для
  генерации всех размеров иконки; без него ставится один PNG 256×256)

## Установка

**Закройте Double Commander** — он перезаписывает конфиг при выходе.
Скрипт проверяет это сам и откажется работать, если DC запущен.

```bash
git clone https://github.com/mishin/doublecmd-totalcommander-theme.git
cd doublecmd-totalcommander-theme
python3 install.py
```

Что произойдёт:

1. `~/.config/doublecmd/colors.json` — перекрашивается (блоки `FilePanel`,
   `Path` и цвета всех колонок в `ColumnSets`, в обеих темах);
2. `~/.config/doublecmd/doublecmd.xml` — `<DirBrackets>` → `False`;
3. создаётся `~/.gtkrc-2.0` с темой Raleigh;
4. в `~/.local/share/icons/hicolor/<размер>/apps/` кладётся иконка TC под
   именем `doublecmd` (перекрывает системную, системные файлы не трогаются).

Перед каждым изменением оригинал сохраняется рядом: `*.bak-ГГГГММДД-ЧЧММСС`.

После установки запустите DC. Если иконка в меню не обновилась: на **Wayland**
нужен выход из сеанса и вход (оболочка кэширует иконки), на X11 обычно
достаточно перезапуска панели/оболочки.

## Флаги

| Флаг | Действие |
|---|---|
| `--no-icon` | не трогать иконку ярлыка |
| `--no-gtkrc` | не включать GTK2-тему Raleigh |
| `--restore` | восстановить конфиг из последнего бэкапа и удалить `~/.gtkrc-2.0` (если создан скриптом) |
| `--remove-icon` | удалить установленную иконку TC |
| `--force` | не проверять, что Double Commander закрыт |

## Откат

```bash
python3 install.py --restore        # конфиг + gtkrc
python3 install.py --remove-icon    # иконка
```

Или вручную: скопировать `*.bak-*` поверх конфигов, удалить `~/.gtkrc-2.0`
и `~/.local/share/icons/hicolor/*/apps/doublecmd.png`.

## Ограничения

* **HiDPI-экраны:** DC масштабирует свои шрифты, но шрифт виджетов GTK2
  (заголовки колонок, дерево настроек, диалоги) — нет, поэтому он может
  выглядеть мелким. Раскомментируйте в `~/.gtkrc-2.0` строку
  `gtk-font-name = "Sans 20"` и подберите число под себя (перезапустите DC).
* Иконка **окна** в панели задач остаётся DC-шной — она зашита в бинарник
  (`/usr/share/doublecmd/pixmaps/mainicon/`). Замена требует правки
  системных файлов.
* Общий вид виджетов ограничен возможностями GTK2: Raleigh даёт классический
  «серый» вид, но пиксель-в-пиксель как на Windows не повторить.
* Скрипт проверен на конфиге, который генерирует DC 1.1.32; на других версиях
  структура `colors.json` может отличаться — если что-то пошло не так,
  `--restore` вернёт всё как было.

## Горячие каталоги (Ctrl+D) — как в TC

Меню горячих каталогов в Double Commander работает так же, как в Total
Commander, и уже назначено на те же клавиши:

| Клавиши | Команда | Что делает |
|---|---|---|
| **Ctrl+D** | `cm_DirHotList` | попап-меню с сохранёнными каталогами (как Ctrl+D в TC) |
| **Ctrl+Shift+D** | `cm_ConfigDirHotList` | окно настройки — аналог «Настройка…» в меню TC |

Как наполнить список (Настройки → Каталоги / Ctrl+Shift+D):

* **«Добавить каталог активной вкладки»** — аналог TC-шного «Добавить текущий
  каталог»;
* «Добавить каталоги активной **и неактивной** вкладок» — обе панели разом;
* «Добавить выделенные или каталог под курсором» — замаркуйте пачку папок в
  панели и закиньте их одним кликом (в TC так нельзя);
* «Добавить вручную» и разделители — для порядка; список — дерево, есть
  сворачивание веток и «Тест итогового меню» (предпросмотр попапа прямо из
  диалога);
* экспорт/импорт списка в файл — удобно переносить между машинами.

Единственное отличие от TC: в попапе Ctrl+D у DC 1.1.32 **нет** пункта
«Добавить текущий каталог» — добавление идёт через диалог (Ctrl+Shift+D).

## English TL;DR

Make [Double Commander](https://doublecmd.sourceforge.io) (GTK build, Linux)
look like classic **Total Commander**: TC panel colors (white background,
black text, yellow cursor, green selected files, silver path line), no
`[brackets]` around folders, classic gray Windows-95-style GTK2 theme
(Raleigh), and the TC floppy icon for the app launcher (downloaded from
Wikimedia Commons at install time — not distributed with this repo, the
logo belongs to Ghisler Software).

```bash
# close Double Commander first!
python3 install.py            # apply everything
python3 install.py --restore  # roll back configs + gtkrc
python3 install.py --remove-icon
```

User-level config only (`~/.config/doublecmd`), automatic timestamped
backups, DC must be closed while running the script. Tested with
Double Commander 1.1.32 (GTK2) on Ubuntu / GNOME (Wayland).

Tip: **Ctrl+D** opens the TC-style directory hotlist, **Ctrl+Shift+D** opens
its editor ("Настройки → Каталоги") — see the section above for details.

## Лицензия

Код — [MIT](LICENSE). Логотип Total Commander не входит в состав репозитория
и является собственностью Ghisler Software GmbH.
