//XXX Here there is a looooot of repeated code, global methods, etc
//XXX should be refactorized =)
function hideResultsTable(){
    $('.poll-results').hide();
}

function pieChart() {
    hideResultsTable();
    $('#content .poll-data.pie-poll').each(function(){
        var $this = $(this);
        var r = Raphael($this.find('.pollresultholder')[0]);
        var labels = [];
        var data = [];
        var total = 0;
        $this.find('.poll-results .option_description').each(function(){
            labels.push($(this).text());
        });
        $this.find('.poll-results .option_result').each(function(){
            var value = parseInt($(this).text());
            data.push(value);
            total = total + value;
        });

        for (var i=0; i < labels.length; i++){
            var percent = (data[i] / total) * 100;
            var n_round = Math.round(percent*Math.pow(10,2))/Math.pow(10,2);
            labels[i] = String(n_round) + "% - " + labels[i];
        }

        pie = r.piechart(110, 110, 100,
                        data,
                            {
                            legend: labels,
                            legendpos: "east",
                            legendothers: legendothers_translation
                            }
                        );

        pie.hover(function () {
            this.sector.stop();
            this.sector.scale(1.1, 1.1, this.cx, this.cy);

            if (this.label) {
                this.label[0].stop();
                this.label[0].attr({ r: 7.5 });
                this.label[1].attr({ "font-weight": 800 });
            }
        }, function () {
            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

            if (this.label) {
                this.label[0].animate({ r: 5 }, 500, "bounce");
                this.label[1].attr({ "font-weight": 400 });
            }
        });
    });
};

function barChart() {
    hideResultsTable();
    $('#content .poll-data.bar-poll').each(function(){
        var $this = $(this);
        var r = Raphael($this.find('.pollresultholder')[0]);
        var labels = [];
        var data = [];
        $this.find('.poll-results .option_description').each(function(){
            labels.push($(this).text());
         });
        $this.find('.poll-results .option_result').each(function(){
             data.push(parseInt($(this).text()));
          });
        fin = function () {
                      this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
                  };
        fout = function () {
                      this.flag.animate({opacity: 0}, 300, function () {this.remove();});
                  };
        var bar = r.hbarchart(0, 0, 300, 220, data,{type: "soft"}).hover(fin, fout);
        var txtattr = { font: "12px sans-serif", "text-anchor": "start" };
        for (var j = 0; j < (data.length || 1); j++) {
            var text = r.text(10, bar.bars[j].y, labels[j]).attr(txtattr);
        }
    });
};

function hideResultsPortlet(){
    $('.poll-results').hide();
}

function pieChartPortlet() {
    hideResultsPortlet();
    $(".poll-data.pie-poll").each(function(){
        var $this = $(this);
        var r = Raphael($this.find('.portletpollresultholder')[0]);
        var labels = [];
        var data = [];
        var total = 0;
        $this.find('.poll-results .option_description').each(function(){
            labels.push($(this).text());
        });
        $this.find('.poll-results .option_result').each(function(){
            var value = parseInt($(this).text());
            data.push(value);
            total = total + value;
        });

        for (var i=0; i < labels.length; i++){
            var percent = (data[i] / total) * 100;
            var n_round = Math.round(percent*Math.pow(10,2))/Math.pow(10,2);
            labels[i] = String(n_round) + "% - " + labels[i];
        }

        pie = r.piechart(30, 30, 20,
                        data,
                        { legend: labels,
                        legendpos: "east",
                        legendothers: legendothers_translation
                        });

        pie.hover(function () {
            this.sector.stop();
            this.sector.scale(1.1, 1.1, this.cx, this.cy);

            if (this.label) {
                this.label[0].stop();
                this.label[0].attr({ r: 7.5 });
                this.label[1].attr({ "font-weight": 800 });
            }
        }, function () {
            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

            if (this.label) {
                this.label[0].animate({ r: 5 }, 500, "bounce");
                this.label[1].attr({ "font-weight": 400 });
            }
        });
    });
};

function barChartPortlet() {
    hideResultsPortlet();
    $(".poll-data.bar-poll").each(function(){
        var $this = $(this);
        var r = Raphael($this.find('.portletpollresultholder')[0]);
        var labels = [];
        var data = [];
        $this.find('.poll-results .option_description').each(function(){
            labels.push($(this).text());
        });
        $this.find('.poll-results .option_result').each(function(){
            data.push(parseInt($(this).text()));
        });
        fin = function () {
            this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
        };
        fout = function () {
            this.flag.animate({opacity: 0}, 300, function () {this.remove();});
        };
        var bar = r.hbarchart(0, 0, 120, 200, data,{type: "soft"}).hover(fin, fout);
        var txtattr = { font: "12px sans-serif", "text-anchor": "start" };
        for (var j = 0; j < (data.length || 1); j++) {
            var text = r.text(10, bar.bars[j].y, labels[j]).attr(txtattr);
        }
    });
};

/*ajax submit form*/
function ajaxSubmitForm() {
    $('.votePortlet form').submit(function(event) {
      var $this = $(this);
      var $parent = $this.parents('.votePortlet');
      var url = $this.attr('action');
      var data = $this.serialize()+'&ajax_load=True&poll.submit=True';
        //show the ajax load spinner
        $('.poll-spinner', $parent).show();
        $this.css({'visibility': 'hidden'});
      $.ajax({
        url: url,
        data: data,
        type: 'POST',
        contents: '#content-core',
        success: function(html){
            //gets the portlet assigment column
            var manager = ''
            if ($parent[0] !== undefined){
                manager = $parent.attr('data');
            }
            $.ajax({
                url: './@@poll_portlet_render',
                data: {'column':manager},
                success:function(data){
                    $parent.replaceWith(data);
                    $('.spinner', $parent).hide();
                }
            });

        }
      });
      return false;
    });
}

jQuery(document).ready(function($) {
    var portletpies = $('.votePortlet .pie-poll');
    var portletbars = $('.votePortlet .bar-poll');

    ajax_starter = false;
    if (portletpies[0] !== undefined) {
        pieChartPortlet();
        ajax_starter = true;
    }
    if (portletbars[0] !== undefined) {
        barChartPortlet();
        ajax_starter = true;
    }
    if (ajax_starter) {
        ajaxSubmitForm();
    }

    var pies = $('#content .pie-poll');
    var bars = $('#content .bar-poll');

    if (pies[0] !== undefined) {
        pieChart();
    }
    if (bars[0] !== undefined) {
        barChart();
    }
});
