

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
        try {
            func();
        } catch (error) {
            console.error("failed new_data_callback");
            console.error(error);
        }
    }
});


function update_slate(update, meta) {
    // console.log(typeof(update))
    // console.log(typeof(meta))
    // console.log(update, meta)

    if ("valu" in meta){
        meta["valu"] = update
        return
    }

    for (key in meta) {
        update_slate(update[key], meta[key])
    }
    
}

function send_command(cmd, target = "cmd") {
    //TODO: check if it is editable

    if(Cookies.get('auth') ){
      out = { "auth": Cookies.get('auth')}
      out[target] = cmd;
      socket.emit("cmd", out);
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