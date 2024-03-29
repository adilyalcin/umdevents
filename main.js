
function updateSearchText_When(){
	targetDom = $('#header_when_detail');
	switch($('input[name=when_choice]:checked').val()){
	case "1": targetDom.text("Now"); break;
	case "2": targetDom.text("At "+$("#when_hours_from_now").val()+" hours from now"); break;
	case "3": targetDom.text($("#when_rel_day_select").val()+", in the "+
							 $("#when_rel_hour_select").val()); break;
	case "4": targetDom.text("From "+$("#when_date_range_from").val()+" to "+$("#when_date_range_to").val()); break;
	case "5": targetDom.text("In future"); break;
	case "6": targetDom.text("In past"); break;
	};
	// update sub-texts
	$("#when_sub1").text($("#when_hours_from_now").val());
	$("#when_sub2").text($("#when_rel_day_select").val());
	$("#when_sub3").text($("#when_rel_hour_select").val());
	$("#when_sub4").text($("#when_date_range_from").val());
	$("#when_sub5").text($("#when_date_range_to").val());
}

function updateSearchText_Where(){
	targetDom = $('#header_where_detail');
	switch($('input[name=where_choice]:checked').val()){
	case "1": targetDom.text("Near me ("+$("#where_near_feet").val()+" feet)"); break;
	case "2": targetDom.text("Location: "+selectedLoc+" ("+$("#where_building_feet").val()+" feet)"); break;
	case "3": targetDom.text("Anywhere in campus"); break;
	};
	// update sub-texts
	$("#where_sub1").text($("#where_near_feet").val());
	$("#where_sub2").text(selectedLoc);
	$("#where_sub3").text((selectedLoc=="?")?"?":$("#where_building_feet").val())
}
		
$( window.document ).bind( "mobileinit", function() {
//	alert("mobileinit");
});

var monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function twoDigits(i){ if(i<10) return "0"+i; return i; }
function getDate(d){ return d.getDate()+" "+monthNames[d.getMonth()]+" "+d.getFullYear(); }
function getHour(d){ return twoDigits(d.getHours())+":"+twoDigits(d.getMinutes()) }

function eventMultiDay(e){
	return !(
		(e.dateBegin.getDate() == e.dateEnd.getDate()) &&
		(e.dateBegin.getFullYear() == e.dateEnd.getFullYear()) &&
		(e.dateBegin.getMonth() == e.dateEnd.getMonth())
	);
}

function eventDate(e){
	var s;
	// if begin and end date is the same, display the same date, only change start/end time
	if(!eventMultiDay(e)){
		s = "<strong>"+getDate(e.dateBegin)+"</strong> "+
			getHour(e.dateBegin) + " - " + getHour(e.dateEnd);
	} else {
		s = "<strong>"+getDate(e.dateBegin)+"</strong> "+getHour(e.dateBegin) + " - " + 
			"<strong>"+getDate(e.dateEnd)+"</strong> "+getHour(e.dateEnd);
	}
	return s;
}

function eventMultiDay(e){
	return true;
	var dateBegin = new Date(e["startDateTime"]);
	var dateEnd   = new Date(e["endDateTime"]);
	return 
}

var buildings_loaded = false;
loadBuildings = function() {
	if(buildings_loaded) return;
	// create building list
	$.getJSON('./json/buildings_all.json', function(data) {
		var trgt = $("#where_building_list_ul");
		// alert(data.length); //uncomment this for debug
		for (var i = 0; i < data.length; i++) {
			trgt.append("<li><a href=\"#\">"+data[i]["name"]+"</a></li>");
		}
		trgt.listview("refresh");
		$('input[data-type="search"]').trigger("change");
		buildings_loaded = true;
	});
}

// from http://stackoverflow.com/questions/10671092/passing-data-between-pages-with-jquery-mobile
function parseURLParams(url) {
  var queryStart = url.indexOf("?") + 1;
  var queryEnd   = url.indexOf("#") + 1 || url.length + 1;
  var query      = url.slice(queryStart, queryEnd - 1);
  var params     = {};

  if (query === url || query === "") return params;

  var nvPairs = query.replace(/\+/g, " ").split("&");

  for (var i=0; i<nvPairs.length; i++) {
    var nv = nvPairs[i].split("=");
    var n  = decodeURIComponent(nv[0]);
    var v  = decodeURIComponent(nv[1]);
    if ( !(n in params) ) params[n] = [];
    params[n].push(nv.length === 2 ? v : null);
  }
  return params;
}

function init_event_page(){
	$("#event_info").on('pageshow', function (event, ui) {
		var eventID=0;
		var params=parseURLParams(window.location.href);
		if(params["id"]) eventID = params["id"];
		else eventID = eventId;
//		alert("eventId:"+eventID);	
		// read event data
		$.getJSON('./json/event?id='+eventID, function(data) {
			data.dateBegin = new Date(data["startDateTime"]);
			data.dateEnd   = new Date(data["endDateTime"]);
			$("#event_title").text(data["title"]);
			$("#event_description").text(data["description"]);
			if(data["eventWebsite"]){
				$("#event_webpage").html(
					"<br/><strong>Visit <a href=\""+data["eventWebsite"]+"\" target=\"_blank\">this page</a> for more information.</strong>");
			}
			{	// Location
				$("#event_location").text(data["locationName"]);
				if(data["locationRoomNumber"])
					$("#event_locationroom").text(data["locationRoomNumber"]);
				else
					$("#event_locationroom").text("");
				if(data["locationCode"]){
					$("#event_info_maplink").css('display',((data["locationCode"])?"block":"none"));
					$("#event_info_maplink").html(
						"<a href=\"http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code="+
							data["locationCode"].toUpperCase()+"\">Click for map</a>");
				}
				event_info_maplink
			}
			$("#event_audience").text(data["audience"]);
			// categories, loop through (TODO)
			//var cat = "";
			//alert(data["categories"].length);
			//for (var i = 0; i < data["categories"].length; i++) {
			//	alert("sds");
			//	cat+=data["categories"][i][1];
			//}
			$("#event_categories").text(data["categories"]["category"]);
			// show date
			{
				$("#event_time").html(eventDate(data));
			}
			
			$("#event_info_multiday").css('display',(eventMultiDay(data)?"block":"none"));
		});
	});
//	alert("eventId: (captured at event page):"+eventId);
}

updateCatDisplay = function(){
	// select/deselct all sub-categories. If no subcategory exist, has no effect.
	$("INPUT[class~='sub_"+this.id+"']").prop('checked', this.checked).checkboxradio("refresh");
	// update categories
	var cats= [
		[1,2,6],
		[7,8,12],
		[13,14,15],
		[16,17,18],
		[19,20,25]
	];
	for(var c=0;c<cats.length;c++){
		var show_et=false;
		for(var i=cats[c][1]; i<=cats[c][2]; i++) {show_et = show_et || $('#et_'+i).prop('checked'); }
		$("input[class~='et_"+cats[c][0]+"']").prop('checked',(show_et!=false)).checkboxradio("refresh");
	//	var x=$("input[class~='et_1']").parent().children().children().children('span[class~=\'ui-icon\']');
	//	x.css("background-color","transparent");
		$("fieldset[class~='sub_et_"+cats[c][0]+"']").css('display',((show_et==false)?'none':'block'));
	}
}

// detch the building data & create dom elements only when building selection is to be displayed
function init_page_main() {
	selectedLoc = "?";
	$("#where_building_dialog").on("pageshow",loadBuildings);
	
	$("#profile_store_button").on("click", function() {
		$.mobile.changePage('#profile_store_dialog',   { transition: "pop"});
	});
	
	// detect change of when selection
	$("[name=when_choice]").change(function() {
		switch($('input[name=when_choice]:checked').val()){
		case "1": break;
		case "2": $.mobile.changePage('#when_in_x_hours_dialog',   { transition: "pop"}); break;
		case "3": $.mobile.changePage('#when_rel_day_hour_dialog', { transition: "pop"}); break;
		case "4": $.mobile.changePage('#when_date_range_dialog',   { transition: "pop"}); break;
		};
		updateSearchText_When();
	});
	
	// detect change of where selection
	$("[name=where_choice]").change(function(){
		switch($('input[name=where_choice]:checked').val()){
		case "1": $.mobile.changePage('#where_me_feet_dialog',  { transition: "pop"}); break;
		case "2": $.mobile.changePage('#where_building_dialog', { transition: "pop"}); break;
		}
		updateSearchText_Where();
	});
	
	$("[name=when_hours_from_now]").change(function(){
		updateSearchText_When();
	});
		$("#when_rel_day_hour_dialog").on("pagehide", function() {
		updateSearchText_When();
	});
	$("#when_date_range_dialog").on("pagehide", function() {
		updateSearchText_When();
	});
	$("#where_me_feet_dialog").on("pagehide", function() {
		updateSearchText_Where();
	});
	$("#where_building_dialog").on("pagehide", function() {
		updateSearchText_Where();
	});
	
	$("#where_building_list_ul").on('click', 'li', function() {
		selectedLoc = this.textContent;
		$('input[data-type="search"][id!="searchinput2"]').val(this.textContent);
		$('input[data-type="search"][id!="searchinput2"]').trigger("change");
	});
	
	$("#search_button").on('click', function() {
		$("#event_listing_collapsable").trigger('expand');
		$("#search_setting_collapsable").trigger('collapse');
		updateEventList();
	});
	
	// set todays date by default on date selection option
	{	var fullDate = new Date()
		//convert month to 2 digits
		var twoDigitMonth = ((fullDate.getMonth().length+1) === 1)? (fullDate.getMonth()+1) : '0' + (fullDate.getMonth()+1);
		var currentDate = fullDate.getFullYear() + "-" + twoDigitMonth + "-" + fullDate.getDate();
		$("#when_date_range_from").val(currentDate);
		$("#when_date_range_to").val(currentDate);
	}
	
	// capture category click updates
	$(".et_x").click(updateCatDisplay);
	updateCatDisplay();
	
	$("#search_I_liked_id").click(function(){
		var bttn=$("#search_I_liked_id");
		alert(bttn.data("theme"));
		if (bttn.data("theme") == "a") {
			alert("sdsds");
			bttn.buttonMarkup({ theme: 'c' }).button('refresh');
		} else {
			bttn.buttonMarkup({ theme: 'a' }).button('refresh');
		}
	});

	updateSearchText_When();
	updateSearchText_Where();
}

function updateEventList(){
	// create event list
	$.getJSON('./json/search', function(data) {
		var trgt = $("#event_listing_ul");
		// alert(data.length); //uncomment this for debug
		for (var i = 0; i < data.length; i++) {
			var e = data[i];
			e.dateBegin = new Date(e["startDateTime"]);
			e.dateEnd   = new Date(e["endDateTime"]);
			var t = 
				"<li data-theme=\"";
			if(!e["liked"]) 
				t+="c";
			else
				t+="e";
			t+="\">" +
					"<a href=\"event.html\" data-transition=\"slide\" "+
					"onclick=\"eventId=" +e["id"]+"\""+
					">";
			t+="<img src=\"event_photo.png\">";
//			t+="<div class=\"customTableLayout\"><a data-role=\"button\" data-icon=\"check\" data-inline=\"true\" data-iconpos=\"left\" >Like</a></div>";
			t+= "<h3>" + e["title"];
			if(e["liked"]) t+=" (liked)";

			t+="</h3>"+
						"<p>" + eventDate(e) + "</p>"+
						"<p>" + e["locationName"];
			if(e["locationRoomNumber"])	t += " - " + e["locationRoomNumber"];
			t+= "</p>";
			t+="</a>"+"</li>";
			trgt.append(t);
		}
		trgt.listview("refresh");
	});
	
}
