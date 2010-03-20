const close_without_change = 10000; // 10 seconds
const close_with_change = 3000; // 3 seconds

(function($) {
	$.widget("ui.range_command", {
        _init: function() {
            var self = this, o = this.options;
			var states = o.states.toLowerCase().split(/\s*,\s*/);
			this.min_value = states[0];
			this.max_value = states[1];
			this.steps = states[2];
            this.widgets = new Array();
            this.element.addClass('command_range')
                .addClass('icon32-state-' + o.usage);
        },
                
        registerWidget: function(id) {
            this.widgets.push(id);
            $(id).range_widget({
                command: this,
                usage: this.options.usage,
				min_value: this.min_value,
				max_value: this.max_value,
				steps: this.steps,
				unit: this.options.unit
            })
			.range_widget('setValue', this.currentValue);
        },
		
		setValue: function(value) {
			if (value >= this.min_value && value <= this.max_value) {
				this.currentValue = value;
			} else if (value < this.min_value) {
				this.currentValue = this.min_value;
			} else if (value > this.max_value) {
				this.currentValue = this.max_value
			}
			this.processingValue = this.currentValue;
            this.displayValue(this.currentValue);
            for each (widget in this.widgets) {
                $(widget).range_widget('setValue', this.currentValue);
            }
        },

		setProcessingValue: function(value) {
			if (value >= this.min_value && value <= this.max_value) {
				this.processingValue = value;
			} else if (value < this.min_value) {
				this.processingValue = this.min_value;
			} else if (value > this.max_value) {
				this.processingValue = this.max_value
			}
            this.displayProcessingValue(this.processingValue);
            for each (widget in this.widgets) {
                $(widget).range_widget('setProcessingValue', this.processingValue);
            }
		},
		
		processValue: function() {
			this.options.action(this, this.processingValue);
		},
		
        displayValue: function(value) {

        },
        displayProcessingValue: function(value) {

        },		
		plus_range: function() {
			var value = Math.floor((this.processingValue + 10) / 10) * 10;
			this.setProcessingValue(value);
		},
		
		minus_range: function() {
			var value = Math.floor((this.processingValue - 10) / 10) * 10;
			this.setProcessingValue(value);
		}
    });
    
    $.extend($.ui.range_command, {
        defaults: {
        }
    });
	
	/* Widget */
    
    $.widget("ui.range_widget_core", {
        _init: function() {
            var self = this, o = this.options;
            this.element.addClass('widget_range')
                .attr("tabindex", 0);
			this.elementstate = $("<div class='widget_state'></div>");
            this.elementicon = $("<div class='widget_icon'></div>");
			this.elementvalue = $("<div class='widget_value'></div>");
			this.elementvalue.addClass('icon32-state-' + o.usage);
			this.element.append(this.elementstate);
			this.elementicon.append(this.elementvalue);				
            this.element.append(this.elementicon);
        },

		displayBackground: function(value, min_value, max_value) {
			var percent_value = (value / (max_value - min_value)) * 100;
			this.elementicon.css('-moz-background-size', '100% ' + percent_value + '%');
			var percent_icon = findRangeIcon(this.options.usage, percent_value);
			this.elementvalue.addClass('range_' + percent_icon);
        },
		
		displayValue: function(value, unit) {
			this.elementstate.text(value + unit);
			this.elementvalue.text('');
        },
		
		displayProcessingValue: function(value, unit) {
			this.elementvalue.text(value + unit);
		}
    });
    
    $.extend($.ui.range_widget_core, {
        defaults: {
        }
    });
    
    $.widget("ui.range_widget", {
        _init: function() {
            var self = this, o = this.options;
            this.element.range_widget_core({
                usage: o.usage
            });
			this.button_plus = $("<div class='range_plus' style='display:none'></div>");
			this.button_plus.click(function (e) {self.plus();e.stopPropagation()});
			this.button_minus = $("<div class='range_minus' style='display:none'></div>");
			this.button_minus.click(function (e) {self.minus();e.stopPropagation()});
			this.element.addClass('closed');
			this.element.find('.widget_icon').append(this.button_plus)
				.append(this.button_minus)
				.click(function (e) {
						if (self.openflag) {
							self.close();
							self.options.command.processValue();							
						} else {
							self.open();							
						}
						e.stopPropagation();
					});
			this.element.keypress(function (e) {
					switch(e.keyCode) { 
					// User pressed "up" arrow
					case 38:
						self.plus();
						break;
					// User pressed "down" arrow
					case 40:
						self.minus();
						break;
					}
					e.stopPropagation();
				});
        },
		
		setValue: function(value) {
            this.element.range_widget_core('displayBackground', value, this.options.min_value, this.options.max_value);                
            this.element.range_widget_core('displayValue', value, this.options.unit);                
        },

		setProcessingValue: function(value) {
            this.element.range_widget_core('displayBackground', value, this.options.min_value, this.options.max_value);                
            this.element.range_widget_core('displayProcessingValue', value, this.options.unit);                
        },
		
		plus: function() {
			var self = this;
			this.element.doTimeout( 'timeout', close_with_change, function(){
				self.close();
				self.options.command.processValue();
			});
			this.options.command.plus_range();
		},

		minus: function() {
			var self = this;
			this.element.doTimeout( 'timeout', close_with_change, function(){
				self.close();
				self.options.command.processValue();
			});
			this.options.command.minus_range();
		},
		
		open: function() {
			var self = this;
			this.openflag = true;
			this.element.removeClass('closed')
				.addClass('opened');
			this.button_plus.show();
			this.button_minus.show();
			this.element.doTimeout( 'timeout', close_without_change, function(){
				self.close();
			});
		},
		
		close: function() {
			this.openflag = false;
			this.element.removeClass('opened')
				.addClass('closed');
			this.button_plus.hide();
			this.button_minus.hide();
		}
    });
	
    $.extend($.ui.range_widget, {
        defaults: {
        }
    });
})(jQuery);

/*
function widget_range(widget_id, function_id, widget_usage, min_value, max_value, default_value, unit) {
    $('#' + widget_id).addClass('widget_range')
        .addClass('icon32-usage-' + widget_usage);
    $('#' + widget_id + " .up").click(function () {plus_range(function_id)});
    $('#' + widget_id + " .down").click(function () {minus_range(function_id)});
    
    $('#' + widget_id + " .slider").slider({
	range: false,
	min: min_value,
	max: max_value,
	value: default_value,
	slide: function(event, ui) {
		slide_range(function_id, ui.value);
	    }
	});
	$('#' + widget_id + " .value").val(default_value + unit);
}


		function plus_range(function_id) {
			var data = $("#range_data").data(function_id);
			data.value = Math.floor((data.value + 10) / 10) * 10;
			if (data.value > data.max) {data.value = data.max}
			$('#widgetmini_' + function_id + ' .range_value').text(data.value+data.unit);
			$('#widget_' + function_id + " .value").val(data.value+data.unit);
			$('#widget_' + function_id + " .slider").slider('value', data.value);
			var percent_value = (data.value / (data.max - data.min)) * 100;
			$('#widgetmini_' + function_id).css('-moz-background-size', '100% ' + percent_value + '%')
		}
		
		function minus_range(function_id) {
			var data = $("#range_data").data(function_id);
			data.value = Math.floor((data.value - 10) / 10) * 10;
			if (data.value < data.min) {data.value = data.min}
			$('#widgetmini_' + function_id + ' .range_value').text(data.value+data.unit);
			$('#widget_' + function_id + " .value").val(data.value+data.unit);
			$('#widget_' + function_id + " .slider").slider('value', data.value);
			var percent_value = (data.value / (data.max - data.min)) * 100;
			$('#widgetmini_' + function_id).css('-moz-background-size', '100% ' + percent_value + '%')
		}


function slide_range(function_id, value) {
    var data = $("#range_data").data(function_id);
    data.value = value;
    $('#widgetmini_' + function_id + ' .range_value').text(data.value+data.unit);
    $('#widget_' + function_id + " .value").val(data.value+data.unit);
    var percent_value = (data.value / (data.max - data.min)) * 100;
    $('#widgetmini_' + function_id).css('-moz-background-size', '100% ' + percent_value + '%')
}
 */