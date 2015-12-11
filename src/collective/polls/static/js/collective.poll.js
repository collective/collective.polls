! function($) {

  "use strict"; // jshint ;_;

  $(function() {
    var init_poll = function($poll) {
      var url = $poll.attr('data-poll-url');
      // Get updated results with ajax
      $.ajax({
        url: url + '/@@update-poll',
        context: $poll,
        success: function(data) {
          var $poll = this;
          var uid = $poll.attr('data-poll-uid');
          var base_css = '.poll[data-poll-uid=' + uid + '] ';
          // Update html
          $(base_css + '.poll-graph').html(data);

          // Check cookie and update poll state
          var cookie = 'collective.poll.' + uid;
          var has_votted = (document.cookie.indexOf(cookie) >= 0);
          var closed = ($poll.attr('data-poll-closed') === "True");
          var total_votes = parseInt($poll.attr('data-poll-totalvotes'), 10);
          if (total_votes === 0) {
            $(base_css + '.toggle-result').hide();
          } else {
            $(base_css + '.toggle-result').show();
          }
          if (has_votted || closed) {
            $(base_css + '.poll-form').remove();
            $(base_css + '.toggle-result').remove();
            $(base_css + '.poll-graph').addClass('active');
          } else { // not has_votted
            $(base_css + '.poll-form').addClass('active');
          }

          // Redraw the graphs
          $(base_css + '.poll-data, ' + base_css + ' .votePortlet form').drawpoll();
        }
      });
    };

    // Register click event on poll to persist when html change
    $('.poll').on('click', 'a.toggle-result', function(e) {
      e.preventDefault();
      var $poll = $(this).parents('.poll');
      $('.poll-toggle', $poll).toggleClass('active');
    });

    $('.poll form').on('submit', function(e) {
      // stop form submit and submit with ajax
      e.preventDefault();
      var $form = $(this);
      $.ajax({
        type: 'POST',
        url: $form.attr('action'),
        data: $form.serialize() + '&poll.submit=Submit',
        context: this,
        success: function(data) {
          var $form = $(this);
          var $poll = $form.parents('.poll');
          // After ajax submit, update the poll
          init_poll($poll);
        }
      });
    });

    $('.poll').each(function() {
      var $poll = $(this);
      init_poll($poll);
    });
  });

  var DrawPoll = function(element, options) {
    this.init(element);
  };

  DrawPoll.prototype = {

    constructor: DrawPoll,

    init: function(poll) {
      this.poll = $(poll);
      this.content_handler = this.get_handler();
      if (this.content_handler[0] !== undefined) {
        this.type = this.get_type();
        this.data = this.get_data();
        this.extra_conf = {
          'width': undefined
        };

        switch (this.type) {
          //XXX at some poing we are going to have more cases :P
          case 'portlet':
            this.setup_portlet(this.data.type);
            break;
          default:
            this.setup_default(this.data.type);
        }

        this.draw(this.data, this.content_handler, this.extra_conf);
      }
    },

    draw: function(data, content_handler, extra_conf) {
      content_handler.polls({
        width: extra_conf.width,
        type: data.type,
        data: data.result_data
      });
    },

    get_data: function(poll) {
      var poll = poll !== undefined ? poll : this.poll,
        raw_results = poll.find('.poll-results'),
        result = {},
        result_data = [];

      raw_results.find('li').each(function(i) {
        var li = $(this),
          data = {};

        data['label'] = li.find('.option_description').text();
        data['data'] = li.find('.option_result').text() * 1;
        result_data[i] = data;
      });

      result['type'] = this.get_graph_type(poll);
      result['result_data'] = result_data;
      raw_results.hide();

      return result
    },

    get_handler: function(poll) {
      var poll = poll !== undefined ? poll : this.poll,
        handler = poll.find('[class*=pollresultholder]');

      return handler
    },

    get_type: function(handler) {
      var handler = handler !== undefined ? handler : this.content_handler,
        re = /\w+(?=pollresultholder)/,
        match = handler.attr('class').match(re),
        type = match ? match[0] : match;

      if (type === undefined) {
        type = 'default';
      }

      return type
    },

    get_graph_type: function(poll) {
      var poll = poll !== undefined ? poll : this.poll,
        re = /\w+(?=-poll)/,
        match = poll.attr('class').match(re),
        type = match ? match[0] : match;

      return type
    },

    setup_portlet: function(type) {
      if (type === 'pie') {
        this.content_handler.height(150);
      } else if (type === 'bar') {
        var width = this.poll.parents('.portletItem').width();
        this.content_handler.width(width);
      }
    },
    setup_default: function(type) {
      var width = 350;
      switch (type) {
        case 'pie':
          this.content_handler.height(200);
          this.content_handler.width(width);
          break;
        case 'bar':
          width = 300;
          break;
      }
      this.extra_conf['width'] = width;
    }
  };

  /*we define a jquery plugin, in that way we can go out of the js scope
   and yes i know, cluttering the global namespace*/

  $.fn.drawpoll = function(option) {
    return this.each(function() {
      var $this = $(this),
        data = $this.data('drawpoll'),
        options = typeof option == 'object' && option;

      if (!data) $this.data('drawpoll', (data = new DrawPoll(this, options)));
      if (typeof option == 'string') data[option]();
    });

  };

  $.fn.drawpoll.Constructor = DrawPoll;

}(window.jQuery);
