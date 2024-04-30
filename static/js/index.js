const bg_tag = document.getElementById("bg");
const thumb_l_tag = document.getElementById("thumb_l")
const thumb_tag = document.getElementById("thumb")
const audio_tag = document.getElementById("audio");
const preview_tag = document.getElementById("preview");
const video_tag = document.getElementById("video");
const b_tag = document.getElementById("b");
const d_tag = document.getElementById("d");
const osu_tag = document.getElementById("osu");
const web_maps_tag = document.getElementById("/web/maps/")
//const remove_tag = document.getElementById("remove")
const filesinfo_tag = document.getElementById("filesinfo")
const filesinfo2_tag = document.getElementById("filesinfo2")
const replayparser_tag = document.getElementById("replayparser")

function bg(arg) {
    //arg.preventDefault();
    const get_id = prompt("+BeatmapSetID or BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else {
        bg_tag.href = `${document.location.href}bg/${get_id}`
    }
}

function thumb_l(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        thumb_l_tag.href = `${document.location.href}thumb/${get_id}l.jpg`
    }
}

function thumb(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        thumb_tag.href = `${document.location.href}thumb/${get_id}.jpg`
    }
}

function audio(arg) {
    //arg.preventDefault();
    const get_id = prompt("+BeatmapSetID or BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else {
        const mods = prompt("mods (DT, NC, HF)\nno mods = Skip This")
        if (mods === null | mods === "" | mods === "no") {
            audio_tag.href = `${document.location.href}audio/${get_id}`
        }
        else {
            audio_tag.href = `${document.location.href}audio/${get_id}${mods}`
        }
    }
}

function preview(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        preview_tag.href = `${document.location.href}preview/${get_id}.mp3`
    }
}

function video(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        video_tag.href = `${document.location.href}video/${get_id}`
    }
}

function b(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        b_tag.href = `${document.location.href}b/${get_id}`
    }
}

function d(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        d_tag.href = `${document.location.href}d/${get_id}`
    }
}

function osu(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        osu_tag.href = `${document.location.href}osu/${get_id}`
    }
}

function web_maps(arg) {
    //arg.preventDefault();
    const filename = prompt(".osu full filename")
    if (filename === null | filename === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        filename = "";
        location.reload(true);
    }
    else {
        web_maps_tag.href = `${document.location.href}web/maps/${filename}`
    }
}

/* function remove(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        const key1 = prompt("key1")
        if (key1 === null | key1 === "") {
            alert("정확하게 입력하세요! \nPlease enter it correctly!");
            key1 = "";
            location.reload(true);
        }
        else {
            remove_tag.href = `${document.location.href}remove/${get_id}?key=${key1}`
        }
    }
    
} */

function filesinfo(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        filesinfo_tag.href = `${document.location.href}filesinfo/${get_id}`
    }
}

function filesinfo2(arg) {
    //arg.preventDefault();
    const get_id = prompt("BeatmapSetID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    }
    else {
        const get_id2 = prompt("BeatmapID")
        if (get_id2 === null | get_id2 === "") {
            alert("정확하게 입력하세요! \nPlease enter it correctly!");
            get_id2 = "";
            location.reload(true);
        }
        else if (isNaN(get_id2) === true) {
            alert("숫자를 입력하세요! \nEnter Number!")
            location.reload(true);
        }
        else {
            filesinfo2_tag.href = `${document.location.href}filesinfo/${get_id}/${get_id2}`
        }
    }
}

function replayparser(arg) {
    //arg.preventDefault();
    const get_id = prompt("정보 = info \nrawReplay 다운로드 = dl \n\n info = info \nrawReplay download = dl")
    if (get_id === "info") {
        replayparser_tag.href = `${document.location.href}replayparser`
    }
    else if (get_id === "dl") {
        replayparser_tag.href = `${document.location.href}replayparser?dl`
    }
    else {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
}

bg_tag.addEventListener("click", bg);
thumb_l_tag.addEventListener("click", thumb_l);
thumb_tag.addEventListener("click", thumb);
audio_tag.addEventListener("click", audio);
preview_tag.addEventListener("click", preview);
video_tag.addEventListener("click", video);
b_tag.addEventListener("click", b);
d_tag.addEventListener("click", d);
osu_tag.addEventListener("click", osu);
web_maps_tag.addEventListener("click", web_maps)
//remove_tag.addEventListener("click", remove)
filesinfo_tag.addEventListener("click", filesinfo)
filesinfo2_tag.addEventListener("click", filesinfo2)
replayparser_tag.addEventListener("click", replayparser)