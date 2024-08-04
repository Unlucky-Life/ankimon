_bottomHTML_template = """
        <center id=outer>
        <table id=innertable width=100%% cellspacing=0 cellpadding=0>
        <tr>
        <td align=start valign=top class=stat>
        <button title="%(editkey)s" onclick="pycmd('edit');">%(edit)s</button></td>
        <td align=center valign=top id=middle>
        </td>
        <td align=center valign=top class=stat>
        <button title="%(CatchKey)s" onclick="pycmd('catch');">Catch Pokemon</button>
        <button title="%(DefeatKey)s" onclick="pycmd('defeat');">Defeat Pokemon</button>
        </td>
        <td align=end valign=top class=stat>
        <button title="%(morekey)s" onclick="pycmd('more');">%(more)s %(downArrow)s</button>
        <span id=time class=stattxt></span>
        </td>
        </tr>
        </table>
        </center>
        <script>
        time = %(time)d;
        timerStopped = false;
        </script>
        """

button_style = """
    .button_style {
        position: absolute;
        white-space: nowrap;
        font-size: small;
        right: 0px;
        transform: translate(-50%, -100%);
        font-weight: normal;
        display: inline-block;
        }
    """

pokedex_html_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pokédex</title>
        <style>
        .pokedex-table { width: 100%; border-collapse: collapse; }
        .pokedex-table th, .pokedex-table td { border: 1px solid #ddd; text-align: left; padding: 8px; }
        .pokedex-table tr:nth-child(even) { background-color: #f2f2f2; }
        .pokedex-table th { padding-top: 12px; padding-bottom: 12px; background-color: #4CAF50; color: white; }
        .pokemon-image { height: 50px; width: 50px; }
        .pokemon-gray { filter: grayscale(100%); }
        </style>
        </head>
        <body>
        <table class="pokedex-table">
        <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Image</th>
        </tr>
        <!-- Table Rows Will Go Here -->
        </table>
        </body>
        </html>
        '''

attack_details_window_template = """
    <style>
      .pokemon-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        margin-bottom: 20px;
      }

      .pokemon-table th, .pokemon-table td {
        padding: 8px;
        border: 1px solid #ddd; /* light grey border */
      }

      .pokemon-table th {
        background-color: #040D12;
      }

      .pokemon-table tr:nth-child(even) {background-color: #f9f9f9;}

      .pokemon-table .move-name {
        text-align: center;
        font-weight: bold;
      }

      .pokemon-table .basePower {
        font-weight: bold;
        text-align: center;
      }

      .pokemon-table .no-accuracy {
        text-align: center;
        color: yellow;
      }
    </style>
    </head>
    <body>

    <table class="pokemon-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Category</th>
          <th>Power</th>
          <th>Accuracy</th>
          <th>PP</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
    """

attack_details_window_template_end = """
      </tbody>
    </table>

    </body>
    </html>
    """

remember_attack_details_window_template = """
    <style>
      .pokemon-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        margin-bottom: 20px;
      }

      .pokemon-table th, .pokemon-table td {
        padding: 8px;
        border: 1px solid #ddd; /* light grey border */
      }

      .pokemon-table th {
        background-color: #040D12;
      }

      .pokemon-table tr:nth-child(even) {background-color: #f9f9f9;}

      .pokemon-table .move-name {
        text-align: center;
        font-weight: bold;
      }

      .pokemon-table .basePower {
        font-weight: bold;
        text-align: center;
      }

      .pokemon-table .no-accuracy {
        text-align: center;
        color: yellow;
      }
    </style>
    </head>
    <body>

    <table class="pokemon-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Category</th>
          <th>Power</th>
          <th>Accuracy</th>
          <th>PP</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
    """

remember_attack_details_window_template_end = """
      </tbody>
    </table>

    </body>
    </html>
    """

terms_text = """§1 Disclaimer of Liability
(1) The user acknowledges that the use of the downloaded files is at their own risk. \n The provider assumes no liability for any damages, direct or indirect,\n that may arise from the download or use of such files.
(2) The provider is not responsible for the content of the downloaded files or \n for the legal consequences that may result from the use of the files. \n Each user is obligated to inform themselves about the legality of the use \n before using the files and to use the files only in a manner that does not cause any legal violations.

§2 Copyright Infringements
(1) The user agrees to respect copyright and other protective rights of third parties. \n It is prohibited for the user to download, reproduce, distribute, or make publicly available any copyrighted works \n without the required permission of the rights holder.
(2) In the event of a violation of copyright provisions, the user bears full responsibility and the resulting consequences. \n The provider reserves the right to take appropriate legal action \n in the event of becoming aware of any rights violations and to block access to the services.
                       
Check out https://pokeapi.co/docs/v2#fairuse and https://github.com/smogon/pokemon-showdown for more information.
                       """

rate_addon_text_label = """Thanks for using Ankimon! 
                            \nI would like Ankimon to be known even more in the community, 
                            \nand a rating would be amazing. Letting others know what you think of the addon.
                            \nThis takes less than a minute.

                            \nIf you do not want to rate this addon. Feel free to press: I dont want to rate this addon.
                            """

inject_life_bar_css_1 = """
            @keyframes shake {{
                0% {{ transform: translateX(0) rotateZ(0); filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5)); }}
                10% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                20% {{ transform: translateX(10%) rotateZ(5deg); }}
                30% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                40% {{ transform: translateX(10%) rotateZ(5deg); }}
                50% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                60% {{ transform: translateX(10%) rotateZ(5deg); }}
                70% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                80% {{ transform: translateX(10%) rotateZ(5deg); }}
                90% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                100% {{ transform: translateX(100vw); filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5)); }}
            }}
            """

inject_life_bar_css_2 = """
            #pokebackground {{
                color: white;
                background-color: blue;
                z-index: 99999;
            }}
            """

thankyou_message_text = """
            Thank you for Rating this Addon !
                               
            Please exit this window!
            """

dont_show_this_button_text = """This Pop Up wont turn up on startup anymore.
            If you decide to rate this addon later on.
            You can go to Ankimon => Rate This.
            Anyway, have fun playing !
            """