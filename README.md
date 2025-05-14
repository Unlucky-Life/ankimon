## Ankimon Experimental Branch `(h0tp-ftw/ankimon)`
 This repository is an **experimental branch** for [Ankimon](https://github.com/Unlucky-life/Ankimon) with new features and community-driven development. You can try out the latest features, but beware, you may also have bugs and issues!

---

### Current Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/h0tp-ftw">
        <img src="https://avatars.githubusercontent.com/u/141889580?v=4" width="80"><br>
        <span style="font-size:1.15em; font-weight:bold;">h0tp</span>
      </a><br>
      <span style="font-size:0.9em; color:#888;">Owner</span><br>
      <span style="font-size:0.8em; color:gray;">@h0tp-ftw</span>
    </td>
    <td align="center">
      <a href="https://github.com/thepeacemonk">
        <img src="https://avatars.githubusercontent.com/u/105552060?v=4" width="80"><br>
        <span style="font-size:1.15em; font-weight:bold;">Peace</span>
      </a><br>
      <span style="font-size:0.9em; color:#888;">Contributor</span><br>
      <span style="font-size:0.8em; color:gray;">@thepeacemonk</span>
    </td>
    <td align="center">
      <a href="https://github.com/gykoh">
        <img src="https://avatars.githubusercontent.com/u/105884770?v=4" width="80"><br>
        <span style="font-size:1.15em; font-weight:bold;">Gill</span>
      </a><br>
      <span style="font-size:0.9em; color:#888;">Contributor</span><br>
      <span style="font-size:0.8em; color:gray;">@gykoh</span>
    </td>
    <td align="center">
      <a href="https://github.com/richy431">
        <img src="https://avatars.githubusercontent.com/u/207916526?v=4" width="80"><br>
        <span style="font-size:1.15em; font-weight:bold;">richy</span>
      </a><br>
      <span style="font-size:0.9em; color:#888;">Contributor</span><br>
      <span style="font-size:0.8em; color:gray;">@richy431</span>
    </td>
    <td align="center">
      <a href="https://github.com/unlucky-life">
        <img src="https://avatars.githubusercontent.com/u/77027147?v=4" width="80"><br>
        <span style="font-size:1.15em; font-weight:bold;">Unlucky</span>
      </a><br>
      <span style="font-size:0.9em; color:#888;">Ankimon creator</span><br>
      <span style="font-size:0.8em; color:gray;">@unlucky-life</span>
    </td>
  </tr>
</table>


Want to join us? Read below!


## Table of Contents

- [Downloading the Experimental Ankimon Build](#downloading-the-experimental-ankimon-build)
- [Instructions for Current Contributors](#instructions-for-current-contributors)
- [I don't know how to CODE! Where do I start?](#i-dont-know-how-to-code-where-do-i-start)
- [Instructions for New Contributors](#instructions-for-new-contributors)
- [Need Help?](#need-help)

---

## Downloading the Experimental Ankimon Build

Releases will be published every time a major pull request is merged into `main`; in simple words, after a major change is added. Check the [**Releases**](https://github.com/h0tp-ftw/ankimon/releases) tab here! Make sure to BACKUP before updating!

If you want to download the files and source code directly:

1. Click the green **"Code"** button near the top right of this page.
2. Select **"Download ZIP"**.
3. Unzip the file on your computer. 
4. Make sure you have a **backup** of your `mypokemon.json`, `mainpokemon.json`, `badges.json` and `items.json` files (in `user_files` folder of your Ankimon installation)
5. In the downloaded folder, go in `src` -> `Ankimon` and copy all files inside the folder.
6. Paste these files into your Ankimon folder where the addon is installed in Anki! (Anki -> Add-ons -> Ankimon -> View Files)
7. If you lost your progress, restore by adding the back-up files into the `user_files` folder!

---

## Instructions for Current Contributors

- **Branching:** Always create a new branch for your changes.  
  Name your branch using the format:
  - For bug fixes: `fix/your-fix-name`
  - For new features: `feature/your-feature-name`
  
  `main` is used to get changes from branches (after testing), and `upstream` will be used to send code to the official Ankimon repository.

- **Pull Requests:** After making your changes, open a Pull Request (PR) to merge your branch into the `main` branch.  
  Add a clear description of your changes in the PR.

- **Testing**: For the PRs that are created here, please feel free to review these changes and try them out. We will merge them ONLY if contributors show that it is working properly :)

- After major changes, I will merge it to `upstream` branch, and add a PR to merge it with the official Ankimon branch. 



---

## I don't know how to CODE! Where do I start?

Both me (h0tp) and Unlucky started with barely any experience. You do not need ANY experience to start, as long as you have a **passion** for Ankimon and can spend some time learning new stuff! Ankimon is largely made using *Vibe-coding*, i.e. getting AI assistance with coding. 

It is made 100% by volunteers that help in their spare time. Having more people (like you) will help to make Ankimon better! It is also made using Python (for functions) and JavaScript (for data storage), which are easy to learn!

To get started:

- Download [VS Code](https://code.visualstudio.com/) for coding
- Go through the [W3schools Python tutorial](https://www.w3schools.com/python/default.asp) - no need to learn every single thing
- Make some simple code for practice! For example, you could try making a calculator, or coding some new changes for Ankimon.
- Go through the Ankimon code, especially [here](https://github.com/Unlucky-Life/ankimon/tree/main/src/Ankimon/functions) and learn about how functions work. For example, if it says 
``` catchable = set()
        for pokemon in self.excluded:
            if self.can_catch(caught_pokemon, pokemon):
                catchable.add(pokemon)
        return catchable
```
Can you figure out what this code is actually trying to do? 
- Start using AI! Use the AI service of your choice to get help with coding. Learn how to guide AI and spot the errors that AI makes in coding. 

At this point, it is more important to let AI do the coding, and you should be able to *guide* it! Fixing the errors it makes will be your main concern. 

---

## Instructions for New Contributors

1. **Fork this repository:**  
   Click the "Fork" button at the top right of this page to create your own copy.

2. **Make your changes:**  
   Add your improvements or fixes in your forked repository.

3. **Submit a Pull Request:**  
   - Push your changes to your fork.
   - Go to this repository and click "Pull request".
   - Add a description of your changes and submit.

4. **After your first accepted PR**, you will become access to this repository as a **maintainer** to help shape the project!
You will also get access to our Discord channel for contributors and can collaborate on new features and fixes.

---


### Need Help?

- Please reach out on the [Ankimon Discord server](https://discord.gg/eY8jPHZw4z)
- You can also add to [Issues](../../issues) or [Discussions](../../discussions) tabs here

___


## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=unlucky-life/ankimon&type=Date)](https://www.star-history.com/#unlucky-life/ankimon&Date)

Ankimon is an Anki addon designed to gamify your learning experience by allowing you to catch, collect, train, and fight with Pokémon within the Anki environment. With Ankimon, learning becomes an adventure where you can enhance your knowledge while having fun.

Support my Caffeine Addiction (something that helps building this Addon):

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/A0A7SGLI8)

## Features

- **Pokémon Collection:** Catch and collect Pokémon as you progress through your Anki decks.
- **Training:** Train your Pokémon to improve their abilities and strengths.
- **Battles:** Engage in battles with other users on Pokémon Showdown to test your knowledge and skills.
- **Interactive Learning:** Ankimon integrates seamlessly with Anki, enhancing your learning process by adding an element of excitement and challenge.

## How to Use

1. **Installation:** Download and install Ankimon addon for Anki.

   **Important:** You need to download: „Data Files, Sprite Files and Badges and Item Sprites“!

2. **Catch Pokémon:** As you review your Anki cards, encounter and catch Pokémon to add to your collection.
3. **Training:** Train your Pokémon using various methods to strengthen them for battles.
4. **Battles:** Challenge other users on Pokémon Showdown to battles using your trained Pokémon.
5. **Bug Reporting:** If you encounter any issues or bugs, please report them on the [GitHub Issues Page](https://github.com/Unlucky-Life/ankimon/issues). Your feedback helps improve the addon for everyone.

## Important Notes

- **Linux OS** Before reporting an issue on Linux, make sure you check if it works with the package downloaded directly from the [Anki github](https://github.com/ankitects/anki/releases) as it could be a problem with the package maintained by a third party (distro maintainer or flatpak)
- **Addon Status:** Ankimon is still in development. Please report any bugs you encounter to help improve the addon.
- **Backup Files:** Before updating the addon, ensure to copy your "mypokemon.json" and "mainpokemon.json" files to prevent data loss before any updates. Please check out my GitHub Ankimon Page before updating - I will let you know when an update is coming in.
- **Compatibility:** Currently, Ankimon is **only compatible with PyQt6**. Updates for compatibility with other versions will be provided in the future.

## Screenshots
<div style="display:flex;flex-wrap:wrap;justify-content:center;">
  <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/d3d62c70-8473-407a-92b1-daf37817a9e6" alt="image" width="300" height="200">
    <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/6a1a4979-10d1-4618-81f4-f8865caf7206" alt="image" width="250" height="300">
  <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/ad3bf54f-24dd-4150-abdc-25aa23b6543a" alt="image" width="600" height="200">
    <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/cf131fdc-1ff4-4d67-a6a3-e9d1ec2a3d42" alt="image" width="600" height="200">
  <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/a6f2f1cf-e308-4a02-8c15-9f8a32b32cd7" alt="image" width="600" height="200">
  <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/6bdd303d-3055-4520-b0ae-bc144c3d55b9" alt="image" width="400" height="200">
  <img src="https://github.com/Unlucky-Life/ankimon/assets/77027147/ed6330ad-db26-4894-8375-869704a78a08" alt="image" width="400" height="200">
</div>

Start your Pokémon journey with Ankimon and make learning an adventure!
![image](https://github.com/user-attachments/assets/1e5b9f0e-18c4-4115-a73e-08fc2e97f4d8)


### NOTE - for any contributions, make sure to **create your own branch** instead of merging into `main`, and add pull requests with your changes. We will review these changes and merge onto `main` after testing them.

## Honorable Mentions for current active contributors
**h0tp** @h0tp-ftw
**Peace** @thepeacemonk
**Gill** @gykoh
**richy** @richy431 
