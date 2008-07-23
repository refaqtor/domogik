<?php
/*
Copyright 2008 Domogik project

This file is part of Domogik.
Domogik is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Domogik is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik.  If not, see <http://www.gnu.org/licenses/>.

Author: Maxence Dunnewind <maxence@dunnewind.net>

$LastChangedBy: mschneider $
$LastChangedDate: 2008-07-23 21:42:29 +0200 (mer. 23 juil. 2008) $
$LastChangedRevision: 100 $
*/
?>	

<script src="<?=$this->config->item('JS_DIR')?>prototype.js" language="JavaScript" ></script>
<script src="<?=$this->config->item('JS_DIR')?>reflection.js" type="text/javascript" ></script>
<script type="text/javascript" src="/include/flotr/flotr.js" ></script>
<script>
var f = null;       
var load = function(){
    new Ajax.Request(BASE_URL+'index.php/temperature/update/'+$('roomId').getAttribute('value'), {
        onSuccess: function(transport){
            /**
             * Parse (eval) the JSON from the server.
             */
            var json = transport.responseText.evalJSON();
            
            if(json.series && json.options){
                /**
                 * The json is valid! Display the canvas container.
                 */
                $('container').setStyle({'display':'block'});
                
                /**
                 * Draw the graph using the JSON data. Of course the
                 * options are optional.
                 */
                var f = Flotr.draw($('container'), json.series, json.options);
            }
        }
    });
}
</script>
  	<script type="text/javascript" charset="utf-8">

	/*
	 * Page loading
	 */
	(function() {
      Event.observe(document, 'dom:loaded', function() {
	    load();
        new PeriodicalExecuter(load, <?=$this->config->item('TEMP_REFRESH')?>);
	  })
    })()
  </script>
</head>
