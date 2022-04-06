

var socket = io.connect({ transports: ['websocket'] });

//elements can add themselves to list to update on new data
new_data_callbacks = [() => { console.log("got data", slate) }];
slate = {};

socket.on("new", (data) => {
    slate = data;
    for (func of new_data_callbacks) {
        func();
    }
});

function send_command(params) {
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