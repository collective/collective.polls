function hideResultsTable(){
    jQuery('ul#results').hide();
}

function pieChart() {
    hideResultsTable();
    var r = Raphael("pollresultholder");
    var labels = [];
    var data = [];
    jQuery('ul#results span.option_description').each(function(){
        labels.push(jQuery(this).text());
     });
     jQuery('ul#results span.option_result').each(function(){
         data.push(parseInt(jQuery(this).text()));
      });
     pie = r.piechart(110, 110, 100, 
                      data, 
                      { legend: labels,
                        legendpos: "east",
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
};

function barChart() {
    hideResultsTable();
    var r = Raphael("pollresultholder");
    var labels = [];
    var data = [];
    jQuery('ul#results span.option_description').each(function(){
        labels.push(jQuery(this).text());
     });
     jQuery('ul#results span.option_result').each(function(){
         data.push(parseInt(jQuery(this).text()));
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
};

function hideResultsPortlet(){
    jQuery('ul#results').hide();
}

function pieChartPortlet() {
    hideResultsPortlet();
    var r = Raphael("portletresultholder");
    var labels = [];
    var data = [];
    jQuery('ul#results span.option_description').each(function(){
        labels.push(jQuery(this).text());
     });
     jQuery('ul#results span.option_result').each(function(){
         data.push(parseInt(jQuery(this).text()));
      });
     pie = r.piechart(30, 30, 20, 
                      data, 
                      { legend: labels,
                        legendpos: "east",
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
};

function barChartPortlet() {
    hideResultsPortlet();
    var r = Raphael("portletresultholder");
    var labels = [];
    var data = [];
    jQuery('ul#results span.option_description').each(function(){
        labels.push(jQuery(this).text());
     });
     jQuery('ul#results span.option_result').each(function(){
         data.push(parseInt(jQuery(this).text()));
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
};