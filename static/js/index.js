const bg_tag = document.getElementById("bg");
const thumb_tag = document.getElementById("thumb")
const audio_tag = document.getElementById("audio");
const preview_tag = document.getElementById("preview");
const video_tag = document.getElementById("video");
const b_tag = document.getElementById("b");
const d_tag = document.getElementById("d");
const osu_tag = document.getElementById("osu");

function bg(arg) {
    //arg.preventDefault();
    const get_id = prompt("+BeatmapSetID or BeatmapID")
    if (get_id === null | get_id === "") {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    /* else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    } */
    else {
        bg_tag.href = `${document.location.href}bg/${get_id}`
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
        thumb_tag.href = `${document.location.href}thumb/${get_id}l.jpg`
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
    /* else if (isNaN(get_id) === true) {
        alert("숫자를 입력하세요! \nEnter Number!")
        location.reload(true);
    } */
    else {
        audio_tag.href = `${document.location.href}audio/${get_id}`
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

bg_tag.addEventListener("click", bg);
thumb_tag.addEventListener("click", thumb);
audio_tag.addEventListener("click", audio);
preview_tag.addEventListener("click", preview);
video_tag.addEventListener("click", video);
b_tag.addEventListener("click", b);
d_tag.addEventListener("click", d);
osu_tag.addEventListener("click", osu);