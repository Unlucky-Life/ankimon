def create_html_code(genderTop, genderBottom, nameTop, nameBottom, levelTop, levelBottom, current_health_bottom, max_hp_bottom, max_hp_top, current_health_top, text, general_url, sprites_url, font_url, id_bottom, id_top, display, main_attack, enemy_attack, fx_top = None, fx_bottom = None, xp_bar_width = 0):
    bottompokemon = f"{sprites_url}back_default_gif/{id_bottom}.gif"
    toppokemon = f"{sprites_url}front_default_gif/{id_top}.gif"
    html_code = """<div id="spacer">&nbsp;</div>"""
    html_code += """<div id="AnkimonWindow" class="Ankimon"></div>"""
    html_code += f"""<iframe id="myIframe" src='{general_url}pokemon-battle-master/index.html?generalUrl={general_url}&bottomPokemonUrl={sprites_url}back_default_gif/{id_bottom}.gif&topPokeUrl={sprites_url}front_default_gif/{id_top}.gif&text={text}&levelTop={levelTop}&levelBottom={levelBottom}&nameTop={nameTop}&nameBottom={nameBottom}&genderTop={genderTop}&genderBottom={genderBottom}&current_health_bottom={current_health_bottom}&max_hp_bottom={max_hp_bottom}&max_hp_top={max_hp_top}&fontUrl={font_url}&current_health_top={current_health_top}&main_attack={main_attack}&enemy_attack={enemy_attack}&fx_top={fx_top}&fx_bottom={fx_bottom}' width=100% style="display:{display};"></iframe>"""
    html_code2 = """
	<button id="toggleOpacityButton">Toggle Opacity</button>
    <script>
		var iframe = document.createElement('myIframe');
		document.addEventListener('keydown', function(event) {
		if (event.key === '8') {
			toggleOpacity();
		}
        });
	
		document.getElementById('toggleOpacityButton').addEventListener('click', function() {
		toggleOpacity();
        });
        
        function toggleOpacity() {
            var iframe = document.getElementById('myIframe');
            if (iframe.style.display === "none") {
                iframe.style.display = "block"; // Make the iframe visible
            } else {
                iframe.style.display = "none"; // Hide the iframe
            }
        }
    </script>"""
    return html_code

def create_head_code(generalurl):
    css_code = f"""
	:root {{
        --background_music: "{generalurl}/"
	}}
    
	@keyframes attack {{
    0% {{ transform: translate(0px, 0px); }}
    50% {{ transform: translate(300px, -10px); width: 60%; height: 70%}}
    100% {{ transform: translate(0px, 0px); }}
	}}

    @font-face {{
        font-family: 'Pokemon'; 
        src: url("{generalurl}Early_GameBoy.ttf");
    }}  

    #bottomPokemon {{
        width: 50%  ;
        height: 70%  ;
        background-image: url("{generalurl}/images/1.gif");
        background-size: contain  ;
        background-repeat: no-repeat  ;
        margin: auto  ;
        display: block  ;
        float: left  ;
        z-index: 3  ;
        position: absolute;
        top: 40%  ;
        left: 25%  ;
    }}

    #topPoke {{
        width: 50%  ;
        height: 70%  ;
        background-image: url("{generalurl}images/4.gif")  ;
        background-size: contain  ;
        margin: auto  ;
        display: block  ;
        background-repeat: no-repeat  ;
        float: right  ;
        position: relative  ;
        left: -5%  ;
        top: 10%  ;
    }}

    .innerRectangleBit {{
	width: 75%  ;
	height: 20%  ;
	position: relative  ;
	background-color: rgb(171,154,84)  ;
	top: 75%  ;
	display:inline-block  ;
	background-image: url("/_addons/1908235722/web/images/1.gif")  ;
    background-repeat: repeat-x  ;
    background-size: contain  ;
    }}

    .ovalOutterTop {{
	z-index: 1 ;
	position: absolute ;
    right: 2%;
	top: 35% ;
    width: 40% !important;
	max-width: 300px ;
	height: 20px ;
	background: rgb(200,200,176) ;
	border-radius: 50% / 50% ;
    }}

    .ovalOutterBottom {{
	z-index: 1 ;
	position: absolute ;
	bottom: 3% ;
    left: 2% ;
    width: 40% !important;
	max-width: 300px ;
	height: 20px ;
	background: rgb(200,200,176) ;
	border-radius: 50% / 50% ;
    }}

    #AnkimonContainer {{
    position: absolute;
	height: 100% ;
    width: 100%;
	background-color: rgb(223,225,218) ;
	overflow: hidden ;
	font-family: pokemon ;
	max-width: 800px ;
	max-height: 900px ;
    min-height: 300px;
	margin: auto ;
    }}

#top {{
	background-color: rgb(223,225,218) ;
	height: 70% ;
	width:100% ;
}}

#bottom {{
	background-color: rgb(64,64,80) ;
	height: 30% ;
	width:100% ;
	z-index: 3 ;
}}

#bottomBox {{
	height: 90% ;
	background-color: rgb(207,81,50) ;
	border-radius: 20px ;
	width:99% ;
	position:relative ;
	top: 5% ;
	left:0.5% ;
	z-index: 4 ;
}}

#bottomBoxInner {{
	height: 90% ;
	background-color: rgb(88,144,152) ;
	border-radius: 20px ;
	width:95% ;
	position:relative ;
	top: 5% ;
	left:2.5% ;
	z-index: 5 ;
}}

.topHalf {{
	height: 50% ;
	width: 100% ;

}}

.ovalInner {{
	z-index:2 ;
	width: 90% ;
	height: 80% ;
	background: rgb(176,176,144) ;
	border-radius: 50% / 50% ;
	position: relative ;
	transform: translateY(-180%) ;
	left: 5% ;
}}

.rectangleOutter {{
	z-index: 3 ;
	width: 85% ;
	height: 85% ;
	background: rgb(31,31,39) ;
	margin-left: 10% ;
	border-bottom-right-radius: 20px ;
	border-top-left-radius: 20px ;
	border-top-right-radius: 10px ;
	border-bottom-left-radius: 10px ;
}}

.rectangleInner {{
	z-index: 4 ; 
	width: 95% ;
	height: 90% ;
	background: rgb(240,240,208) ;
	position: relative ;
	top: -55% ;
	left: 2.5% ;
	border-bottom-right-radius: 20px ;
	border-top-left-radius: 20px ;
	border-top-right-radius: 10px ;
	border-bottom-left-radius: 10px ;
}}

#healthContainer {{
	width: 30% ;
	height: 150px ;
	z-index:2 ;
	position: relative ;
	top: 45% ;
}}

.hpContent {{
	width:90% ;
	height: 90% ;
	position: relative ;
	top: 10% ;
	left: 5% ;
	list-style: none ;
}}

#UpperHealthContainer {{
    width: 60%;
    height: 60px;
	z-index:2 !important;
    position: absolute !important;
	top: -5% !important;
	left: 5% !important;
}}

.UpperHpContent {{
	width:90% ;
	height: 90% ;
	position: relative ;
	top: 5% ;
	left: 5% ;
	list-style: none ;
}}

.hpList {{
	width:100% ;
	height:33% ;
}}


.UpperHpList {{
	width:100% ;
	height:50% ;
}}

.left {{
	float:left ;
	width:50% ;
	height: 100% ;
	overflow: hidden ;
}}

.right {{
	margin-left: 50% ;
	width:50% ;
	height: 100% ;
}}

#theTop {{
	float:right ;
	z-index: 0 ;
}}



.triangleBit {{
	z-index: -1 ;
	width:10% ;
	height: 40% ;
	left: 0px ;
	position: relative ;
	top: -25% ;
	float: left ;
	background: linear-gradient(to right bottom, transparent 50%, rgb(64,64,80) 50%) ;
}}

.exp {{
	width: 15% ;
	float: left ;
	position: relative ;
	top: 77% ;
	text-align: center ;
	display:inline-block ;
	color: rgb(240,208,0) ;
	font-size: xx-small ;
}}

.rectangleBit {{
	z-index: -1 ;
	width: 90% ;
	height: 50% ;
	float:right ;
	top:-35% ;
	position: relative ;
	background-color: rgb(64,64,80) ;
	border-bottom-right-radius: 20px ;
}}

#nameTop {{
	float: left ;
	font-size: 2.5vh ;
	font-weight: bold ;
    top: -140%;
    left: 0%;
    position: absolute;
    color: black !important;
}}

#nameBottom {{
	float: left ;
	font-size: 2.5vh ;
	font-weight: bold ;
	transform: translateY(10%) ;
}}

#hp {{
	color: rgb(230, 121, 89) ;
	float:left ;
	width: 20% ;
	position: relative ;
	left: 2% ;
	top: 15% ;
	font-size: 2vh ;
}}

#rhombus {{
	position: relative ;
    width: 80% ;
    height: 40% ;
    -o-transform: skew(45deg) ;
    background-color: rgb(64,64,80) ;
    margin-left: 5% ;
    top: -25% ;
    z-index: -1 ;
}}

#level {{
	float: right ;
	text-align: right ;
	font-weight: bold ;
	transform: translateY(30%) ;
	font-size: 2.5vh ;
}}

#health  {{
	float: right ;
	text-align: right ;
	font-size: 2.5vh ;
}}

#genderm  {{
	color: rgb(0,162,232) ;
	font-size: 1em ;
}}

#genderf  {{
	color: rgb(255,174,201) ;
	font-size: 1em ;
}}

#hpBar {{
	float: right ;
	width:80% ;
	height:70% ;
	background-color: rgb(64,64,80) ;
	border-radius: 500px ;
}}

#hpBarInner {{
	width:85% ;
	height:70% ;
	background-color: rgb(255,255,255) ;
	border-radius: 500px ;
	position: relative ;
	top: 16% ;
	left: 13% ;
}}

#hpSlider {{
	width:100% ;
	height:100% ;
	background-color: rgb(110,218,163) ;
	border-radius: 500px ;
	position: relative ;
	top: 0% ;
	left: 0% ;
}}

#healthTop {{
	margin-left: 0% ;
}}

#battleText {{
	height: 100% ;
	width: 100% ;
	text-align: center ;
	display: table ;
	float: left ;
	font-size: 1.5rem ;
	text-shadow: 2px 2px 0px #43547A ;
	font-family: Pokemon ;
	color: #ECEEED ;
}}

#battleText p{{
	display: table-cell ;
    vertical-align: middle ;
}}

#menuText {{

	display: inline-block ;
	height: 100% ;
	width: 38% ;
	background-color: white ;

}}

.menuRow {{
	height:45% ;
	width: 100% ;
}}

.menuHalf {{
	width: 45% ;
	font-size: 3.5vw ;
	padding: 2% ; 
	border: 2px solid transparent ;
}}


.theFocus {{
    border-radius: 5px ;
    border: 2px solid rgb(207,81,50) ;
    padding: 2% ; 
}}


.clearBoth {{ 
	clear:both ; 
}}
    """
    return css_code

#html_code = f"""<div id="AnkimonContainer">&nbsp<div class="ovalOutterTop">&nbsp;<div class="ovalInner">&nbsp;</div></div><div class="ovalOutterBottom">&nbsp;<div class="ovalInner">&nbsp;</div></div>"""
#html_code += f"""
#html_code += f"""<iframe src='https://play.pokemonshowdown.com/' width=100%></iframe>"""
#<div id="UpperHealthContainer">&nbsp<div class="rectangleOutter" id="healthTop">&nbsp<div class="rectangleInner">&nbsp<ul class="UpperHpContent">&nbsp<li class="UpperHpList">&nbsp<span id="nameTop">{nameTop}<span id="genderf"></span></span><span id="level">Lv: 99</span></li><li class="UpperHpList">&nbsp<div id="hpBar">&nbsp<div id="hp"> HP </div><div id="hpBarInner">&nbsp<div id="hpSlider">&nbsp</div></div></div></li></ul></div></div><div id="rhombus">&nbsp</div></div>"""