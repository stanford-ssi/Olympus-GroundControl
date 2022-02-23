

use std::fs::File;

pub trait DataStream {
    fn next_data_point(&self) -> String;
    fn alive(&self) -> Bool;
}




// struct FileDataStream {
// }


impl DataStream for File {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}



pub fn pull_data(item: &impl DataStream) {

}
