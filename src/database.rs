
use std::fs::{File, OpenOptions};
use serde_json::{Result, Value};
use std::io::BufReader;

use std::io::Write;
use std::io::BufRead;


pub struct DataBase {
    file_on_disk: File,
    data: Vec<Value>,
    lines_in_file: usize,
}


impl DataBase {
    pub fn open(filename: String) -> DataBase {
        // let file = File::open(filename.unwrap()?;

        let file = OpenOptions::new()
                    .read(true)
                    .write(true)
                    .append(true)
                    .create(false)
                    .open(filename).unwrap();

        let reader = BufReader::new(&file);
    
        let mut lines_in_file = 0;
        let mut vec = Vec::new();
        for line in reader.lines() {
            // println!("{}", line.unwrap());
            let v: Value = serde_json::from_str(&line.unwrap()).unwrap();
            vec.push(v);
            lines_in_file += 1;
        }

        DataBase {
            file_on_disk: file,
            data: vec,
            lines_in_file,
        }
    }

    pub fn new(filename: String) -> DataBase {
        let file = OpenOptions::new()
                    .read(true)
                    .write(true)
                    .append(true)
                    .create_new(true)
                    .open(filename).unwrap();

        DataBase {
            file_on_disk: file,
            data: Vec::new(),
            lines_in_file: 0,
        }
    }

    pub fn sync(&mut self) {
        let target = self.data.len();
        while self.lines_in_file < target{
            self.file_on_disk.write_all( self.data[self.lines_in_file].to_string().as_bytes() );
            self.file_on_disk.write_all(b"\n");
            self.lines_in_file += 1;
        }
        self.file_on_disk.sync_all();
    }

    pub fn add(&mut self, to_add: Value) {
        self.data.push(to_add);
    }

    pub fn query(&mut self, index: usize) -> &Value {
        &self.data[index]
    }

}

