const bg_tag = document.getElementById("bg");
const thumb = document.getElementById("thumb")
const bancho_userid = document.getElementById("banchouserid");
const bancho_username = document.getElementById("banchousername");

function bg(arg) {
    //arg.preventDefault();
    const get_id = prompt("+BeatmapSetID or BeatmapID")
    if (get_id === null) {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    /* else if (isNaN(get_id) === true) {
        alert("당신의 ID(숫자)를 입력하세요! \nEnter your ID (number)!")
        location.reload(true);
    } */
    bg_tag.href = `https://media.redstar.moe/bg/${get_id}`

}

function BanchoUserId(arg) {
    //arg.preventDefault();
    const get_id = prompt("당신의 Bancho ID를 적어주세요! \nPlease write down your Bancho ID!")
    if (get_id === null) {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    else if (isNaN(get_id) === true) {
        alert("당신의 ID(숫자)를 입력하세요! \nEnter your ID (number)!")
        location.reload(true);
    }
    bancho_userid.href = `https://a.redstar.moe/bancho/id/${get_id}`

}

function BanchoUserName(arg) {
    //arg.preventDefault();
    const get_id = prompt("당신의 Bancho Name를 적어주세요! \nPlease write down your Bancho Name!")
    if (get_id === null) {
        alert("정확하게 입력하세요! \nPlease enter it correctly!");
        get_id = "";
        location.reload(true);
    }
    bancho_username.href = `https://a.redstar.moe/bancho/u/${get_id}`

}

bg_tag.addEventListener("click", bg);
bancho_userid.addEventListener("click", BanchoUserId);
bancho_username.addEventListener("click", BanchoUserName);