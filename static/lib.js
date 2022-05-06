

var socket = io.connect({ transports: ['websocket'] });

//elements can add themselves to list to update on new data
new_data_callbacks = [];
// new_data_callbacks = [() => { console.log("got data", slate) }];
slate = {};

iter = 0

socket.on("new", (update) => {
    iter += 1;
    if(iter % 10 == 0) {
        // console.log("here");
        // console.log(update);
    }
    // console.log(update)
    update_slate(update, slate)
    for (func of new_data_callbacks) {
        func();
    }
});


function update_slate(update, meta) {
    // console.log(typeof(update))
    // console.log(typeof(meta))
    // console.log(update, meta)

    if ("value" in meta){
        meta["value"] = update
        return
    }

    for (key in meta) {
        update_slate(update[key], meta[key])
    }
    
}

function send_command(cmd) {
    //TODO: check if it is editable
    cmd['auth'] = Cookies.get('auth')

    if(Cookies.get('auth') ){
      socket.emit("cmd", cmd);
    }else{
      alert("Observers can't send commands");
    }

}

function get_data(path) {
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