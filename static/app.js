
// player

var player = $("#player")[0];
var playpause = $("#playpause");
var previous = $("#previous");
var next = $("#next");
var progress = $("#progress");
var bar = $("#bar");
var volume = $("#volume");
var volumeSlider = $("#volume-slider");
var volumeSliderBar = $("#volume-slider-bar");

var shuffle = false;
var repeat = false;
var unmutedVolume = 0.8;

var clock;

var playPrevious = function() {
    var previous = $(".playing").prev();
    if(previous.length === 0) { previous = $(".playing").siblings().last(); }
    playTrack(previous);
};

var playNext = function() {
    if(repeat) {
        playTrack($(".playing"));
        return;
    }
    var tracks = $("table.now-playing tbody .track:not(.playing)");
    if(shuffle) {
        var random = Math.floor(Math.random()*tracks.length);
        playTrack(tracks.eq(random));
        return;
    }
    var next = $(".playing").next();
    if(!next || next.length === 0) { next = tracks.first(); }
    playTrack(next);
};

var updateProgress = function() {
    var percentage = ((player.currentTime / player.duration) * 100) + "%";
    bar.width(percentage);
    // convert current position float into mm:ss format
    var m = Math.floor(player.currentTime / 60);
    var s = Math.floor(player.currentTime - (m * 60));
    var readableTime = m + ":" + (s < 10 ? ("0"+s) : s);
    $(".now-playing-info .current-time").html(readableTime);
};

player.addEventListener("play", function(){
    $("#playpause i").removeClass("fa-play").addClass("fa-pause");
    // html5 spec only demands timeUpdate every 200ms or so
    // looks really laggy, so lets update it more often
    clock = setInterval(function() { updateProgress(); }, 100);
});

player.addEventListener("pause", function(){
    $("#playpause i").removeClass("fa-pause").addClass("fa-play");
    clearInterval(clock);
});

player.addEventListener("ended", playNext);

player.addEventListener('timeupdate', function() {
    // we still also want to update the track progress when the timeupdate
    // fires, as it is called instantly when the user seeks for instance
    updateProgress();
});

progress.click(function(e) {
    // work out where in the progress bar we have clicked and skip
    // to that time
    var pos = (e.pageX  - $(this).offset().left) / $(this).outerWidth();
    var time = pos * player.duration;
    player.currentTime = time;
});

// volume

var mute = function() {
    unmutedVolume = player.volume;
    player.volume = 0;
};

var unmute = function() {
    player.volume = unmutedVolume;
}; 

var updateVolume = function(volume) {
    // handle the UI for the volume bar, toggling icons for muting
    // and adjusting the length of the volume bar
    if(volume === 0) {
        $("#volume i").removeClass("fa-volume-up").addClass("fa-volume-off");
        volumeSliderBar.addClass("inactive");
    } else {
        $("#volume i").removeClass("fa-volume-off").addClass("fa-volume-up");
        volumeSliderBar.removeClass("inactive");
        volumeSliderBar.width((volume * 100) + "%");
    }
};

volume.click(function(e) {
    if(player.volume === 0) { unmute(); }
    else { mute(); }
    updateVolume(player.volume);
});

volumeSlider.click(function(e) {
    // work out where in the volume bar we have clicked
    var volume = (e.pageX - $(this).offset().left) / $(this).outerWidth();
    // round up to nearest 0.05 to make UI look a bit better
    volume = Math.ceil(volume/0.05)*0.05;
    player.volume = volume;
    updateVolume(volume);
});

playpause.click(function(e) {
    if(!player.getAttribute("src")) { return playNext(); }
    if(player.paused) { player.play(); }
    else { player.pause(); }
});

previous.click(function(e) {
    playPrevious();
});

next.click(function(e) {
    playNext();
});

$("#shuffle").click(function(e) {
    shuffle = !shuffle;
    $(this).toggleClass("active");
});

$("#repeat").click(function(e) {
    repeat = !repeat;
    $(this).toggleClass("active");
});

var updateNowPlaying = function(track) {
    var artist = track.data("artist");
    var title = track.data("title");
    var album = track.data("album");
    var duration = track.data("duration");
    $(".now-playing-info .title").html(title);
    $(".now-playing-info .artist").html(artist);
    $(".now-playing-info .album").html(album);
    $(".now-playing-info .duration").html(duration);
    $(".now-playing-info .current-time").html("0:00");
    track.data("playing", true);
    $(".playing").removeClass("playing").removeClass("success");
    track.addClass("playing").addClass("success");
};

var playTrack = function(track) {
    player.pause();
    player.setAttribute('src', "/music/track/"+track.data("id"));
    player.load();
    updateNowPlaying(track);
    player.play();
};

var renderTrackQueryResults = function(data) {
    if(!data.tracks) { return; }
    $("table.results tbody").html("");
    if(!data.tracks.length) { 
        $(".search-no-results").show();
        return;
    }
    // append our results to the DOM
    $.each(data.tracks, function(i, track) {
        $("table.results tbody").
            append($("<tr>").
                append($("<td>").text(track.title)).
                append($("<td>").text(track.artist)).
                append($("<td>").text(track.album)).
                append($("<td>").text(track.duration)).
                data("id", track.id).
                data("artist", track.artist).
                data("title", track.title).
                data("album", track.album).
                data("duration", track.duration).
                addClass("track"));
    });
    gotoSection("results");
};

// search

$("#search").submit(function(e) {
    e.preventDefault();
    var query = $(".search-input").val();
    if(!query) { return; }
    var api = "/search";
    $.getJSON(api, {
        query: query
    }, renderTrackQueryResults);
});

// playlists

$("table.now-playing").on("click", ".track", function(e) {
    playTrack($(this));
});

var updateNowPlayingOnServer = function() {
    var playlist = 1;
    var api = "/playlist/tracks/"+playlist;
    var trackIDs = [];
    $("table.now-playing tbody").children().each(function() {
        trackIDs.push($(this).data("id"));
    });
    $.post(api, {
        tracksJSON: JSON.stringify({tracks: trackIDs})
    });
};

$("table.results").on("click", ".track",  function(e) {
    $("table.now-playing tbody").html("");
    $("table.results tbody").children(".track").each(function() {
        $(this).clone(true).appendTo("table.now-playing tbody");
    });
    updateNowPlayingOnServer();
    gotoSection("now-playing");
    playTrack($("table.now-playing .track:eq("+$(this).index()+")"));
});

$("table.user-playlist").on("click", ".track", function(e) {
    $("table.now-playing tbody").html("");
    $("table.user-playlist tbody").children(".track").each(function() {
        $(this).clone(true).appendTo("table.now-playing tbody");
    });
    updateNowPlayingOnServer();
    gotoSection("now-playing");
    playTrack($("table.now-playing .track:eq("+$(this).index()+")"));
});

$(".playlist tbody").sortable({
    items: "tr",
    cursor: "move",
    update: function(event, ui) {
        // when we have moved a track and the position changes
        // we need to send this information to the server
        // so that it can store the new order in the playlist
        var playlist = $(this).data("playlist");
        var api = "/playlist/tracks/"+playlist;
        var trackIDs = [];
        $(this).children().each(function() {
            trackIDs.push($(this).data("id"));
        });
        $.post(api, {
            tracksJSON: JSON.stringify({tracks: trackIDs})
        }, function(response) {
            ui.item.effect("highlight", {}, 1500);
        }, 'json');
    }
}).disableSelection();

// sidebar 

var gotoSection = function(section) {
    // to switch views we toggle active classes on the various sections
    // and the links to various sections
    $(".search-no-results").hide(); 
    $(".section-links .active").removeClass("active");
    $(".playlist-links .active").removeClass("active");
    $(".section-links ."+section).parent().addClass("active");
    $(".section.active").removeClass("active");
    $(".section."+section).addClass("active");
    // scroll to the top else we may be half-way down the new view
    window.scrollTo(0,0);
};

$(".section-link").on("click", function(e) {
    e.preventDefault();
    var section = $(this).data("section");
    gotoSection(section);
});

$("#new-playlist-button").on("click", function(e) {
    e.preventDefault();
    $(".new-playlist-ui").show();
    $(".new-playlist-input").select();
});

$("#new-playlist").submit(function(e) {
    e.preventDefault();
    var name = $(".new-playlist-input").val();
    if(!name) { return; }
    var api = "/playlist/new";
    $.post(api, {
        name: name
    }, function(response) {
        // when server confirms adding the playlist,
        // append it to the playlist list
        // we must wait for the server to respond or else
        // we don't know the id of the playlist and therefore cannot use it
        // to add tracks
        $(".playlist-links").
            append($("<li>").
                append($("<a>").
                    data("id", response.id).
                    data("section", "playlist").
                    attr("href", "#playlist").
                    addClass("playlist-link").
                    html('<i class="fa sidebar-icon fa-file-audio-o"></i> '+response.name)).
                addClass("playlist-item").
                droppable(playlistDroppableOptions));
        $(".new-playlist-ui").hide();
    }, 'json');
});

$(".delete-playlist").on("click", function(e) {
    var playlist = $("table.user-playlist tbody").data("playlist");
    if(playlist == 1) { return; }
    var api = "/playlist/delete";
    $.post(api, {
        id: playlist
    }, function(response) {
        $(".playlist-link").filter(function() {
            return $(this).data("id") == playlist;
        }).remove();
        gotoSection("now-playing");
    });
});

$(".playlist-links").sortable({
    items: "li",
    cursor: "move",
    update: function(event, ui) {
        var api = "/playlist/sort";
        var playlists = [];
        $(".playlist-links").find("a").each(function(index) {
            playlists.push({
                sort: index,
                id: $(this).data("id")
            });
        });
        $.post(api, {
            playlistsJSON: JSON.stringify({playlists: playlists})
        });
    }
});

var playlistDroppableOptions = {
    accept: ".track",
    hoverClass: "active",
    tolerance: "pointer", // want to base dropping on where mouse cursor is
    drop: function(event, ui) {
        var api = "/playlist/add";
        var playlist = $(this);
        $.post(api, {
            playlist: $(this).children("a").first().data("id"),
            track: ui.draggable.data("id")
        }, function(data) {
            // show an effect to confirm when action is confirmed by the server
            playlist.effect("highlight", {}, 1500);
        });
    }
};

$(".playlist-item").droppable(playlistDroppableOptions);

var nowPlayingDroppableOptions = {
    accept: ".track",
    hoverClass: "active",
    tolerance: "pointer",
    drop: function(event, ui) {
        var api = "/playlist/add";
        $.post(api, {
            playlist: $(this).children("a").first().data("id"),
            track: ui.draggable.data("id")
        }, function(data) {
            var trackClone = ui.draggable.clone(true);
            $("table.now-playing tbody").append(trackClone);
            $(this).effect("highlight", {}, 1500);
        });
    }
};

$(".now-playing-drop").droppable(nowPlayingDroppableOptions);

var renderPlaylist = function(data) {
    $("table.user-playlist tbody").html("");
    $("table.user-playlist tbody").data("playlist", data.id);
    $.each(data.tracks, function(i, track) {
        // append tracks to the dom displaying them in the playlist table
        $("table.user-playlist tbody").
            append($("<tr>").
                append($("<td>").text(track.title)).
                append($("<td>").text(track.artist)).
                append($("<td>").text(track.album)).
                append($("<td>").text(track.duration)).
                append($("<td>").
                    append($("<a>").
                        append($("<i>").
                            addClass("fa").addClass("fa-remove")).
                        addClass("remove-track"))).
                data("id", track.id).
                data("pt", track.pt).
                data("artist", track.artist).
                data("title", track.title).
                data("album", track.album).
                data("duration", track.duration).
                addClass("track"));
    });
    gotoSection("user-playlist");
};

$(".playlist-links").on("click", ".playlist-link", function(e) {
    e.preventDefault();
    $(".playlist-item.active").removeClass("active");
    var api = "/playlist/tracks/"+$(this).data("id");
    var playlistItem = $(this).parent();
    $.getJSON(api, {}, function(data) {
        renderPlaylist(data);
        playlistItem.addClass("active");
    });
});

$("table").on("click", ".remove-track", function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();
    var track = $(this).parent().parent();
    var playlist = $(this).parent().parent().parent().data("playlist");
    var pt = track.data("pt");
    var api = "/playlist/remove";
    $.post(api, {
        pt: pt
    }, function(response) {
        track.hide("fade", {}, 200);
    });
});

// library

$(".artist-filter").on("click", function(e) {
    e.preventDefault();
    $(".artist-filter.active").removeClass("active");
    $(this).addClass("active");
    var artist = $(this).data("artist");
    if(!artist) {
        $(".album-filter").show();
        $(".album-filter.album-filter-all").removeData();
    } else {
        $(".album-filter").hide();
        $(".album-filter.album-filter-all").data("artist", artist);
        $(".album-filter.album-filter-all").show();
        $(".album-filter").filter(function() {
            return $(this).data("artist") === artist;
        }).show();
    }
    window.scrollTo(0,0);
});

$(".album-filter").on("click", function(e) {
    e.preventDefault();
    var api = "/tracks";
    $.getJSON(api, {
        artist: $(this).data("artist"),
        album: $(this).data("album")
    }, renderTrackQueryResults);
});

