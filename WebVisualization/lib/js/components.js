// Javascript for branded web components
	$(document).ready(function(){
		$.ajaxSetup({
		    timeout: 10000
		});
			// added YKimura 08-20-2015 for keyboard accessibility
            // hide megamenu when tabbed away from
            $(document).keyup(function(event) {
				if (event.which == 9 && !$(event.target).parent('.dropdown-menu li').length) {
					$(".dropdown-menu").slideUp("fast");
                }
            });

		// Load Twitter feed dynamically
		$('.twitter-feed').each(function() {
			var compName = $(this).attr('id');
	        $(this).find('.livefeed').html('<h4 class="loading" style="text-align:center; padding-top:20px;">Loading...</h4>').load('/twitter/index/'+compName, function( response, status, xhr ) {
			});
		});

		// Load Instagram feeds dynamically
		$('.instagram-feed').each(function() {
			var compName = $(this).attr('id');
	        $(this).find('.livefeed').html('<h4 class="loading" style="text-align:center; padding-top:20px;">Loading...</h4>').load('/instagram/index/'+compName, function( response, status, xhr ) {
//			console.log('STATUS: ' + xhr.status + " " + xhr.statusText );
			});
		});
		
		// Load Blog feed dynamically
		var blogComp = $('.blog-feed').attr('id');
		$('.blog-feed .block').html('<h4 class="loading" style="text-align:center; padding-top:20px;">Loading...</h4>').load('/blog/index/'+blogComp);

		// Load News feed dynamically
		var newsComp = $('.news-feed').attr('id');
		$('.news-feed .block').html('<h4 class="loading" style="text-align:center; padding-top:20px;">Loading...</h4>').load('/livenews/index/'+newsComp);
		
		// Large Carousel
	  var largeOwl = $("#carouselHome"); 
	  largeOwl.owlCarousel({
	
	      nav : true, // Show next and prev buttons
	      navText:[ "<span class='entypo chevron-thin-left'></span>", "<span class='entypo chevron-thin-right'></span>" ],
	      slideSpeed : 300,
	      paginationSpeed : 400,
	      scrollPerPage: true,
	      items : 1,
	      loop: true,
	      navElement:'button',
	      singleItem:true
	 
	  });
	  
	  // Header Carousel
	  var headerOwl = $("#carouselLanding");
	  headerOwl.owlCarousel({
	
	      nav : true, // Show next and prev buttons
	      navText:[ "<span class='entypo chevron-thin-left'></span>", "<span class='entypo chevron-thin-right'></span>" ],
	      slideSpeed : 300,
	      paginationSpeed : 400,
	      scrollPerPage: true,
	      items : 1,
	      loop: true,
	      navElement:'button',
	      singleItem:true
	 
	  });
	  
	  // Multi Item Carousel
	  var threeItemOwl = $("#carouselMultiItems");
	  threeItemOwl.owlCarousel({
	
	      nav : true, // Show next and prev buttons
	      navText:[ "<span class='entypo chevron-thin-left'></span>", "<span class='entypo chevron-thin-right'></span>" ],
	      slideSpeed : 300,
	      paginationSpeed : 400,
	      scrollPerPage: true,
	      singleItem:false,
	      items : 3,
	      loop: true,
	      itemsDesktop : [1199,3],
	      itemsDesktopSmall : [979,3],
	      itemsMobile : true
	      // "singleItem:true" is a shortcut for:
	      // items : 1, 
	      // itemsDesktop : false,
	      // itemsDesktopSmall : false,
	      // itemsTablet: false,
	      // itemsMobile : false
	 
	  });
	  
	  $('#og-more-toggle').click(function(){					   
			$('#ogDrawer').slideDown('fast');
			return false;
		});
		  	  
		// Modal Carousel
		$('.slideshow-modal').click(function(){
			$('#modalSlideshow').modal('show');
			return false;
		});
		
	// Modal Timeline Slideshow - added ykimura Nov 4, 2014
		$('.slideshow-modal').click(function(){
			var target_modal_id_str = $(this).data("target");
			$(target_modal_id_str).modal('show');
			$(target_modal_id_str).on('shown.bs.modal', function (e) {
				var thisID = target_modal_id_str.substring(16);
//				alert('entry id='+thisID);
				var modalOwl = $("#carouselModal-"+thisID);
				modalOwl.owlCarousel({		
		      nav : true, // Show next and prev buttons
		      navText:[ "<span class='entypo chevron-thin-left'></span>", "<span class='entypo chevron-thin-right'></span>" ],
		      slideSpeed : 300,
		      paginationSpeed : 400,
		      loop: true,
		      items : 1,
		      scrollPerPage: true,
		      singleItem:true		 
				});		  
			});
			return false;
		});

		// Thumbnail Grid with Expanding Captions
		var squareGrid = Grid( $('#og-grid') );
		squareGrid.init();
	
		var circleGrid = Grid( $('#og-grid-02') );
		circleGrid.init();
		
		$('.og-more-toggle').click(function(){			
			$(this).parent().siblings('.ogDrawer').slideDown('fast'); 		 
			return false;
		});
		
		// Activate video modal		
		$('.video-modal-trigger').click(function() {			
			var target_modal_id_str = $(this).data("target");
			$(target_modal_id_str).modal(options);
			var options = {
			    "backdrop" : "static",
				"show" :true,
				"keyboard" : true
			}
		  return false;
		});
		$('.shareemail').click(function(e){
			e.preventDefault();
			var vidURL = $(this).attr("name");
			var thisID = $(this).parents(".modal").attr("id").substr(10);
			$('#tellafriend'+thisID+' pre').append(vidURL);
			$('#tellafriend'+thisID).show();
			$('#video-container'+thisID).hide();
		});
		
		$('.shareemail-hero').click(function(e){
			e.preventDefault();
			var vidURL = $(this).attr("name");
			var vidTitle = $(this).parents().siblings().find('h4').html();
			$('#tellafriend-hero pre').append(vidURL);
			$('#tellafriend-hero').show();
			$('#video-container-hero').hide();
		});

      // loads the YouTube IFrame Player API code asynchronously.
	  var tag = document.createElement('script'); 
      tag.src = "https://www.youtube.com/iframe_api";
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
	
	$('.modal').on('hidden.bs.modal',function() {
		var thisID = $(this).attr('id');
		var video = $(this).find('.youtube').attr('id');
		var suffix = thisID.substr(10);
		if (thisID == 'videoModal') {
			$('#tellafriend-hero').hide();
			$("#video-container-hero").find("iframe").attr("src", $("#video-container-hero").find("iframe").attr("src"));
			$('#video-container-hero').show();
		} else if (thisID.indexOf('video') > -1) {
			$('#tellafriend'+suffix).hide();
			$('#video-container'+suffix).show();
			$("#video-container"+suffix).find("iframe").attr("src", $("#video-container"+suffix).find("iframe").attr("src"));
		}
	});

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
	var thisID = $(this).attr('href');
	if (thisID.indexOf('video') > -1) {
		var src = $('#'+thisID+' > .embed-container').find('iframe').attr('src'); 
		alert(src);
		$('#'+thisID).find('iframe').attr('src', ''); 
		$('#'+thisID).find('iframe').attr('src', src); 
//		alert(iframe.attr('src'));
//  var src = iframe.attr('src');
//  iframe.attr('src', '');
//  iframe.attr('src', src);
	}
});

	$('.sharefacebook').click(function(){
		var shareURL = $(this).attr('name');
	    var fbpopup = window.open("https://www.facebook.com/sharer/sharer.php?u="+shareURL, "fbshare", "width=600, height=400, scrollbars=no");
    	return false;
	});
  
	$('.sharetwitter').click(function(){
		var tweetURL = $(this).attr('name');
		var tweetText = $(this).closest('.modal-content').find('h4').text();
		window.open("https://twitter.com/intent/tweet?text="+tweetText+"&url="+tweetURL, "twshare", "width=600, height=400, scrollbars=no");
	});

  /* highlight active mega category */  
  $(function() {
	  	var pathArray = window.location.pathname.split( '/' );		
		var secondLevelLocation = '/'+pathArray[1];
	  	$('#\\'+secondLevelLocation+' a').eq(0).addClass('main_menu_selected');
	});
});
	

$(window).load(function () {
// Make all info graphics on a page the same height
// Make social media tab box panes the same height
//	  $('.social-tabbox').find('.tab-pane').equalHeightColumns();
});
$(window).resize( $.throttle( 250, function () {
	  
	  // Make social media tab box panes the same height
//	  $('.social-tabbox').find('.tab-pane').equalHeightColumns();
	  
} ));


      // function creates an <iframe> (and YouTube player)
      // after the API code downloads.
	 var players = {};
      function onYouTubeIframeAPIReady() {
		var videos = document.getElementsByClassName('youtube');
		for (var i = 0; i < videos.length; ++i) {
			var thisid = videos[i].id;
			if (thisid.indexOf("_time_") == -1) {
				var videoid = thisid;
				players[i] = new YT.Player(videoid, {
					height: '1280',
					width: '720',
					videoId: videoid,
					playerVars: { 'autoplay': 0, 'controls': 2, 'modestbranding': 1, 'showinfo': 0, 'ohide': 1, 'enablejsapi': 1, 'wmode':'transparent' }
				});
			} else {
//timeline videos are identified by category_url
				var n = thisid.indexOf("_time_");
				var videoid = thisid.substr(n+6);
				players[i] = new YT.Player(thisid, {
					height: '1280',
					width: '720',
					videoId: videoid,
					playerVars: { 'autoplay': 0, 'controls': 2, 'modestbranding': 1, 'showinfo': 0, 'ohide': 1, 'enablejsapi': 1, 'wmode':'transparent' }
				});
			}
    	}
	  }
	  
		// JavaScript Document
		