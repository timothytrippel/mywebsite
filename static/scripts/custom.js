/*
 * BSD 3-Clause License
 *
 * Copyright (c) 2021, Timothy Trippel <trippel@umich.edu>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permisson.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

$.fn.exists = function () {
  return this.length > 0 ? this : false;
};
//Handle window resize
var resizeFlag = 0;
$(window).resize(function () {
  resizeFlag = 1;
});
checkSizeChange();
function checkSizeChange() {
  if (resizeFlag) {
    resizeFlag = 0;
    $(window).trigger("resized");
  }
  setTimeout(function () {
    checkSizeChange();
  }, 200);
}

$(document).ready(function () {
  /*++++++++++++++++++++++++++++++++++++
		tooltips
	++++++++++++++++++++++++++++++++++++++*/
  $(".tooltips").tooltip();

  /*++++++++++++++++++++++++++++++++++++
		sidebar
	++++++++++++++++++++++++++++++++++++++*/
  var sideS,
    sidebar = {
      settings: {
        $side: $("#sidebar"),
        $main: $("#main"),
        $trigger: $("a.mobilemenu"),
        $totaltrigger: $(".social-icons, #main-nav, #main"),
        $sideFooter: $("#sidebar-footer"),
        $sideContent: $("#main-nav"),
        $sidebarWrapper: $("#sidebar-wrapper"),
        windowWidth: $(window).width(),
      },

      init: function () {
        sideS = this.settings;
        sideS.contentPadding = parseInt(
          sideS.$sideContent.css("padding-bottom")
        );
        this.customScrollFlag = false;
        this.setScrollBar();
        this.setContentPadding();
        this.bindUiActions();
        this.setMobileSide();
      },

      isIn: function () {
        return sideS.$main.hasClass("sideIn");
      },

      bindUiActions: function () {
        var self = this;
        sideS.$trigger.click(function (e) {
          e.preventDefault();
          if (self.isIn()) {
            self.sideOut();
          } else {
            self.sideIn();
          }
        });
        sideS.$totaltrigger.click(function () {
          if ($(window).width() < 960 && self.isIn()) self.sideOut();
        });

        sideS.$side.on("afterSlideIn", function () {
          if ($(window).width() <= 600) {
            // under 600px sidebar will cover the whole screen
            sideS.$main.css("display", "none");
          }
        });

        sideS.$side.on("beforeSlideOut", function () {
          if ($(window).width() <= 600) {
            sideS.$main.css("display", "block");
          }
        });

        $(window).on("resized", function () {
          sideS.windowWidth = $(window).width();
          self.setContentPadding();
          self.setScrollBar();
          if (sideS.windowWidth > 991) {
            self.reset();
          } else {
            self.gomobile();
          }

          self.setMobileSide();
        });
      },

      sideIn: function () {
        var self = this;
        var sWidth = sideS.$side.width();
        sideS.$side.trigger("beforeSlideIn");
        var SidebarAnimIn = new TimelineLite({
          onComplete: function () {
            sideS.$side.trigger("afterSlideIn");
          },
        });
        SidebarAnimIn.to(
          sideS.$main,
          0.5,
          { left: sWidth, right: -sWidth, ease: Power2.easeIn },
          "-=0.2"
        );
        sideS.$main.addClass("sideIn");
      },

      sideOut: function () {
        var self = this;
        sideS.$side.trigger("beforeSlideOut");
        var SidebarAnimOut = new TimelineLite({
          onComplete: function () {
            sideS.$side.trigger("afterSlideOut");
          },
        });
        SidebarAnimOut
          //.to(sideS.$side,0.2,{left:-250})
          .to(
            sideS.$main,
            0.5,
            { left: 0, right: 0, ease: Power2.easeIn },
            "-=0.2"
          );
        sideS.$main.removeClass("sideIn");
      },

      reset: function () {
        sideS.$main.css({ left: 250, right: 0 });
        sideS.$side.css({ left: 0 });
        sideS.$main.addClass("sideIn");
      },

      gomobile: function () {
        sideS.$main.css({ left: 0, right: 0 });
        sideS.$side.css({ left: 0 });
        sideS.$main.removeClass("sideIn");
      },
      setMobileSide: function () {
        var self = this;

        var tWidth = $(window).width();

        if (tWidth < 600) {
          sideS.$side.width(tWidth);
        } else {
          sideS.$side.width("");
          sideS.$main.css("display", "block");
        }
      },
      setContentPadding: function () {
        var self = this;
        var footerHeight = sideS.$sideFooter.outerHeight();
        sideS.$sideContent.css({
          paddingBottom: sideS.contentPadding + footerHeight,
        });
      },
      setScrollBar: function () {
        var self = this;

        if (
          (sideS.windowWidth > 1024 || !isTouchSupported()) &&
          !self.customScrollFlag
        ) {
          //Considiton that we want custom scrollbar
          self.setCustomScroll();
        } else if (
          sideS.windowWidth <= 1024 &&
          isTouchSupported() &&
          self.customScrollFlag
        ) {
          // Condition that we don't want custom scrollbar
          self.destroyCustomScroll();
        }
      },
      setCustomScroll: function () {
        this.customScrollFlag = true;
        sideS.$sidebarWrapper.niceScroll({
          horizrailenabled: false,
          cursorwidth: "6px",
          cursorborder: "none",
          cursorborderradius: "0px",
          cursorcolor: "#aaa",
        });
      },
      destroyCustomScroll: function () {
        sideS.$sidebarWrapper.niceScroll("destroy");
        this.customScrollFlag = false;
      },
    };
  sidebar.init();

  /*++++++++++++++++++++++++++++++++++++
		click event on ul.timeline titles
	++++++++++++++++++++++++++++++++++++++*/
  //$("ul.timeline").children().eq(0)
  //.find(".text").slideDown()
  //.addClass("open");

  $("ul.timeline")
    .on("click", "li", function () {
      $this = $(this);
      if ($this.hasClass("open")) {
        $this.find(".text").slideUp();
        $this.removeClass("open");
      } else {
        $this.find(".text").slideDown();
        $this.addClass("open");
        $this.siblings("li.open").find(".text").slideUp();
        $this.siblings("li").removeClass("open");
      }
    })
    .on("mouseenter", "li", function () {
      $this = $(this);
      var anim = new TweenLite($(this).find(".subject"), 0.4, {
        "padding-left": 20,
        paused: true,
      });
      $this.hasClass("open") || anim.play();
    })
    .on("mouseleave", "li", function () {
      var anim = new TweenLite($(this).find(".subject"), 0.2, {
        "padding-left": 0,
      });
    });

  /*++++++++++++++++++++++++++++++++++++
		ul-withdetails details show/hide
	++++++++++++++++++++++++++++++++++++++*/
  $("ul.ul-withdetails li")
    .find(".row")
    .on("click", function () {
      // $this = $(this);
      $(this).closest("li").find(".details").stop(true, true).animate(
        {
          height: "toggle",
          opacity: "toggle",
        },
        300
      );
    })
    .on("mouseenter", function () {
      $this = $(this);
      var anim = new TweenLite(
        $(this).closest("li").find(".imageoverlay"),
        0.4,
        { left: 0 }
      );
    })
    .on("mouseleave", function () {
      var anim = new TweenLite(
        $(this).closest("li").find(".imageoverlay"),
        0.2,
        { left: "-102%" }
      );
    });

  /*++++++++++++++++++++++++++++++++++++
		Publications page categorization
	++++++++++++++++++++++++++++++++++++++*/

  $("div#pub-grid")
    .mixitup({
      layoutMode: "list",
      easing: "snap",
      transitionSpeed: 600,
      onMixEnd: function () {
        $(".tooltips").tooltip();
      },
    })
    .on("click", "div.pubmain", function () {
      var $this = $(this),
        $item = $this.closest(".item");

      $item.find("div.pubdetails").slideToggle(
        function () {
          $this.children("i").toggleClass("icon-collapse-alt icon-expand-alt");
        },
        function () {
          $this.children("i").toggleClass("icon-expand-alt icon-collapse-alt");
        }
      );
    });

  $("#cd-dropdown").dropdownit({
    gutter: 0,
  });

  $("[name=cd-dropdown]").on("change", function () {
    var item = this.value;
    $("div#pub-grid").mixitup("filter", item);
  });

  /* Detect touch devices*/
  function isTouchSupported() {
    //check if device supports touch
    var msTouchEnabled = window.navigator.msMaxTouchPoints;
    var generalTouchEnabled = "ontouchstart" in document.createElement("div");

    if (msTouchEnabled || generalTouchEnabled) {
      return true;
    }
    return false;
  }
});
