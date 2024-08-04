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