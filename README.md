# Multi-Language Auto Typer

## Overview
Multi-Language Auto Typer is a versatile application that allows you to automatically type text in multiple languages, including Arabic and English. It provides a user-friendly interface with various customization options to suit your typing needs.

## Features
- Support for multiple languages including Arabic and English
- Character-by-character typing or whole text pasting options
- Adjustable typing speed and delay settings
- Save and load frequently used texts
- Pause and resume typing functionality
- Progress tracking with visual progress bar
- Light and dark theme options
- Convenient hotkey controls

## Requirements
- Python 3.6 or higher
- Required Python packages:
  - tkinter
  - pyautogui
  - keyboard
  - pyperclip

## Installation
1. Clone this repository or download the source code
2. Install the required packages:
```bash
pip install pyautogui keyboard pyperclip
```

## Usage
1. Run the application:
```bash
python auto_typer.py
```

2. Enter the text you want to type automatically in the text input area
3. Configure the typing settings:
   - Set the delay before typing starts
   - Adjust the typing speed
   - Select the appropriate language mode
   - For Arabic text, choose between character-by-character typing or whole text pasting

4. Click "Start Typing" or press F6
5. Quickly click where you want the text to be typed
6. Use F7 to pause/resume and F8 to stop typing if needed

## Language Support
- **Auto Detect**: Automatically detects Arabic characters in the text
- **Arabic Mode**: Optimized for Arabic text
- **English Mode**: Optimized for English text

## Arabic Text Handling
- **Character by Character**: Types each Arabic character individually
- **Paste Whole Text**: Pastes the entire Arabic text at once (better for preserving formatting)

## Hotkeys
- **F6**: Start typing
- **F7**: Pause/Resume typing
- **F8**: Stop typing

## Linux Compatibility
For Linux users:
1. Make sure xclip or xsel is installed for clipboard functionality:
```bash
sudo apt-get install xclip
```
or
```bash
sudo apt-get install xsel
```
2. Some window managers may require adjustments for the auto-typing to work properly.

## Saving and Loading Text
- Enter a name for your text and click "Save"
- Access your saved texts in the "Saved Texts" tab
- Load or delete saved texts as needed

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is intended for legitimate use cases such as data entry automation. Please use responsibly and respect the terms of service of any applications you interact with.

        