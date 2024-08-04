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