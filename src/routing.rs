


use warp::Filter;

#[tokio::main]
async fn main() {
    // GET /hello/warp => 200 OK with body "Hello, warp!"
    let hello = warp::path!("hello" / String)
        .map(|name| format!("Hello, {}!", name));

    let css = warp::path("style.css")
        .and(warp::fs::file("./static/style.css"));

    let main = warp::get().and(warp::path::end())
        .and(warp::fs::file("./static/main.html"));

    let routes = main.or(css).or(hello);

    warp::serve(routes)
        .run(([127, 0, 0, 1], 7878))
        .await;
}

// use std::io::prelude::*;
// use std::net::TcpListener;
// use std::net::TcpStream;

// use std::fs;

// fn main() {
//     let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

//     for stream in listener.incoming() {
//         let stream = stream.unwrap();

//         handle_connection(stream);
//     }
// }


// // --snip--

// fn handle_connection(mut stream: TcpStream) {
//     let mut buffer = [0; 1024];
//     stream.read(&mut buffer).unwrap();

//     let contents = fs::read_to_string("html/main.html").unwrap();

//     let response = format!(
//         "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}",
//         contents.len(),
//         contents
//     );

//     stream.write(response.as_bytes()).unwrap();
//     stream.flush().unwrap();
// }


