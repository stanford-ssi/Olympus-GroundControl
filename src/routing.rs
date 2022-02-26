

use warp::Filter;

// use serde_json::{Result, Value};
// use serde_json::json;

use std::collections::HashMap;

use handlebars::Handlebars;

// async fn filter_page(name: String) 
//     -> impl Filter<Extract = impl warp::Reply, Error = warp::Rejection> + Clone {

//     if name == "" || name == "dashboard" {
//         return warp::fs::file("./static/main.html");
//     }

//     if name == "messages"{
//         return warp::fs::file("./static/messages.html");
//     }

//     return warp::reject();

//     // if !hb.has_template(name){
//     //     return Err(warp::reject())
//     // }

//     // let page = hb.render_template( json!( {"indentifier".to_string() : "test".to_string(),
//     //                                         "id".to_string() : 2}   ));

//     // return hb.render_template("skeleton".to_string(),
//     // json!( {page} ) );
// }

fn get_dashboard_page(hb: &Handlebars) -> String {

    let mut data = HashMap::new();
    data.insert("page", "testing");

    return hb.render_template("skeleton", &data).unwrap();

}

pub fn get_routes()
    -> impl Filter<Extract = impl warp::Reply, Error = warp::Rejection> + Clone {

    let mut hb = Handlebars::new();
    hb.register_template_file("skeleton", "./static/skeleton.hbs").unwrap();

    // handlebars.register_template_file("dashboard", "./static/dashboard.hbs").unwrap();

    // let main = warp::get()//.and(warp::path::end())
    //     .and(warp::path::param())
    //     .and_then(move |name: String| filter_page(name));


    // let main = warp::get().and(warp::path::end())
    //     .and(warp::fs::file("./static/main.html"));

    // GET /hello/warp => 200 OK with body "Hello, warp!"
    // let hello = warp::path!( String )
    //     .map(|name| format!("Hello, {}!", name));

    let css = warp::path("style.css")
        .and(warp::fs::file("./static/style.css"));

    let normalize = warp::path("normalize.min.css")
        .and(warp::fs::file("./static/normalize.min.css"));

    let dashboard = warp::path("messages")
        .map( move || get_dashboard_page(&hb) );


    let routes = dashboard.or(css).or(normalize);

    return routes;

}
