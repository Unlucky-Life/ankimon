# 🌟 Patch Notes v1.352 🌟

## **New Features & Enhancements:**
- **Improved Pokémon Collection:** Fixed the issue with multiple paginator buttons appearing when reopening the Pokémon collection window.
- **Streamlined UI:** Refactored and categorized the buttons in the Ankimon window menu for a cleaner, more organized interface.
- **PyQt6 Support:** Added an option to install the PyQt6 dependency directly into Anki for smoother integration.
- **User Role Enhancement:** Assigned a base value of **1000** to `UserRole`, providing a clearer structure.
- **Pokédex Improvements:** Added a loading screen while the Pokédex prepares the HTML data for a seamless user experience.

## **Bug Fixes:**
- **Pokémon Sync Window:** Resolved an issue related to the `text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap)` function in PyQt6.
- **Attack Fixes:** Addressed the problem of multiple attacks being assigned to a single Pokémon.
- **Crash Prevention:** Added a paginator to the Pokémon collection window, preventing crashes from occurring.
- **Evolution Fixes:** Corrected the evolution mechanics for Pokémon by level and item.

## **Quality of Life Updates:**
- **Logger Integration:** Added a comprehensive logger to capture all messages and improve debugging.
- **Shiny Pokémon:** Implemented functionality to encounter and collect shiny Pokémon.
- **Spawn Rates:** Reworked Pokémon spawn rates for a more balanced experience.
- **Pokémon Attributes:** Now track individual Pokémon attributes such as **ID**, **catch date**, **defeated Pokémon count**, and **friendship score**.
- **Object-Oriented Refactor:** The code has undergone a full refactor into an "object-oriented" design for greater maintainability and flexibility.

## **New Gameplay Features:**
- **Ankimon Tracker:** Introduced an Ankimon tracker to help with debugging and provide more detailed insights into the gameplay.
- **Daily Item Shop:** Added a new daily item shop where trainers can purchase valuable items.
- **Trainer Card System:** Implemented a trainer card that levels up as you progress, showcasing your achievements.
- **Trainer Cash Rewards:** Trainers can now earn cash by reaching custom daily goals on their trainer card.

## **Usability Enhancements:**
- **Fast Selection Dialog:** Added a quick selection dialog to easily choose Pokémon attacks.
- **Reviewer Window Customization:** Trainers can now select a different view in the reviewer window for added flexibility.
- **Styling Toggle:** Quickly toggle the Ankimon reviewer’s styling with a simple press of **button 8** for a more personalized look.
- **Missing Sprite Fallbacks:** Added fallback sprites to handle any missing sprite errors, ensuring smooth visuals.
- **Pokédex Upgrade:** Added a live Pokédex alongside the traditional Pokédex, keeping you updated with real-time Pokémon data.

## **Miscellaneous Fixes:**
- **Ankimon Open/Close Key:** Resolved issues with the Ankimon open and close key functionality, ensuring smooth transitions between windows.

---

With these improvements, trainers can enjoy a more polished, streamlined, and feature-rich Ankimon experience. Don’t forget to update and dive into all the exciting new content!


### 🚀 **Patch notes v1.286!** 🚀

## 🚀 **Ankimote Implementation!** 🚀
- Choose if you would like to automatically defeat or catch an Ankimon.
- **Automatic Options:** Decide if you want to automatically catch or defeat Ankimon or none of both.
- You can now press a button combination inside the Anki reviewer to catch or defeat an Ankimon.
    - HowTo: Check out the configuration options
    - default catch pokemon: control + D for catching pokemon
    - default defeat pokemon: control + F for defeating pokemon
### How to Implement Ankimote 🎮:

1. **Locate the Configuration File:**
   - Find the `ankimote_config.json` file inside the `addon_files` folder.

2. **Copy the Configuration File:**
   - Copy the `ankimote_config.json` file.

3. **Replace the Existing Configuration File:**
   - Navigate to the Ankimote addon folder.
   - Paste the copied file into this folder.
   - Rename the copied file from `ankimote_config.json` to `config.json`, replacing the existing `config.json` file in the folder.
     
### 🎮 Commands for Catching and Defeating Pokémon in Ankimote: 🎮

- **CMD 2:** Use this command to catch Ankimon.
- **CMD 3:** Use this command to defeat Ankimon.
=> Add these buttons on your phone with the Settings Option

### Using Ankimote in Anki Reviewer:
- if the wild pokemon is defeated you can choose to catch or defeat the pokemon automatically in the options of ankimon
- OR
- You can instead use the ankimon shortcut key
### 📘 **HowTo: Check Out the Configuration Options!** 📘

------------------------------------

### 🚀 **Update v1.285!** 🚀

- 🛠️ Fixed issues when exporting all Ankimon data to Ankimon Paste and Ankimon Showdown.
- 🆕 Added filter for Ankimon collection by type.
- 🔧 Resolved issues with moves not found after trading.
- 🎨 New ability to deactivate styling in reviewer.
- 🔄 Fixed trading, naming, and releasing issues with multiple Ankimon having the same ID.
- 🌟 All sprites are now included within the addon due to licensing changes of PokeAPI.

-------------------------------------

## 🚨 **Attention Ankimon Trainers!** 🚨

🔥 Whether you're eager to **trade** your Ankimon 🐉, **train** with fellow trainers 🏋️‍♂️, or simply chat and share tips 🗣️, our server is THE place to be! 🔥

🎉 **Don't miss out! Join us today and become part of our rapidly growing community!** 🎉

🔗 **Join the Discord Server Now!** 👉 [Join the Discord Server](https://discord.gg/AvCESmPGfy)

Link: https://discord.gg/AvCESmPGfy

🌟 Let's catch 'em all together! See you there, Trainers! ⚡

### 📢 **Having Issues? Let Us Know!** 📢

If you encounter any new issues with the update, please report them on GitHub instead of downvoting: [GitHub Issues](https://github.com/Unlucky-Life/ankimon/issues)
https://github.com/Unlucky-Life/ankimon/issues

### 💡 **Have Ideas? We Want to Hear Them!** 💡

If you have any awesome ideas or suggestions for Ankimon, share them on our discussion page: [Discussion Page](https://github.com/Unlucky-Life/ankimon/discussions/2)
https://github.com/Unlucky-Life/ankimon/discussions/2

Copyright © 2024 Unlucky-Life on GitHub. All rights reserved.
