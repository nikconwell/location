# location
Little experiment plotting things on a map.

Takes things from the Natick, MA police logs https://www.natickma.gov/1600/Daily-Log, downloads PDFS, processes (using Census Geolocation data) to a CSV, then uses libraries from https://plotly.com/ and javascript to display an interactive map of interesting activity in the town. 


# Install notes

## Create venv
```bash
python3 -m venv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
```

# How to run

## Download

Run download.py, potentially adjusting the baseURL for the current year.

```bash
./download.py --help
./download.py
```

This will create a bunch of ```Daily-Log-[MONTH]-[DD]-[YYYY[-to-[MONTH]-[DD]-[YYYY].pdf``` files.

## Process and normalize the data

Run parselog.py to take the log entries, normalize some of the text (this is a free form log so there is a fair amount of variation), do some geolocation lookup, and produce a CSV of the data suitable for the plotly libraries to create nice maps.

```
./parselog.py --help
./parselog.py --input Daily-Log-*.pdf > activity.csv
```

This will take a while and likely you will see warnings like:

```
>>>>>> WARNING, NO GEO information for 261 WORCESTER ST, natick, ma, 01760 (parsed from >>SHAANXI GOURMET - 261 WORCESTER ST<<)
```

This is largely because ```parselog.py``` uses the freely accessible Census Geolocation data at https://geocoding.geo.census.gov/geocoder/ which is fast and has no limits on usage (at the scale we are using it I guess), but since it is based on Census responses it does not have the best accuracy, and if there is no census for the address (like commercial properties), then likely no address info. Originally I had used some of the more available APIs at https://openstreetmap.org but they are all tightly rate limited (or cost actual $$$) and so I stopped using them.

But then I discovered...

## (Optional) Tune the Geo Location

https://openstreetmap.org actually has freely available data that you can download and serve yourself without rate limits. The rate limit is just on their public API in the cloud, which is fair enough. So, we have a process for fixing up the geolocation data, which is to run ```refine-geodata.py```.

When you run ```parselog.py``` it generates two files, ```geodata.json``` and ```geofail.json```. This cache of address to map coordinates makes it easer to rerun ```parselog.py```, but having the cache files available separately also allows us to refine these addresses useing better GeoLocation data.


### Start a docker service for serving OpenStreetMap GeoLocation data

```
docker run -it -e PBF_URL=https://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf -e REPLICATION_URL=https://download.geofabrik.de/north-america/us/massachusetts-updates/ -p 0.0.0.0:80:8080 --name nominatim mediagis/nominatim:4.5
```

Basically we download all of Massachusetts data and start up a service listening on port 80. This start takes a long time (20 minutes?) on my ancient system, so be patient before the API is running. Evidently the download takes a while, but once it's downloaded there is a lot of DB building and index building that takes forever and uses 100% of my CPU. You can tell things are ready if you go to http://your.local.system.address/search.php?q=1%20main%20street%20natick,ma and you get JSON output indicating map data.

Refine the geodata:
```
./refine-geodata.py --help
./refine-geodata.py
```

This will run for a while and update the ```geodata.json``` and ```geodata.fail``` files. Then rerun parselog.py to use the new geodata to produce more accurate coordinates for the mapping.

```
./parselog.py --input Daily-Log-*.pdf > activity.csv
```

At this point you have a large CSV, one line per activity throughout the year.

## Display the data

I upload the data to github and I have a github page https://nikconwell.github.io/location/ to display it. During development, I used VSCode to run the javascript locally and serve from the local system. To display the data, you can use something like:

```html
<!DOCTYPE html>
<html lang="en">
<head>
        <!-- Load plotly.js into the DOM -->
        <script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js'></script>
        <link rel="stylesheet" href="styles.css">
</head>

<body>
  <div id='myDiv'><!-- Plotly chart will be drawn inside this DIV --></div>
  <script src='https://nikconwell.github.io/location/try-plotly3.js'> </script>
   <!-- <script src="try-plotly3.js"> </script> -->
</body>
</html>
```

and either source the try-plotly3.js locally or from a web service. The try-plotly3.js itself has code:

```js
d3.csv(
  "https://raw.githubusercontent.com/nikconwell/location/main/activity.csv",
  handleCsvData
);
```

which tells it where to get the CSV. If you source it locally, like running from VSCode, you can replace this with a local file.

# Creation notes

This was an interesting project, taking me most of a year in my spare time. I'm relatively new to Python, JavaScript, HTML, etc. and totally unaware of GeoLocation stuff so I stumbled on a bunch of things as I did this.

## Download (```download.py```)

There is probably an easier way to download (curl?) the logs from https://www.natickma.gov/1600/Daily-Log but initially I had a single script to download/parse/GeoLocate, thinking it would be quick / straightforward. So, I have a downloader. There is a little HTML parsing to find URLs there so it was an interesting exercise in screen scraping.

The downloader could be made a bit more efficient by figuring out if it has already downloaded the data, that way you can run this download on a schedule and it will only download new data.

## Parsing (```parselog.py```)

Python has some nice libraries for PDF parsing which made it very easy to access the data. The data unfortunately is mostly free text following some very loose conventions, so there is a fair amount of code in ```extract_reason( )``` to normalize the text. This will likely need tuning over time. Normlizing the reasons makes the charting be more manageable as you can click on various large categories and then hover over the point to see the actual text that was in the log. If the values were not normalized you would not be able to select various categories since many things that are largely the same sort of activity (Motor Vehicle Stop, Suspicious Activity) are often written in slightly different ways and so would show up multiple times in the key.

The GeoLocation lookup was interesting. Initially I had thought my usage would be small enough for fair use on OpenStreetMap's public API, but it turns out it is way more. So I settled for using the freely available Census information at https://geocoding.geo.census.gov/geocoder/. This is a really good API, excellent documentation, and it's always good to see our government/tax money being used for cool and useful high tech things. Ultimately though this data is a little limited compared to OpenStreetMap.

## Refining GeoLocation(```refine-geodata.py```)

Plotly (https://plotly.com) and the GeoLocation stuff of OpenStreetMap (https://openstreetmap.org) has a TON of excellent documentation, however there is so much information that I did not initially see that I could download the data and serve it up myself. Once I started googling ```docker serve openstreetmap data``` then I stumbled on https://github.com/mediagis/nominatim-docker/tree/master/4.5 to be able to run a container to serve up the data locally. Intitially I was thinking I would speed things up by downloading USA data instead of the world map, but due to the MASSIVE size of all this data I just downloaded Massachusetts which still took a long time. We are truly living in a wonderful modern age when we have this sort of quality data freely available for download, and we can easily run things in a docker container to serve out.

## Charting

HTML and JavaScript are still a bit of a mystery to me, so it took a while to throw together something which could be hosted on github.io under my name. Plotly (https://plotly.com) has some amazing free libraries which produce really nice maps and interactive keys where you can search for data easily enough. The Plotly documentation is extremely detailed, although at times can be confusing due to a lack of examples, and having some parts looking very similar to other parts, but are not the same usage.

There was a fair amount of messing around with ChatGPT to produce the JavaScript map displayer even though all the hard work is actually being done in the library. All the details of the parameters, how to get it from the CSV, how to get things to display are all handled in the library, but you need to tell it what you want, and at times this was confusing as you need to refer to things in slightly different ways but the documentation has multiple ways of doing it all using the same or similar parameters. It did not help as my timing was slightly off so I intitially started using one library call which was actually deprecated, then needed to swap to a different / more modern library call which is the standard now. I am also a bit challenged by the common(?) JavaScript convention of just coding an entire function in a parameter to library call. This all works but to a new JavaScript person this is a bit confusing, why not just make it more apparent and make it a function and reference the function as a parameter to the library call? I can see frequent use of very small functions making different functions not tenable, but we are talking about a fairly large and complex function in this case so why not make that separate? IDK.
