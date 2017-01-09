# Niconico Video Downloader
Niconico video downloader for Python(CLI)
Support Video ID(s) or MyList ID with range

# Preview
Add preview

# Prerequisite
virtualenv(Add link)

```
MacBook-Pro:nicodownloader User$ virtualenv venv
```

# Dependencies
See [requirements.txt](/requirements.txt)

# Usage
## Setup
source venv/bin/activate

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
