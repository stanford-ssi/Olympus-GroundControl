

#[warn(unused_imports)]
#[warn(dead_code)]

mod database;
// use database::DataBase;

// use serde_json::{Result, Value};
// use serde_json::json;
// use handlebars::Handlebars;

use warp::Filter;

mod routing;
// use routing::get_routes;

#[tokio::main]
async fn main() {

    let routes = routing::get_routes();

    warp::serve(routes)
        .run(([127, 0, 0, 1], 7878))
        .await;

    // let mut magic = DataBase::new("testing.json".to_string());
    // let john = json!({
    //     "name": "John Doe",
    //     "age": 43,
    //     "phones": [
    //         "+44 1234567",
    //         "+44 2345678"
    //     ]
    // });

    // magic.add( john.clone() );

    // magic.add( john );

    // magic.sync();


    // let mut read = DataBase::open("testing.json".to_string());
    // println!("{}", read.query(0) );

    // let mut handlebars = Handlebars::new();
    // handlebars.register_template_file("skeleton", "./static/main.hbs").unwrap();
    // handlebars.register_template_file("skeleton", "./static/main.hbs").unwrap();


}