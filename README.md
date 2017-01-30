# Niconico Video Downloader
Niconico video downloader for Python(CLI)

- Download by Video ID(s)/MyList ID (with range)
- Supports "Resume Download"

For those who uses Mac, see [NicoDownloader for MacOS](https://github.com/crowjdh/Nico-Downloader-for-MacOS)
# Preview
![preview](/images/preview_01.png)

# Prerequisite
- [Virtualenv](https://virtualenv.pypa.io/en/stable/)

```
MacBook-Pro:nicodownloader User$ [sudo] pip install virtualenv
MacBook-Pro:nicodownloader User$ virtualenv venv
MacBook-Pro:nicodownloader User$ source venv/bin/activate
MacBook-Pro:nicodownloader User$ pip install -r requirements.txt
```

# Dependencies
See [requirements.txt](/requirements.txt)

# Usage
## Setup
```
MacBook-Pro:nicodownloader User$ source venv/bin/activate
```

### Using Video ID(s)
```
MacBook-Pro:nicodownloader User$ python nicodownloader.py -o outputPath -p download_thread_count email@host.com your_password v video_id_first video_id_second
```

### Using MyList ID
```
MacBook-Pro:nicodownloader User$ python nicodownloader.py -o outputPath -p download_thread_count email@host.com your_password m -r 0:30 mylist_id
```

Try below for more information
```
MacBook-Pro:nicodownloader User$ python nicodownloader.py -h
MacBook-Pro:nicodownloader User$ python nicodownloader.py id pw m -h
MacBook-Pro:nicodownloader User$ python nicodownloader.py id pw v -h
```
