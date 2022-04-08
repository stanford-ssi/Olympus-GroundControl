

var socket = io.connect({ transports: ['websocket'] });

//elements can add themselves to list to update on new data
new_data_callbacks = [];
// new_data_callbacks = [() => { console.log("got data", slate) }];
slate = {};

socket.on("new", (update) => {
    update_slate(update, slate)
    for (func of new_data_callbacks) {
        func();
    }
});


function update_slate(update, meta) {
    // console.log(update, meta)

    if ("value" in meta){
        meta["value"] = update
        return
    }

    for (key in meta) {
        update_slate(update[key], meta[key])
    }
    
}

function send_command(params) {
    socket.emit("cmd", params);
}

function get_data(path) {
    console.log(path)
    path = path.split(".")
    if (path[0] != "slate") {
        return null
    }
    path.shift()
    node = slate
    for (item of path) {
        node = node[item]
    }
    return node
}