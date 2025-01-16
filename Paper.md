---
title: "Key Drivers of Attractiveness of Regional Rail for Commuters: Case Study of Vienna and Lower Austria"
author: [Maciej Kilijański]
date: "11.11.2024"
csl: Bibliography/harvard-cite-them-right.csl
bibliography: [Bibliography/ref.bib]
citeproc: true
toc: true
toc-depth: 2
lof: true
lot: true
output: pdf_document
header-includes:
  - \usepackage{setspace}
  - \linespread{1.5}
...

<div style="page-break-after: always;"></div>

# Introduction

With local governments of regions all around Europe striving to reduce emissions and congestion caused by citizens' daily commutes, regional rail emerges as a potential solution to this problem. This paper provides a step-by-step guide to building a framework to analyze factors driving popularity of regional rail as a mode of transport people will choose for their daily commute.

The topic is extremely relevant, as according to @eurostatPersonsEmploymentCommuting an average European spends 25 minutes commuting to work every workday. Spending almost an hour commuting everyday significantly influences quality of life of commuters [@hanEffectCommutingTime2022a]. Increasing popularity of railway, as a sustainable mode of transport, can bring our society closer to achieving climate neutrality in passenger transport. Rail transport also reduces traffic externalities, therefore improving citizens' life quality [@fagedaLightRailSystems2021a]. This relevance has brought many scientific writers to do research on the topic. Because of significant interest we now understand a lot of ways public transport planners can influence ridership via timetable changes [@asensioTransportModeChoice2002a; @heuermannEffectInfrastructureWorker2019a; @weliwitiyaBicycleTrainIntermodality2019a]. The effects of timetables are clearly visible in one of the regions of Poland, the Dolnośląskie voivodeship. The region has experienced the strongest growth of regional rail's passenger numbers in the country, despite having similar rolling stock to other regions in the country. It has been achieved largely with a sharp increase of the number of connections per day and establishing a minimum standard of 8 pairs of trains operated on each route. This has lead to 22.6% year-to-year increase in passengers transported between 2023 and 2024 [@kolejedolnoslaskieRekordowyStyczenKoleje2024].

However, little to no research has been done regarding the influence of amenities present during such commute on percent of potential commuter demand utilized by railways. This is largely due to lack of official data on rolling stock used on railway connections. Such data is not provided by most of big European railway operators, including České Dráhy, Deutsche Bahn, PKP Intercity and Österreichische Bundesbahnen. This paper aims at establishing a framework for retrieving of such data from a community-based website Vagonweb.cz, and transformation of this data and connecting it to official data for timetable information (GTFS) and official data about railway infrastructure (NetEx).  
A retrieval and transformation process is then conducted for Vienna and Lower Austria region in Austria. Similar process can be repeated for most regions in Central Europe thanks to availability of necessary data on Vagonweb.cz and usage of industry data exchange standards: GTFS and NetEx.  
The region was a convenient point for developing such framework thanks to an excelent work conducted by @brezinaPendelnOstregionPotenziale2015. Its authors conducted an analysis of commuter potential in the region using similar geospatial methods but focused heavily on development of passenger potential of railway axis leading into the city of Vienna. Despite that, methods and techniques employed by @brezinaPendelnOstregionPotenziale2015 proved helpful in developing the framework and are heavily utilized in this paper.

The paper uses three computation tools: ArcGIS Pro for simple geospatial calcualtions, Python programming language for complex processing and Tableau Prep ETL tool for resource intensive dataset filtering and manipulation.

# Data gathering

The framework heavily relies on accessibility of geospatial data from official sources, as well as third-party data from community-based websites run by railway geeks around the world on providing data on rolling stock attributed to connections. In case of Vienna region and the entire Central Europe, the Vagonweb.cz provides one of the most comprehensive databases.

## NetEx

The Network and Timetable Exchange (NetEx) is a standardized data format, sanctioned by European Union's standard EN 12896 as part of a so-called Transmodel. The Transmodel contains various data exchange formats like NetEx, Siri or OJP and aims at delivering seamless experience for intra and international public transport travel within Europe [@transmodelEN12896].

The NetEx acts as part of the Transmodel and aims at sharing the topology, amenities and infrastructure features along the network. It is favorable to use due to its wide availability across countries. A map of all countries using NetEx as of 2024 can be seen in Figure 1 [@transmodelMap].

![Countries involved in Transmodel Development and implementation. Source: Transmodel (2024)](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/NetEx Usage.png)

Moreover, European Union's member countries are obligated to implement National Access Points to data for all formats present in the Transmodel, including NetEx, under European Delegated Regulation (EU) 2024/490 (MMTIS) [@europeanparliamentCommissionDelegatedRegulation2024]. This obligation makes it relevant for use in this paper as a base of a framework to use across countries.

### History

The Transmodel as a whole can be traced back its origins to European Economic Community's DRIVE programme [@wrro2200]. The program aimed at aiding transport scheduling and operation with use of computers. Further generations of the data model have been developed over the years, fostered by European institutions, with NetEx emerging in the lates version of the data model - Transmodel 6.0 [@wiki:netex].

As of 15^th^ of January 2025 following @wiki:netex2 NetEx has been already implemented by 17 countries. 16 of them in Europe, one foreign being Australia.

### Description of data model

NetEx's data is provided to users in `xml` format. Depending on so-called NetEx flavor a country implementation uses, different categories of data can be accessed in the data model. A common core is however accessible in all current implementations. An overview based on @wiki:netex2 and @europeanparliamentCommissionDelegatedRegulation2024 can be seen in Table 1.

| Level of service (LOS) | Static data                                  |
| ---------------------- | -------------------------------------------- |
| LOS 1-9                | Network topology and routes/lines (topology) |
| LOS 1-10               | Transport operators                          |
| LOS 1-11               | Timetables                                   |

Table: Levels of service (LOS) accessible in all current implementations of NetEx.

As this paper's primary concern are amenities accessible on railway network and in connections, the only LOS necessary to use is the LOS 1-9. It provides detailed shapes of the rail network, one can measure distances on, station and network junctions locations as well as availability of station amenities like platform clocks, bicycle parkings, WiFi, Park&Ride parkings.

The 2024 NetEx provided by @oebbNetex contains this information in two files - one containing infrastructure information, the other information about stations specifically. A sample of such files can be seen in Appendix 1.

Thanks to the data model being structured in `xml` it allows for creation of flavors in implementation by adding attributes to the data structure with ease. A feature not available so easily using another popular format - `json`.

### Model transformation

Further processing of NetEx data in ArcGIS and Python for geospatial use requires transforming its `xml` format to one readeable by geospatial software. A format of choice in this paper was `geojson`, allowing for easy import and further manipulation. Transformation was conducted in Python using `xml.etree.ElementTree`, `geojson` and `json` packages available via the `pip install` command.

Both files were first imported and parsed using `ET.fromstring()` command, then the procedure exported each of the nodes necessary for further analysis and parsed its features into a `geojson` feature structure, a comparison of which can be seen below, on example of a station Kapellerfeld.

```xml
<StopPlace version="any" created="2023-12-11T09:46:17.2376314+01:00" id="at-43-3852">
    <ValidBetween>
        <FromDate>2023-12-10T00:00:00</FromDate>
        <ToDate>2024-12-07T00:00:00</ToDate>
    </ValidBetween>
    <keyList>
        <KeyValue>
            <Key>NETEX-ID</Key>
            <Value>at-43-3852</Value>
        </KeyValue>
    </keyList>
    <Name lang="de">Kapellerfeld</Name>
    <ShortName>Gef H1</ShortName>
    <Description/>
    <PrivateCode>571</PrivateCode>
    <Centroid>
        <Location>
            <Longitude>16.495168</Longitude>
            <Latitude>48.31701</Latitude>
        </Location>
    </Centroid>
    <TransportMode>rail</TransportMode>
    <StopPlaceType>railStation</StopPlaceType>
    </quays>
</StopPlace>
```

Snippet 1: NetEx information in `xml` format

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [16.495168, 48.31701]
  },
  "properties": {
    "name": "Kapellerfeld",
    "description": null,
    "key_values": {
      "NETEX-ID": "at-43-3852"
    }
  }
}
```

Snippet 2: NetEx information in `geojson` format

Transforming this information not only made it more concise and readable, it also reduced its size for junction and station files. After importing the transformed data into ArcGIS Pro, a map of the whole railway network in Austria could be constructed (Figure 2).

![Map of Austrian rail network created in ArcGIS Pro using NetEx data. Source: Own work](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/NetEx Map.png)

Full code snippet used for `xml` to `geojson` transformation is available in Appendix 2.

## GTFS

TODO: Until 30.11

### History

### Description of data model

### Model transformation

## Vagonweb

Collecting data about rolling stock assigned to certain connections is a notoriously hard task for public railway operators in Europe. There is no open data policy forced by any of the European regulators to publish such data, leaving it optional for railway operators to publish any of such data. Most operators provide little to no information. The Austrian ÖBB allows for retrieval of limited data on rolling stock, such as possible classes of carriages or a restaurant on board, but without specific information like the age of rolling stock used. Such data can be retrieved using a specific website: live.oebb.at, but has limited capabilities for mass retrieval of data or webscraping due to use of a sophisticated user interface. For the purpose of this study, this publically available information on each connection was therefore not sufficient.

ÖBB's official timetables only provides information on accessibility for disabled people, WiFi, availability of the 1^st^ class, possibility to take bicycles onboard and low-floor carriages. No data on availaility of air conditioning onboard and the age of rolling stock is provided. These data in timetables were not accessible neither in any of the available NetEx files, nor in GTFS files available. These were however included in the scope of this study creating a need for alternative sourcing of data.

With no official sources availabe this paper resorted to webscraping of the community-based online forum created by railway enthusiasts - [vagonweb.cz](https://www.vagonweb.cz/). The website is constructed by Pavel Dvořák and maintained by a range of contributors, providing compositions of most (and in some cases all) trains running in Austria, Switzerland, Germany, Czechia, Slovakia, Poland, Hungary, Slovenia, Croatia, Servia, Bosnia and Hercegovina, North Macedonia, Bulgaria, Romania, Ukraine, Italu, France, Luxembourg, Belgium, Netherlands, Norway, Sweden, Finland, Greece, Albania and Turkey [@vagonweb]. The interface of the website was simple enough to employ classical webscraping techniques in order to retrieve train compositions of all trains operated in Vienna and Lower Austria. Train numbers were retrieved from GTFS data and filtered to include local trains operated in Vienna and Lower Austria only.

### Webscraping - methodology

With lack of an official API supported by the website for downloading the data on rolling stock compositions this paper resorted to webscraping the data. The process was conducted in Python using packages described in Table 2.

| Library          | Description                                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `urllib.request` | Used for executing callouts to the website itself and receiving the data.                                                      |
| `urllib.parse`   | Used for URL parsing for the calluts to be made.                                                                               |
| `BeautifulSoup`  | Used for parsing the data retrieved and retrieving the actual part of data necessary for the analysis from the html structure. |
| `ssl`            | Used for ssl authentication to allow retrieving data using the https protocol.                                                 |

Table: Python libraries used for webscraping Vagonweb.cz

Due to concerns about complexity and code readablility, the Python code is divided into two files, each containing several functions, each responsible for a part of work. The controler file employs its main function `scrape_and_update()`, that orchestrates the whole process, importing the list of all connections needing retrieval first, controlling the pace of data querying and writing the data back locally. The performer functions consisted of methods interacting with local data, the website, processing the html content retrieved and ultimately saving the data retrieved. All webscraping is executed by functions present in the webscraper file. The train numbers are loaded from `trips.txt` file, a part of GTFS data provided by a railway operator. Such setup made code debugging easier and followed code readablility best practices [@parlantePythonReadablility].

Precise steps to follow for data retrieval are described in following subchapters. Full Python code for retrieval is available in Appendix 3.

### Standardizing train categories

As train compositions stored in Vagonweb.cz are categorized by operational categories of trains operated, the first step conducted by the orchestration function after loading all train numbers from GTFS standarization of categories is necessary. As the website does not provide differentiation between S-Bahn and Regional trains in Vienna and Lower Austria region.

```python
def standardize_category(category: str) -> str:
        if category == "S":
            return "R"
        else:
            return category
```

That standarization is achieved using the `standardize_category()` category function, which replaces all S-Bahn train numbers to their Regional train numbers. Then it is time to scrape the data from the website.

### Creating request URL

A first step of which is creating a request URL, specific for the train considered.

The `create_request` function creates a unique request URL for each of the train connections needing retrieval. It takes website's base URL of `https://www.vagonweb.cz/razeni/vlak.php?` and appends necessary information to it. Then a parsed string is returned. The information allowing to retrieve each train were:

- Operator - ÖBB for the case of Lower Austria and Vienna (according to GTFS data)
- Category - S for S-Bahn, R for Regio and REX for Regional Expressess. Other categories like CAT (City Airport Train) or long distance D-Zuge, Euro/Inter-City and RailJets are not considered as the scope of this study only includes regional, commuter trains.
- Number - train number
- Year - year of the timetable (2024 for this paper)

```python
def create_request(operator: str, category: str, number: str, year=2024) -> str:
    url = baseurl
    if operator:
        url = url + "&zeme=" + parse_url.quote(operator)
    if category:
        url = url + "&kategorie=" + category
    if number:
        url = url + "&cislo=" + number
    if year:
        url = url + "&rok=" + str(year)
    return url
```

### Sending a request

Having successfully created a request URL, it is now time to send it to the website. Use of the `SSL` package is necessary to create a safe connection between Python and the website. The package signs the request using a so-called Secure Sockets Layer protocol, allowing the code to make a secure https connection [@ssl]. Headers are then added to enact a request made by a normal browser and prohibit the website to block the request.

```python
def __request_vagonweb__(
    operator: str, category: str, number: str, year=2024
) -> BeautifulSoup:
    url = create_request(operator=operator, category=category, number=number, year=year)
    context = ssl._create_unverified_context()
    req = Request(url)
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    )
    req.add_header("Connection", "keep-alive")

    try:
        response = urlopen(req, context=context)
        html_bytes = response.read()
        html_content = html_bytes.decode("utf-8")  # Decode bytes to string
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()
    return BeautifulSoup(html_content, "html.parser")
```

A try/except block allows to catch possible errors and inform a user excecuting the request what went wrong. Finally the received website body is decoded and returned for further processing as a `BeautifulSoup`.

### Retrieving meaningful data

Having retrieved the rendered website, Python code further employs the `BeautifulSoup` package to find an html element `table` within the retrieved website. The table containing information on train composition is marked with a class `vlacek` for the website.

```python
def __extract_train_class__(soup: BeautifulSoup) -> list:
    result = []
    vlacek_table = soup.find("table", class_="vlacek")

    if vlacek_table:
        # Use CSS selector to find the desired span element
        selector_carriages = "tr > td.bunka_vozu"
        carriages = vlacek_table.select(selector_carriages)
        for carriage in carriages:
            selector_class = "div > div > span.tab-radam"
            className = carriage.select_one(selector_class)
            if className:
                result.append(className.get_text(strip=True))
    return result
```

The table rows (carriages) are then extracted. If a train composes of multiple carriages, the results are stored as a Python list. The final format of retrieved data for a single train can be seen below. A dictionary with train number as key and a list of rolling stock a train is composed of is formatted by the Python script.

```json
{
  "3633": ["1144", "Bmpz-l", "Bmpz-l", "Bmpz-l", "Bmpz-s"]
}
```

Such structure ensures uniqueness of each composition and ensures easy filtering of the dataset later on.

### Performance

Webscraper's performance was limited with threshholds of the website. Randomly distributed breaks between 0 and 360 milliseconds are done using Python's `time` package to protect against getting marked as a distributed denial-of-service (DDoS) attack [@ddos]. Figure 3 displays time of retrieval for each request made by the code.

![Retrieval time of train compositions](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/Vw Retrieval time.png)

Despite an initial spike almost reaching 90 seconds per request, an overall retrieval time for all 3748 trains was just under 130 minutes, making an average of around 2 seconds per request - a performance comparable to loading a website directly in a browser. Such timing outpaces manual collection of necessary data from the website to desired data structure, proving value of the code provided.

## Pendler Dataset

The pendler dataset was joined to Raster `shp` file and mapped.

TODO: Until 06.12

## Road network

https://www.data.gv.at/katalog/dataset/no-strassen-b-und-l-strassengraph-level-1#resources
https://www.data.gv.at/katalog/dataset/stadt-wien_straengraphwien#resources
TODO: Until 11.12

The road networks of Vienna and Lower Austria were retrieved in `shp` format and transformed into a routable network using ArcGIS Pro's Network Analyst tool.

The road network was constructed without use of elevation. Three modes of transport were added:

- Driving
- Cycling
- Walking

# Model description

The model considered in this paper is calculated as following. In order to measure attractiveness of commutes
for each of the 250m rasters, each raster is first assigned the nearest station based on proximity to their centroid.
Then the bi-directional passenger potentials are calculated for each combination of stations based on the assignment made. Thanks to the availability of GTFS transit data, these potentials were attributed to sets of morning commute connections using a bi-directional network and a modified Djkstra algorithm.

Each potential commute is then assigned the amenities offered by rolling stock used. Data about necessary train changes and additional time necessary for it is also attributed along with average speed and duration of each potential commute. The last factor noted for is the time of arrival at the destination station. Following paragraphs provide a detailed description of the calculations.

## Distance raster to station

In order to assign stations to rasters, each raster has a centroid calculated, from which distance is measured to all stations in the dataset. The centroid calculation is conducted using the Point tool, according to ESRI's documentation for ArcGIS Pro [@centroidEsri]. In case of this paper the rasters dataset is retrieved from Austrian Statistical Office (Statistik Austria) and filtered by location to only include rasters that intersect communities within Lower Austria and Vienna [@statistikRasters]. Filtering is conducted using a spacial join. ArcGIS Pro allows to select based on location, therefore each raster touching any within the region. The filtering allowes the number of mobility rasters in dataset to shrink, in case of this paper from over a million rows to 316317.

Originally the assignment of each raster centroid to the nearest station was supposed to be conducted using the road network for Vienna and Lower Austria and the Network Analyst tool available in ArcGIS Pro. The size of the dataset however posed a problem:

- 381 stations (_Facilities_)
- 316.317 rasters (_Incidents_)

Giving $381\cdot316.317=120.516.777$ possible combinations.  
Such number of calculations turned out to be infeasible for ArcGIS Pro as the problem would not construct, let alone execute. Therefore, heuristics became a necessity. Following the example of @brezinaPendelnOstregionPotenziale2015, each station within Vienna city limits is assigned a distance band along the road network. Stations outside of Vienna city limits are assigned distance bands based on a circle being drawn around them, radius of which demarked a distance band. Following the reasoning of @brezinaPendelnOstregionPotenziale2015 further, the distance bands calculated for each station are:

- 500 meters
- 1000 meters
- 1500 meters
- 2000 meters
- 4000 meters
- 6000 meters
- 8000 meters

![Distance bands around stations](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/DistanceBands.png)

Final outcome of the distance band calculation can be seen in Figure 4. Distance bands are there exported from ArcGIS Pro as `shp` files and are further processed in Python using the `geopandas` package.

### Raster to station attribution process in Python

To ensure correct processing all geometries must be transformed to the same coordinate reference system (crs). A dominant `shp` file is chosen and all other geometries are converted to its crs.

```python
distance_bands_Wien = distance_bands_Wien.to_crs(raster_points_Wien.crs)
raster_points_NO = raster_points_NO.to_crs(raster_points_Wien.crs)
distance_bands_NO = distance_bands_NO.to_crs(raster_points_Wien.crs)
```

All rasters are then spatially joined to the distance bands around the stations, allowing for subsequent calculation of a distance matrix.

```python
raster_join_wien = raster_points_Wien.sjoin(distance_bands_Wien, how="left")
raster_join_no = raster_points_NO.sjoin(distance_bands_NO, how="left")
```

With spatial joins performed a distance matrix can be calculated. In case of this paper the distance matrix for Vienna was calculated separately and later merged with distance matrix for Lower Austria due to different geometries of the distance bands around stations. This does not have to be the case when analyzing other regions. The code extracts station code and range of the distance band for each band. Naming structure of the distance bands is determined by ArcGIS Pro as a tool used for distance band calculation. Further, a matrix is calculated as a list of Python dictionaries containing all distance bands a raster centroid is located within.

```python
def DistanceMatrixVienna(
    rasters=raster_join_wien, pattern=r"(at:\d+:\d+).*?(\d+ - \d+)"
) -> list:
    # Extract "station_code" and "range" from the "Name" column
    extracted = rasters["Name"].str.extract(pattern)
    rasters["station_code"] = extracted[0]  # Matches the first group (e.g., at:49:94)
    rasters["range"] = extracted[1]  # Matches the second group (e.g., 6000 - 8000)

    # Filter out rows where 'FromBreak' is NaN
    rasters = rasters.dropna(subset=["FromBreak"])

    # Group by 'gid' and construct dictionaries
    matrix = [
        {"gid": gid, **dict(zip(group["station_code"], group["FromBreak"]))}
        for gid, group in rasters.groupby("gid")
    ]

    return matrix
```

![Final Raster Selection](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/Selected Rasters.png)

In case of this paper, the lists for Lower Austria and for Vienna had to be merged together as a `pandas` data frame. The results (Figure 5) are then saved as a conventional distance matrix in a `csv` file.

```python
def MergeLists(base=dist_lower_austria, to_merge=dist_vienna, key="gid"):
    # Create a dictionary to hold the merged results
    # Convert lists of dictionaries into DataFrames
    df1 = pd.DataFrame(base).set_index(key)
    df2 = pd.DataFrame(to_merge).set_index(key)

    # Merge the two DataFrames on the key, preserving all data
    merged_df = df1.combine_first(df2).reset_index()

    # Convert the merged DataFrame back to a list of dictionaries
    merged_list = merged_df.to_dict(orient="records")
    return merged_list


OD_All = pd.DataFrame(MergeLists())
OD_All.to_csv("Straßennetz/GrossraumWienMatrix.csv")
```

Full Python code for distance matrix calculation is available in Appendix 4.

The station assignment was then conducted using code available in Appendix 5. The code analyzed the distance matrix and selected the closest station to each of the rasters. If several stations were within the same distance band, the one with a lower Id derived from NetEx was chosen. A large scale of the distance matrix (120516777 possible combinations) demanded the use of multicore processing using the `multiprocessing` package in Python.

Thanks to no use of loops and multicore processing the whole calculation executed in 12.4 seconds for all 197.820 rows. The assigned station assignment was then used to aggregate station-to-station passenger flows.

## Station to station passenger potential based on Pendler dataset

Each station had a sum departing and arriving passengers calculated. These sums were calculated in the same form as in the Pendler dataset from Statistik Austria, keeping the division into total number of commuters, work commuters and school commuters. The formula for calculation of commuter potential of between each set of stations can be summarized as:
$$\sum_{r\in R} passengers_{r}, \forall o \in O, \forall d \in D$$
$$\text{Where } r\text{ represents a raster in Rasters } R$$
$$\text{Where } o\text{ represents an origin station in } O$$
$$\text{Where } d\text{ represents a destination station in } D$$

The aggregation was conducted in Tableau Prep, due to large scale of calculations needed. The ETL tool handled necessary work in very low time, while testing in Python proved to be challenging for the programming language. At this point a graphical representation of results was possible to present. The visuals were generated using Tableau Desktop business inteligent software.

### Commuter balance - initial findings from station to station passenger potential

![Commuter Balance Map](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Commuter Balance Map.png)

Figure 6 displays a map of commuter balances for stations in Vienna and Lower Austria. This paper calls commuter balance a difference between number of commuters leaving for work and arriving to work at the station. A negative balance implicates more commuter potential in people departing from the station for their morning commute. Three categories of commuter balance were selected: red denotes negative commuter balance (more people leaving than arriving), yellow denotes close to equal yet positive commuter balance and green a strongly positive commuter balance. Size of each point demarks total number of commuters that could potentially utilize the station, both leaving from it (from their place of residence) and arriving at it (to their place of work/study).

What turns attention quickly is the concentration of strongly positive stations in Vienna city center (with the exception of Wien Hauptbahnhof). Outside of Vienna only 14 stations had a strong positive balance: St. Pölten Hauptbahhof, Krems, Tulln, Katzelsdorf, St. Pölten Bildungscampus, Hollabrunn, Amstetten, Brunn-Maria Enzendorf, Achau, Horn, Gunstramsdorf Thallern, Korneuburg, Wieselburg, Fischamend, as seen in Figure 7.

![Biggest potential stations excluding Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Busiest Stations without Vienna.png)

Including Vienna the station potential diagram becomes dominated by the metropoly. 6 biggest potential stations are in Vienna, followed by Brunn-Maria-Enzersdorf (close to Vienna), which is then followed by another 8 stations in Vienna. This is visible in Figure 8.

![Biggest potential stations including Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Busiest Stations.png)

Drawing on Figures 7 and 8, a fascinating statistic can be seen in Figure 9. 65% of all commuters in the region commute with a destination at a attributed to a station within Vienna's city limits. The disproportion towards the number of commuters who's target is elsewhere is significant. This proves the metropolitan position the city has within the neighbouring region and poses a set of potential challanges for infrastructure and railway operators with uneven demand in both directions.

![Commuters arriving in Vienna vs. outside of Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Arrivals Vienna vs. Rest.png)

## Commuter to connection assignment

In order to calculate amenities available for each commute to work, routings for commuters must be calculated. As rasters differ in proximity to stations, this paper once again takes inspiration from @brezinaPendelnOstregionPotenziale2015 and calculates necessary commutes for both two modes of transport.

@brezinaPendelnOstregionPotenziale2015 differentiate modes of transport into SLOW and MIV. For purpose of this paper, these modes are attributed to walking for SLOW and public transit for MIV. This makes logical sense as commuters arriving by public transport to their destinations do not have access to a motorized mode of transport other than public transport.

For walking, a time necessary to cover a distance is calculated with according to measurements conducted by @azmiComparingWalkingBehaviour2012. With the average walking pace equal 1.4 meters per second, which translates to 5 km/h.

With 65% of all commuters in Vienna and Lower Austria arriving daily in Vienna (Figure 9), the MIV average speed must consider the average speed of the local public transport. @steinwidderEvaluationMethodAnalysis2023 provides a recent measurement of such equal to 15.44 km/h. The time necessary to cover the distance in each distance band is then calculated for both modes of transport and rounded up to a full minutes (Table 3).

| Distance [meters] | Walking time | Public Transit Time |
| ----------------- | ------------ | ------------------- |
| 500               | 6            | 2                   |
| 1000              | 12           | 4                   |
| 1500              | 18           | 6                   |
| 2000              | 24           | 8                   |
| 4000              | 48           | 18                  |
| 6000              | 72           | 24                  |
| 8000              | 96           | 32                  |

Table: Distance vs. time needed to cover it using walking and public transport in Vienna

Four time slots of arrival are calculated: 10 minutes prior work start, 20 minutes prior work start, 30 minutes prior work start and 40 minutes prior work start. Values larger than these are removed due to unlikely nature of such commute.

From this table bins are calculated for time necessary to arrive before 8:00 AM - a popular work and school start hour in Europe. Each connection was analyzed for trains allowing to arrive at destination station at 7:50 AM, 7:40 AM, 7:30 AM and 7:20 AM.

Solving a shortest optimization problem on such scale of a dataset would not be feasible using an everyday computer. A Dijkstra algorithm [@dijkstra1959note] is therefore proposed to be calculated of each set of two stations. A method of conducting such algorithm for a GTFS dataset using Python was described and developed by @Github2018. The script available in Appendix 6 contains modifications necessary to accomodate restrictions regarding arrival times (bins) and execute pathfinding on a bulk scale.

In order to allow an arrival constrained route calculation, the connections are filtered for each time bin and route is calculated backwards, i.e. using the first connection arriving at destination comming from the direction of origin. The final result is then inverted again. This approach allows to prepare and save data for morning commute between each set of stations for each arrival time bin for during morning rush. Resulting routings are then saved as a `json` file structured in a following way:

```json
{
  "from-to-arrival": {
    "from": "str",
    "departure": "datetime",
    "to": "str",
    "arrival": "datetime",
    "trips": {
      "tripid": {
        "from": "str",
        "to": "str",
        "duration": "int",
        "stop_count": "int",
        "average_speed": "float",
        "via": [
          {
            "from": "str",
            "departure": "datetime",
            "to": "str",
            "arrival": "datetime",
            "duration": "int",
            "distance": "int",
            "speed": "float"
          }
        ]
      }
    },
    "duration": "int",
    "changeCount": "int",
    "changesAt": [{ "station": "str", "duration": "int", "sequence": "int" }]
  }
}
```

The above structure provides a way of storing all data on a trip, that are necessary for further analysis. Information on origin and destination station is saved as well as times of departure/arrival for both of them. The total duration of a trip taken is also recorded, together with a count of all stops taken throught the journey and the average speed along it. Each train trip necessary to be taken along the journey is logged using its GTFS Id, along with all stations a train stops at during the trip, departure and arrival times, duration, distance and average speed for each segment of route is also recorded. The overall journey contains a summary of changes count as well as precise information on where necessary changes (if any) must occur, in which sequence and how long is the waiting time a passenger must consider.

## Route amenities calculation

Having retrieved data from Vagonweb.cz, it is now time to employ it for a good purpose. From 3748 trips operated by ÖBB in Vienna and Lower Austria, that are a part of the GTFS dataset, the enthustiast-run database contained data on 2092 of them (55.8%). Route amenities were awarded based on publically available characteristics of the rolling stock provided by

Data was webscraped from vagonweb.cz. From 3748 trips handled by ÖBB in Vienna and Lower Austria, the enthustiast-run database contained data on 2092 of them (55.8%). The route score for train compositions was calculated based on data available in @fahrzeugdaten. The attributes involve the presence of following features:

- CCTV
- Wheelchair place
- Bicycle place
- Air Conditioning
- WiFi
- Low Floor

Each route calculated according using the [modified Dijkstra algorithm](## Commuter to connection assignment) receives a score calculated for each of the above amenities. The score indicates the percentage of total route distance with a presence of a selected amenities. As an example: the route consists of 100 kilometers, 90 of which are spent onboard a train equiped with air conditioning, 10 kilometers are spent onboard an older unit without air conditioning. A score for such imaginary trip would be 0.9.

Trip attribute assignment procedure is conducted using Python script available in Appendix 7. For each route considered, each trip within it is checked by the script for information contained in the dataset retrieved from Vagonweb.cz. For trains that do not compose of Electric Multiple Units (EMUs) or Diesel Multiple Units (DMUs), a presence of an amenity in any of carriages is considered as presence of the amenity in the whole composition. With an amenity not present in any of the carriages, EMUs or DMUs within the composition absence of it is marked.

Route amenities are then calculated based on all trips taken during a commute. If certain rolling stock data was not available for a connection, it was interpolated using an average score for all retrieved connections from Vagonweb.cz. The average scores for all connections are shown in Table 4.

| CCTV | Wheelchair | Bicycle | AC   | WiFi | Low Floor |
| ---- | ---------- | ------- | ---- | ---- | --------- |
| 0.6  | 0.77       | 0.97    | 0.88 | 0.27 | 0.6       |

Table: Average scores for connections retrieved from Vagonweb.cz

Summary of each commute is enriched with data on distance, duration and number of necessary changes. Additionally the time of arrival before the desired hour is also added as a column.

Full code covering this calculation is available in Appendix 8.

# Analysis

The data calculated was then used to identify areas with high potential for railway services in terms of passengers but are underserved in terms of timetable offering. Each connection, which was attributed in part **Route score** was assigned number of potential passengers. These were attributed based on their home station and target station, and connection they would need to take in order to make it on time (arriving at 07:20, 07:30, 07:40, or 07:50).  
Stations were then assigned their connection attributes based on weighted average of connection attributes taken. Numbers of potential passengers per connection were considered as weights. Attributes of stations were assigned based on people leaving from station. Each time slot was calculated separately, allowing for both analysis of different commuter distances from destination stations and overall (weighted) analysis. Each station therefore was put in a following data model (example data):

| GTFS ID    | Station Name      | Time of arrival at destination | Potential passengers | CCTV | Wheelchair | Bicycle | AC   | WiFi | Low Floor |
| ---------- | ----------------- | ------------------------------ | -------------------- | ---- | ---------- | ------- | ---- | ---- | --------- |
| at:49:1349 | Wien Hauptbahnhof | 07:20                          | 1500                 | 0.6  | 0.77       | 0.97    | 0.88 | 0.27 | 0.6       |

Times of arrival at destination were attributed based on distances according to [@peperna1982einzugsbereiche] presented by @brezinaPendelnOstregionPotenziale2015. The function states, that only 10% to 30% of people will be willing to walk to their place of work for more than 500 meters if there is public transit available, with 0% to 10% willing to do so at 800m. Therefore only 500m distance was attributed according to walking time. The times of arrival present as follows:

| Distance [meters] | Walking time | Public Transit Time | Preffered time of arrival |
| ----------------- | ------------ | ------------------- | ------------------------- |
| 500               | 6            | 2                   | 07:50                     |
| 1000              | 12           | 4                   | 07:50                     |
| 1500              | 18           | 6                   | 07:50                     |
| 2000              | 24           | 8                   | 07:50                     |
| 4000              | 48           | 18                  | 07:40                     |
| 6000              | 72           | 24                  | 07:30                     |
| 8000              | 96           | 32                  | 07:20                     |

This allowed to calculate number of people potentially commuting in each of the hours, based on 250m rasters and their distances to stations. Each time slot was assigned the sum of people that work or study within a raster assigned the destination station, laying within a set distance. This was conducted using Tableau Prep in 1 second of processing time, contrary to 4 hours of processing time forecasted by `tqdm` package in Python.

TODO: Until 01.01.2025

# Bibliography

<div id="refs"></div>

# Appendix

## Appendix 1

2024 NetEx file structure for infrastructure.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PublicationDelivery xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:siri="http://www.siri.org.uk/siri" xmlns="http://www.netex.org.uk/netex" xsi:schemaLocation="http://www.netex.org.uk/netex http://netex.uk/netex/schema/1.10/xsd/NeTEx_publication.xsd" version="1.10">
	<PublicationTimestamp>2022-09-08T06:17:31.8499236</PublicationTimestamp>
	<ParticipantRef>GIP_OEBB</ParticipantRef>
	<Description>OEBB InfrastructureLinks v-2022.0</Description>
	<dataObjects>
		<CompositeFrame version="001" responsibilitySetRef="OEBB Infrastruktur" id="nap:oebb:CompositeFrame:BS1">
			<Name>OEBB Streckennetz</Name>
			<codespaces>
				<Codespace id="epip_data">
					<Xmlns>nap:oebb</Xmlns>
					<XmlnsUrl>http://netex-cen.eu/epip_data</XmlnsUrl>
					<Description>EPIP data</Description>
				</Codespace>
			</codespaces>
			<FrameDefaults>
				<DefaultCodespaceRef ref="epip_data"/>
				<DefaultLocationSystem>EPSG:4326</DefaultLocationSystem>
			</FrameDefaults>
			<frames>
				<InfrastructureFrame id="nap:oebb:ServiceFrame:SL1:name" version="any">
					<TypeOfFrameRef ref="epip:EU_PI_NETWORK"/>
					<junctions>
                        <RailwayJunction version="any" id="at-47-2184">
							<Name lang="de">Kufstein</Name>
							<Location>
								<Longitude>12.165597</Longitude>
								<Latitude>47.583376999999999</Latitude>
							</Location>
						</RailwayJunction>
					</junctions>
					<elements>
                        <RailwayElement version="any" id="10101:at-43-3314+at-43-4651">
							<Name/>
							<gml:LineString gml:id="id-06893bc0-9bdb-4c30-bba8-025a2e0ffd17-0" srsName="LL-WGS84" srsDimension="2"><gml:posList>16.062011403000042 48.17851540800007 16.061832158000072 48.178456416000074 16.061831980000022 48.17845636700008 16.061523514000044 48.17837180200007 16.061522969000066 48.178371671000036 16.061197048000054 48.17829918100006 16.061193159000027 48.178298417000065 16.06087578100005 48.17824379100006 16.060872377000067 48.178243286000054 16.060541628000067 48.17820212300006 16.060540193000065 48.17820197700007 16.06021362100006 48.17817627900007 16.060212878000073 48.178176233000045 16.05987600000003 48.178164980000076 16.059874425000032 48.17816497200005 16.05948556100003 48.17817124700008 16.059484849000057 48.17817128200005 16.05914733000003 48.178192986000056 16.059144315000026 48.17819323600003 16.058820541000046 48.178226823000045 16.058817745000056 48.178227150000055 16.05849147200007 48.178270317000056 16.058490162000055 48.17827050100004 16.058169341000053 48.178319103000035 16.058168153000054 48.178319284000054 16.057848987000057 48.178371248000076 16.057848093000075 48.17837138600004 16.057520685000043 48.17842556800008 16.05752037800005 48.17842561100008 16.05687187500007 48.17853273500003 16.056856276000076 48.17853529700005 16.056444141000043 48.178603027000065 16.056226851000076 48.17863899100007 16.05592081100002 48.17868980500003 16.05556338100007 48.17874902300008 16.055217898000024 48.17880609700006 16.054920913000046 48.17885535600004 16.054644917000076 48.178901404000044 16.054280779000067 48.17896184600005 16.053951536000056 48.17901632200005 16.053950815000064 48.179016438000076 16.053619542000035 48.17907095100003 16.053296043000046 48.179124381000065 16.05297502700006 48.17917715900006 16.05263790400005 48.179232832000025 16.05232440800006 48.17928429700004 16.051996506000023 48.179338493000046 16.05168900500007 48.179389051000044 16.05168545600003 48.17938962900007 16.051365900000064 48.179441567000026 16.05136341700006 48.17944196700006 16.051036002000046 48.17949391600007 16.05103395900005 48.17949422500004 16.050703938000026 48.17954294800006 16.050703122000073 48.179543058000036 16.050351139000043 48.17958978200005 16.05034960200004 48.17958997100004 16.05002827900006 48.17962642800006 16.050025093000045 48.179626764000034 16.049689021000063 48.17965860500004 16.049685872000055 48.179658876000076 16.04936599900003 48.17968367700007 16.049363545000062 48.17968384200003 16.049003011000025 48.17970501000008 16.049002569000038 48.179705038000066 16.048674532000064 48.17971810100005 16.04867334900007 48.179718138000055 16.04832319700006 48.17972728700005 16.048321866000038 48.17972731000003 16.048089220000065 48.179730465000034 16.04808880300004 48.17973047500004 16.047944142000063 48.179731926000045 16.04794398100006 48.17973193000006 16.047743355000023 48.179733320000025 16.04774300500003 48.179733319000036 16.04706655900003 48.179736311000056 16.045332966000046 48.17974354000006 16.04499320700006 48.17974499400003 16.044240737000052 48.17974834700004 16.043681424000056 48.17975084700004 16.04348241300005 48.179751715000066 16.042923106000046 48.17975405800007 16.042816173000062 48.17975451600006 16.042277855000066 48.17975674500008 16.042256998000028 48.17975682600007 16.042218374000072 48.17975687100005 16.04205287600007 48.179757496000036 16.04149361700007 48.17975998400004 16.04128085600007 48.17976092600003 16.041280116000053 48.17976093400006 16.040711101000056 48.179763457000035 16.040710388000036 48.17976345500006 16.039283367000053 48.17976920600006 16.037264268000058 48.17977755000004 16.036937583000054 48.17977884700008 16.034222541000076 48.179789449000054 16.033549909000044 48.17979223800006 16.033547998000074 48.179792246000034 16.03253690400004 48.17979630900004 16.03173006700007 48.17979942200003</gml:posList></gml:LineString>
							<FromPointRef ref="at-49-560"/>
							<ToPointRef ref="at-49-1003"/>
						</RailwayElement>
					</elements>
				</InfrastructureFrame>
			</frames>
		</CompositeFrame>
	</dataObjects>
</PublicationDelivery>
```

## Appendix 2

Python code used for transforming NetEx from `xml` to `geojson` format.

```python
import xml.etree.ElementTree as ET
import json
from geojson import Point, Feature, FeatureCollection, LineString

# Define file paths as string variables
stations_input_path = "NetEx/ÖBB NetEx files/netex_oebb_StoppPlaces_20231211.xml"
network_input_path = "NetEx/ÖBB NetEx files/netex_oebb_InfrastructureNetwork_20231211.xml"
stops_output_path = "NetEx/ÖBB NetEx files/haltestellen.geojson"
network_output_path = "NetEx/ÖBB NetEx files/network.geojson"


def parse_stations_to_geojson(stations_input_path, stops_output_path):
    # Load the Stations XML from the specified input file
    with open(stations_input_path, "r", encoding="utf-8") as file:
        stations_xml = file.read()

    # Parse the XML
    root = ET.fromstring(stations_xml)

    # Extract Haltestellen (Stops)
    stops = []
    for stop in root.findall(".//{http://www.netex.org.uk/netex}StopPlace"):
        name = stop.find("{http://www.netex.org.uk/netex}Name").text
        description = stop.find("{http://www.netex.org.uk/netex}Description")
        description_text = description.text if description is not None else ""
        longitude = float(stop.find(".//{http://www.netex.org.uk/netex}Longitude").text)
        latitude = float(stop.find(".//{http://www.netex.org.uk/netex}Latitude").text)

        # Extract additional attributes from keyList if present
        key_values = {}
        for key_value in stop.findall(".//{http://www.netex.org.uk/netex}KeyValue"):
            key = key_value.find("{http://www.netex.org.uk/netex}Key").text
            value = key_value.find("{http://www.netex.org.uk/netex}Value").text
            key_values[key] = value

        # Add stop as GeoJSON feature with all attributes
        point = Point((longitude, latitude))
        feature = Feature(
            geometry=point,
            properties={
                "name": name,
                "description": description_text,
                "key_values": key_values,
            },
        )
        stops.append(feature)

    # Create GeoJSON FeatureCollection for stops
    stops_geojson = FeatureCollection(stops)

    # Save to GeoJSON file (creates file if it doesn't exist)
    with open(stops_output_path, "w", encoding="utf-8") as f:
        json.dump(stops_geojson, f, indent=2)
    print("GeoJSON file created for stations:", stops_output_path)


def parse_network_to_geojson(network_input_path, network_output_path):
    # Load the Infrastructure XML from the specified input file
    with open(network_input_path, "r", encoding="utf-8") as file:
        network_xml = file.read()

    # Parse the XML
    root = ET.fromstring(network_xml)

    # Initialize lists to hold GeoJSON features
    railway_junctions = []
    railway_elements = []

    # Extract `RailwayJunction` elements
    for junction in root.findall(".//{http://www.netex.org.uk/netex}RailwayJunction"):
        name = junction.find("{http://www.netex.org.uk/netex}Name").text
        longitude = float(
            junction.find(".//{http://www.netex.org.uk/netex}Longitude").text
        )
        latitude = float(
            junction.find(".//{http://www.netex.org.uk/netex}Latitude").text
        )
        junction_id = junction.get("id")
        version = junction.get("version")

        # Create GeoJSON point feature
        point = Point((longitude, latitude))
        feature = Feature(
            geometry=point,
            properties={"id": junction_id, "version": version, "name": name},
        )
        railway_junctions.append(feature)

    # Extract `RailwayElement` elements
    for element in root.findall(".//{http://www.netex.org.uk/netex}RailwayElement"):
        element_id = element.get("id")
        version = element.get("version")
        name = (
            element.find("{http://www.netex.org.uk/netex}Name").text
            if element.find("{http://www.netex.org.uk/netex}Name") is not None
            else None
        )
        from_point_ref = element.find(
            "{http://www.netex.org.uk/netex}FromPointRef"
        ).get("ref")
        to_point_ref = element.find("{http://www.netex.org.uk/netex}ToPointRef").get(
            "ref"
        )

        # Parse the coordinates in `gml:posList`
        pos_list = (
            element.find(".//{http://www.opengis.net/gml/3.2}posList")
            .text.strip()
            .split()
        )
        coordinates = [
            (float(pos_list[i]), float(pos_list[i + 1]))
            for i in range(0, len(pos_list), 2)
        ]

        # Create GeoJSON LineString feature
        line = LineString(coordinates)
        feature = Feature(
            geometry=line,
            properties={
                "id": element_id,
                "version": version,
                "name": name,
                "from_point_ref": from_point_ref,
                "to_point_ref": to_point_ref,
            },
        )
        railway_elements.append(feature)

    # Create GeoJSON FeatureCollections
    junctions_geojson = FeatureCollection(railway_junctions)
    elements_geojson = FeatureCollection(railway_elements)

    # Save each to GeoJSON file
    with open(
        network_output_path.replace("network.geojson", "junctions.geojson"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(junctions_geojson, f, indent=2)

    with open(network_output_path, "w", encoding="utf-8") as f:
        json.dump(elements_geojson, f, indent=2)

    print("GeoJSON files created for railway junctions and elements.")


# Usage
parse_stations_to_geojson(stations_input_path, stops_output_path)
parse_network_to_geojson(network_input_path, network_output_path)
```

## Appendix 3

Python code used for webscraping the Vagonweb.cz website.

Controller file:

```python
from webscraper import __request_vagonweb__, __extract_train_class__
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import time
import random

trips_path = "GTFS_Simplified/trips.txt"
delimiter = ","


def load_trips(trips_path, delimiter) -> pd.DataFrame:
    trips = pd.read_csv(trips_path, delimiter=delimiter)
    return trips


def extract_trip_identifier(trips_short_name) -> None | set:
    if pd.isna(trips_short_name):
        return None, None
    parts = trips_short_name.split()
    return parts[1], parts[0]


def process_trips(trips: pd.DataFrame) -> dict:
    trips_data = {}
    for trip_short_name in trips["trip_short_name"]:
        number, category = extract_trip_identifier(trip_short_name)
        if number and category:
            trips_data[number] = category
    keyset = trips_data.keys()
    print(len(keyset))
    return trips_data


trips = process_trips(load_trips(trips_path, delimiter))

tripstest = dict(list(trips.items())[3262:])


def scrape(trips: dict) -> dict:
    def standardize_category(category: str) -> str:
        if category == "S":
            return "R"
        else:
            return category

    i = 0
    class_storage = {}
    for train in trips.keys():
        category = standardize_category(trips.get(train))
        train_class = __extract_train_class__(
            __request_vagonweb__("ÖBB", category, train, 2024)
        )
        class_storage[train] = train_class
        i = i + 1
        print("Done " + str(i) + " out of " + str(len(trips.keys())))
    return class_storage


file_path = "vagonweb/webscraping_result.json"
retrieval_path = "vagonweb/retrieval_times.json"


def save_to_json(data: dict, file_path: str) -> None:
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def scrape_and_update(trips: dict, file_path: str) -> None:
    def standardize_category(category: str) -> str:
        if category == "S":
            return "R"
        else:
            return category

    def makeplot(retrieval_data, path) -> None:
        plt.figure(figsize=(10, 6))
        plt.plot(retrieval_data, marker="o")
        plt.title("Retrieval Times")
        plt.xlabel("Request Number")
        plt.ylabel("Time (seconds)")
        plt.grid(True)
        plt.savefig(
            f"/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/{path}.svg"
        )
        plt.savefig(
            f"/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/{path}.svg"
        )
        plt.show()

    try:
        with open(file_path, "r") as json_file:
            existing_data: dict = json.load(json_file)
        with open(
            retrieval_path,
            "r",
        ) as json_file:
            retrieval_times: dict = json.load(json_file)
    except FileNotFoundError:
        existing_data = {}
        retrieval_times = {}

    i = 0
    for train in trips.keys():
        start_time = datetime.now()
        category = standardize_category(trips.get(train))
        train_class = __extract_train_class__(
            __request_vagonweb__("ÖBB", category, train, 2024)
        )
        if not (train_class) and category == "R":
            train_class = __extract_train_class__(
                __request_vagonweb__("ÖBB", "SB", train, 2024)
            )
        existing_data[train] = train_class
        delta = (datetime.now() - start_time).total_seconds()
        retrieval_times[train] = {"order": i, "time": delta}
        with open(file_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
        with open(
            retrieval_path,
            "w",
        ) as json_file:
            json.dump(retrieval_times, json_file, indent=4)
        i += 1
        print(f"Done {i-3262} out of {len(trips.keys())}. Time elapsed: {delta}s")
        time.sleep(random.randrange(0, 360) / 100)

    # Save updated data back to JSON file
    with open(file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)
    with open(
        retrieval_path,
        "w",
    ) as json_file:
        json.dump(retrieval_times, json_file, indent=4)
    makeplot(retrieval_times.values(), "retrieval")

scrape_and_update(tripstest, file_path)
```

Webscraper file:

```python
from urllib.request import Request, urlopen
import urllib.parse as parse_url
from bs4 import BeautifulSoup
import ssl


baseurl = "https://www.vagonweb.cz/razeni/vlak.php?"


def create_request(operator: str, category: str, number: str, year=2024) -> str:
    url = baseurl
    if operator:
        url = url + "&zeme=" + parse_url.quote(operator)
    if category:
        url = url + "&kategorie=" + category
    if number:
        url = url + "&cislo=" + number
    if year:
        url = url + "&rok=" + str(year)
    return url


def __request_vagonweb__(
    operator: str, category: str, number: str, year=2024
) -> BeautifulSoup:
    url = create_request(operator=operator, category=category, number=number, year=year)
    context = ssl._create_unverified_context()
    # headers = {"User-Agent": "PostmanRuntime/7.42.0", "Connection": "keep-alive"}
    req = Request(url)
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    )
    req.add_header("Connection", "keep-alive")

    try:
        response = urlopen(req, context=context)
        html_bytes = response.read()
        html_content = html_bytes.decode("utf-8")  # Decode bytes to string
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()
    return BeautifulSoup(html_content, "html.parser")


def __extract_train_class__(soup: BeautifulSoup) -> list:
    result = []
    vlacek_table = soup.find("table", class_="vlacek")

    if vlacek_table:
        # Use CSS selector to find the desired span element
        selector_carriages = "tr > td.bunka_vozu"
        carriages = vlacek_table.select(selector_carriages)
        for carriage in carriages:
            selector_class = "div > div > span.tab-radam"
            className = carriage.select_one(selector_class)
            if className:
                result.append(className.get_text(strip=True))
    return result
```

## Appendix 4

Processing spatial join of rasters with stations. Calculation of a distance matrix

```python
# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point, MultiPoint, Polygon
import numpy as np
from multiprocessing import Pool, cpu_count

raster_points_Wien = gpd.read_file(
    "ArcGIS/RasterPointsWien_ExportFeatures.shp"
)
print(len(raster_points_Wien))
raster_points_NO = gpd.read_file(
    "ArcGIS/RasterPointsNO.shp"
)
raster_points_ALL = gpd.read_file(
    "ArcGIS/RasterPointsALL.shp"
)
distance_bands_Wien = gpd.read_file(
    "ArcGIS/DistanceAreasWien.shp"
)
distance_bands_NO = gpd.read_file(
    "ArcGIS/Stops_MultipleRingBuffer_ExportFeatures.shp"
)

# %%
print(raster_points_Wien.crs)
distance_bands_Wien = distance_bands_Wien.to_crs(raster_points_Wien.crs)
raster_points_NO = raster_points_NO.to_crs(raster_points_Wien.crs)
distance_bands_NO = distance_bands_NO.to_crs(raster_points_Wien.crs)

# %%

raster_join_wien = raster_points_Wien.sjoin(distance_bands_Wien, how="left")
raster_join_no = raster_points_NO.sjoin(distance_bands_NO, how="left")
print(raster_join_wien.head())
print(f"Vienna data with {len(raster_join_wien)} rows")

# %%
print(raster_join_no.head())
print(f"Lower Austria data with {len(raster_join_no)} rows")

# %%

raster_assigment_union = pd.concat([raster_join_no, raster_points_Wien])
print(f"Unioned data for {len(raster_assigment_union)} assignmens.")
print(raster_assigment_union.head())


# %%
def GetStationsVienna(df=distance_bands_Wien) -> list:
    pattern = r"(at:\d+:\d+).*?(\d+ - \d+)"
    df[["station_code", "range"]] = df["Name"].str.extract(pattern)
    station_codes = df["station_code"].unique().tolist()
    return station_codes


def GetStationsNO(df=distance_bands_NO) -> list:
    station_codes = df["GStopID"].unique().tolist()
    return station_codes


def DistanceMatrixVienna(
    rasters=raster_join_wien, pattern=r"(at:\d+:\d+).*?(\d+ - \d+)"
) -> list:
    # Extract "station_code" and "range" from the "Name" column
    extracted = rasters["Name"].str.extract(pattern)
    rasters["station_code"] = extracted[0]  # Matches the first group (e.g., at:49:94)
    rasters["range"] = extracted[1]  # Matches the second group (e.g., 6000 - 8000)

    # Filter out rows where 'FromBreak' is NaN
    rasters = rasters.dropna(subset=["FromBreak"])

    # Group by 'gid' and construct dictionaries
    matrix = [
        {"gid": gid, **dict(zip(group["station_code"], group["FromBreak"]))}
        for gid, group in rasters.groupby("gid")
    ]

    return matrix


def DistanceMatrixLowerAustria(rasters=raster_join_no, stations=None) -> list:
    # Filter out rows where 'distance' is NaN
    rasters = rasters.dropna(subset=["distance"])

    # Group by 'gid' and construct dictionaries for each group
    matrix = [
        {"gid": gid, **dict(zip(group["GStopID"], group["distance"]))}
        for gid, group in rasters.groupby("gid")
    ]

    return matrix


dist_vienna = DistanceMatrixVienna()
dist_lower_austria = DistanceMatrixLowerAustria()
OD_Vienna = pd.DataFrame(dist_vienna)
OD_Vienna.to_csv("Straßennetz/WienMatrix.csv")
OD_LoverAustria = pd.DataFrame(dist_lower_austria)
OD_LoverAustria.to_csv("Straßennetz/NOMatrix.csv")


def MergeLists(base=dist_lower_austria, to_merge=dist_vienna, key="gid"):
    # Create a dictionary to hold the merged results
    # Convert lists of dictionaries into DataFrames
    df1 = pd.DataFrame(base).set_index(key)
    df2 = pd.DataFrame(to_merge).set_index(key)

    # Merge the two DataFrames on the key, preserving all data
    merged_df = df1.combine_first(df2).reset_index()

    # Convert the merged DataFrame back to a list of dictionaries
    merged_list = merged_df.to_dict(orient="records")
    return merged_list


OD_All = pd.DataFrame(MergeLists())
OD_All.to_csv("Straßennetz/GrossraumWienMatrix.csv")


def exclude_empty_rows(df=OD_All, key="gid") -> pd.DataFrame:
    # Check if all columns except the key column are NaN
    non_empty_mask = ~df.drop(columns=[key]).isna().all(axis=1)

    # Filter the DataFrame to keep only rows that are not completely empty
    non_empty_rows = df[non_empty_mask]
    return non_empty_rows


rasters_with_station = exclude_empty_rows()
rasters_with_station.to_csv("Straßennetz/WithStation.csv")

```

## Appendix 5

Assigning rasters to the nearest station.

```python
import pandas as pd
from multiprocessing import Pool, cpu_count
from datetime import datetime

with_station_path = "Straßennetz/WithStation.csv"


def process_row(row) -> dict[str, str, int]:
    clean_row = row.drop("gid").dropna()
    lowest = clean_row.idxmin()
    return {
        "raster": row["gid"],
        "stop_id": lowest,
        "distance": clean_row[lowest],
        "finished_at": datetime.now(),
    }


def main() -> pd.DataFrame:
    matrix = pd.read_csv(with_station_path, index_col=0)

    # Prepare data for parallel processing
    rows = [row for _, row in matrix.iterrows()]
    num_cores = cpu_count() - 2
    start = datetime.now()
    print(f"Started at {start}")
    with Pool(num_cores) as pool:
        assignments = pool.map(process_row, rows)

    end = datetime.now()
    print(f"Executed {len(rows)} in {end-start}.")
    return pd.DataFrame(assignments)


if __name__ == "__main__":
    main().to_csv("Straßennetz/StationAssignment.csv")
```

## Appendix 6

Modified Dijkstra algorith [@dijkstra1959note], inspired by @Github2018.

```python
import pandas as pd
from collections import defaultdict
import heapq
import datetime
import json
import os
import numpy as np
from tqdm import tqdm


def time_to_seconds(timestr):
    """Convert HH:MM:SS to seconds from midnight."""
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s


def find_route_with_required_arrival(
    origin,
    destination,
    required_arrival_time_str,
    stops,
    stop_times,
    connections,
    arrivals_index,
):
    required_arrival_time = time_to_seconds(required_arrival_time_str)

    if "shape_dist_traveled" not in stop_times.columns:
        raise ValueError(
            "The stop_times.txt file must have a 'shape_dist_traveled' column."
        )

    lookup_df = stop_times.set_index([stop_times.trip_id, stop_times.stop_id])

    latest_arrival = defaultdict(lambda: -1)
    latest_arrival[destination] = required_arrival_time

    pq = [(-required_arrival_time, destination)]
    predecessor = {}

    # Backward search
    while pq:
        cur_neg_time, cur_stop = heapq.heappop(pq)
        cur_time = -cur_neg_time

        if cur_time < latest_arrival[cur_stop]:
            continue

        if cur_stop in arrivals_index:
            for fstop, fdep, tarr, trip_id in arrivals_index[cur_stop]:
                if cur_time >= tarr:
                    if fdep > latest_arrival[fstop]:
                        latest_arrival[fstop] = fdep
                        predecessor[fstop] = (cur_stop, fdep, tarr, trip_id)
                        heapq.heappush(pq, (-fdep, fstop))

    if latest_arrival[origin] == -1:
        # No route found
        return None, None

    # Reconstruct route forward
    route_info = [
        {
            "stop_id": origin,
            "arrival_sec": latest_arrival[origin],
            "departure_sec": None,
            "trip_id": None,
        }
    ]

    current = origin
    while current in predecessor:
        next_stop, fdep, tarr, trip_id = predecessor[current]
        route_info[-1]["departure_sec"] = fdep
        route_info[-1]["trip_id"] = trip_id
        route_info.append(
            {
                "stop_id": next_stop,
                "arrival_sec": tarr,
                "departure_sec": None,
                "trip_id": trip_id,
            }
        )
        current = next_stop

    # Convert times and gather stop info
    for seg in route_info:
        seg["arrival_time_str"] = (
            str(datetime.timedelta(seconds=int(seg["arrival_sec"])))
            if seg["arrival_sec"] is not None and seg["arrival_sec"] >= 0
            else "N/A"
        )
        seg["departure_time_str"] = (
            str(datetime.timedelta(seconds=int(seg["departure_sec"])))
            if seg["departure_sec"] is not None and seg["departure_sec"] >= 0
            else "N/A"
        )

        stop_row = stops[stops.stop_id == seg["stop_id"]]
        seg["stop_name"] = (
            stop_row.iloc[0]["stop_name"] if not stop_row.empty else seg["stop_id"]
        )

    # Changes
    changes = []
    change_count = 0
    origin_dep_sec = (
        route_info[0]["departure_sec"]
        if route_info[0]["departure_sec"] is not None
        else route_info[0]["arrival_sec"]
    )
    final_arr_sec = route_info[-1]["arrival_sec"]

    for i in range(len(route_info)):
        if (
            i > 0
            and route_info[i]["trip_id"] != route_info[i - 1]["trip_id"]
            and route_info[i]["trip_id"] is not None
            and route_info[i - 1]["trip_id"] is not None
        ):
            curr_seg = route_info[i]
            if (
                curr_seg["departure_sec"] is not None
                and curr_seg["arrival_sec"] is not None
            ):
                waiting_time_sec = curr_seg["departure_sec"] - curr_seg["arrival_sec"]
                changes.append(
                    {
                        "station": curr_seg["stop_name"],
                        "duration": int(waiting_time_sec) / 60,
                        "sequence": i,
                    }
                )
                change_count += 1

    # Trip segments
    trip_segments = defaultdict(list)
    for i in range(len(route_info) - 1):
        fseg = route_info[i]
        tseg = route_info[i + 1]
        trip_id = fseg["trip_id"]
        if trip_id is None:
            continue
        fstop = fseg["stop_id"]
        tstop = tseg["stop_id"]
        try:
            f_dist = float(lookup_df.loc[(trip_id, fstop), "shape_dist_traveled"])
            t_dist = float(lookup_df.loc[(trip_id, tstop), "shape_dist_traveled"])
        except KeyError:
            continue

        segment_distance_m = t_dist - f_dist
        if fseg["departure_sec"] is not None and tseg["arrival_sec"] is not None:
            travel_time_sec = tseg["arrival_sec"] - fseg["departure_sec"]
        else:
            continue

        avg_speed_kmh = (
            (segment_distance_m * 3.6) / travel_time_sec if travel_time_sec > 0 else 0
        )

        trip_segments[trip_id].append(
            {
                "from": fseg["stop_name"],
                "departure": fseg["departure_time_str"],
                "to": tseg["stop_name"],
                "arrival": tseg["arrival_time_str"],
                "duration": int(travel_time_sec),
                "distance": int(segment_distance_m),
                "speed": avg_speed_kmh,
            }
        )

    # Build trips_info
    trips_info = {}
    for trip_id, segments in trip_segments.items():
        total_duration = sum(s["duration"] for s in segments)
        total_distance = sum(s["distance"] for s in segments)
        stop_count = len(segments) + 1
        avg_speed_kmh = (
            (total_distance * 3.6 / total_duration) if total_duration > 0 else 0
        )

        trips_info[trip_id] = {
            "from": segments[0]["from"],
            "to": segments[-1]["to"],
            "duration": total_duration,
            "stop_count": stop_count,
            "average_speed": avg_speed_kmh,
            "via": segments,
        }

    total_duration = (
        final_arr_sec - origin_dep_sec
        if (final_arr_sec is not None and origin_dep_sec is not None)
        else 0
    )
    key = f"{origin}-{destination}-{required_arrival_time_str}"
    result = {
        "from": origin,
        "departure": route_info[0]["departure_time_str"],
        "to": destination,
        "arrival": route_info[-1]["arrival_time_str"],
        "trips": trips_info,
        "duration": total_duration,
        "changeCount": change_count,
        "changesAt": changes,
    }

    return key, result


if __name__ == "__main__":
    # Load preprocessed data
    stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
    stop_times = pd.read_csv(
        "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
    )
    connections = pd.read_csv("djkstra/connections.csv")
    with open("djkstra/arrivals_index.json", "r") as f:
        arrivals_index_data = json.load(f)

    arrivals_index = defaultdict(list)
    for k, v in arrivals_index_data.items():
        arrivals_index[k] = v

    # Example: run for multiple (origin, destination) pairs and multiple arrival times
    df = pd.read_csv("pendler/aggregate_pendler.csv")
    origins_destinations = [
        tuple(row) for row in df[["ao_stop_id", "wo_stop_id"]].to_numpy()
    ]

    arrival_times = ["07:20:00", "07:30:00", "07:40:00", "07:50:00"]

    all_results = {}

    for origin, destination in tqdm(
        origins_destinations, desc="Processing origin-destination pairs"
    ):
        for arr_time in arrival_times:
            key, res = find_route_with_required_arrival(
                origin,
                destination,
                arr_time,
                stops,
                stop_times,
                connections,
                arrivals_index,
            )
            if res is not None:
                all_results[key] = res
            else:
                # If no route found, we can also store a placeholder or skip
                all_results[key] = {"error": "No route found"}

    # Save all results to a JSON file
    with open("djkstra/results.json", "w") as f:
        json.dump(all_results, f, indent=2)
```

## Appendix 7

Route amenities score calculation script:

```python
import json
import pandas as pd
from collections import Counter
from tqdm import tqdm

path = "vagonweb/webscraping_result.json"
gtfs_path = "GTFS_Simplified/trips.txt"
def findGTFS() -> pd.DataFrame:
    trips = pd.read_csv(gtfs_path)
    trips["trip_short_name"] = trips["trip_short_name"].str.extract("(\d+)")
    return trips[["trip_short_name", "trip_id", "route_id"]]


def computeAttributes(data: dict) -> pd.DataFrame:
    attribute_list = []
    fahrzeuge = pd.read_csv("vagonweb/OBB Baureihen.csv")
    gtfs = findGTFS()
    for trip in tqdm(data, desc="Processing trips"):
        composition = data.get(trip)
        gtfs_trip_id = (
            gtfs[gtfs["trip_short_name"] == trip]["trip_id"].values[0]
            if not gtfs[gtfs["trip_short_name"] == trip].empty
            else None
        )
        gtfs_route_id = (
            gtfs[gtfs["trip_short_name"] == trip]["route_id"].values[0]
            if not gtfs[gtfs["trip_short_name"] == trip].empty
            else None
        )
        attr = {
            "trip": trip,
            "gtfs-trip-id": gtfs_trip_id,
            "gtfs-route-id": gtfs_route_id,
        }
        for carriage in composition:
            attr = {
                "trip": trip,
                "gtfs-trip-id": gtfs_trip_id,
                "gtfs-route-id": gtfs_route_id,
                "cctv": False,
                "Wheelchair": False,
                "Bicycle": False,
                "ac": False,
                "WiFi": False,
                "LowFloor": False,
                "Year": int,
            }
            attributes = fahrzeuge[fahrzeuge["Number"].isin([carriage])]
            if len(attributes) < 1:
                continue
            attr["ac"] = (
                True
                if attributes["Klimatisierter Fahrgastinnenraum"].values[0] == "ja"
                and ~attr["ac"]
                else False
            )
            attr["Bicycle"] = (
                True
                if attributes["Fahrradplätze"].values[0] == "ja" and ~attr["Bicycle"]
                else False
            )
            attr["cctv"] = (
                True
                if attributes["Videoüberwachung"].values[0] == "ja" and ~attr["cctv"]
                else False
            )
            attr["LowFloor"] = (
                True
                if attributes["Niederflurzustieg"].values[0] == "ja"
                and ~attr["LowFloor"]
                else False
            )
            attr["Wheelchair"] = (
                True
                if attributes["Rollstuhlplätze"].values[0] == "ja"
                and ~attr["Wheelchair"]
                else False
            )
            attr["WiFi"] = (
                True
                if attributes["W-LAN"].values[0] == "ja" and ~attr["WiFi"]
                else False
            )

        attribute_list.append(attr)
    return pd.DataFrame(attribute_list)


def main():
    with open(path, "r") as file:
        data = json.load(file)
    computeAttributes(data).to_csv("vagonweb/trip_attributes.csv")


if __name__ == "__main__":
    main()

```

## Appendix 8

```python
import pandas as pd
import json
from tqdm import tqdm
import numpy as np
import math as skibidi

ROUTINGS_PATH = "djkstra/results.json"
ATTRIBUTES_PATH = "vagonweb/trip_attributes.csv"
AVERAGE_ATTR = {
    "cctv": 0.6,
    "Wheelchair": 0.77,
    "Bicycle": 0.97,
    "ac": 0.88,
    "WiFi": 0.27,
    "LowFloor": 0.6,
}


def main():
    trip_score = pd.read_csv(ATTRIBUTES_PATH, index_col=0)
    with open(ROUTINGS_PATH, "r") as file:
        routings = json.load(file)

    def score_trip(trip: str, duration: int) -> dict:
        trip_attr = trip_score[trip_score["gtfs-trip-id"] == trip]
        attribute_set_count = {
            "cctv": duration,
            "Wheelchair": duration,
            "Bicycle": duration,
            "ac": duration,
            "WiFi": duration,
            "LowFloor": duration,
        }
        if trip_attr.empty:
            attributes = AVERAGE_ATTR
        else:
            attributes = {
                "cctv": (
                    AVERAGE_ATTR.get("cctv") * duration
                    if np.isnan(trip_attr["cctv"].values[0])
                    else (duration if trip_attr["cctv"].values[0] else 0)
                ),
                "Wheelchair": (
                    AVERAGE_ATTR.get("Wheelchair") * duration
                    if np.isnan(trip_attr["Wheelchair"].values[0])
                    else (duration if trip_attr["Wheelchair"].values[0] else 0)
                ),
                "Bicycle": (
                    AVERAGE_ATTR.get("Bicycle") * duration
                    if np.isnan(trip_attr["Bicycle"].values[0])
                    else (duration if trip_attr["Bicycle"].values[0] else 0)
                ),
                "ac": (
                    AVERAGE_ATTR.get("ac") * duration
                    if np.isnan(trip_attr["ac"].values[0])
                    else (duration if trip_attr["ac"].values[0] else 0)
                ),
                "WiFi": (
                    AVERAGE_ATTR.get("WiFi") * duration
                    if np.isnan(trip_attr["WiFi"].values[0])
                    else (duration if trip_attr["WiFi"].values[0] else 0)
                ),
                "LowFloor": (
                    AVERAGE_ATTR.get("LowFloor") * duration
                    if np.isnan(trip_attr["LowFloor"].values[0])
                    else (duration if trip_attr["LowFloor"].values[0] else 0)
                ),
            }
        return attributes, attribute_set_count

    def process_routings(data):
        rows = []
        for key, value in tqdm(data.items(), desc="Processing routings"):
            # Skip the "null" route
            if key == "null":
                continue

            # Extract the fields
            route_from = value.get("from")
            route_to = value.get("to")
            duration = value.get("duration") / 60
            change_count = value.get("changeCount")
            arrival = value.get("arrival")
            arrival_set = key.split("-")[2]

            # Calculate average and total change durations
            changes = value.get("changesAt", [])
            total_change_duration = sum(change["duration"] for change in changes)
            average_change_duration = (
                total_change_duration / change_count
                if change_count and change_count > 0
                else 0
            )

            # Extract trip IDs
            trips = value.get("trips", {})
            trip_attr = []
            trip_attr_set = []
            distances = []
            for trip in trips.keys():
                scores, attribute_set_count = score_trip(
                    trip, duration=trips.get(trip).get("duration")
                )
                trip_attr.append(scores)
                trip_attr_set.append(attribute_set_count)
                distance = pd.DataFrame(trips.get(trip).get("via"))[
                    "distance"
                ].values.tolist()
                distances = distances + distance
            distance = sum(distances)
            trips_attr_df = pd.DataFrame(trip_attr)
            trips_score_result = pd.Series(trips_attr_df.sum(axis=0).to_dict())
            trips_score_count = pd.Series(
                pd.DataFrame(trip_attr_set).sum(axis=0).to_dict()
            )
            trips_calculated = (
                (trips_score_result / trips_score_count).round(1).to_dict()
            )

            row = {
                "from": route_from,
                "to": route_to,
                "arrival": arrival,
                "arrival_set": arrival_set,
                "duration": duration,
                "distance": distance,
                "change count": change_count,
                "average change duration": skibidi.ceil(average_change_duration),
                "total change duration": total_change_duration,
            }
            row.update(trips_calculated)
            rows.append(row)
        return rows

    return process_routings(data=routings)


if __name__ == "__main__":
    pd.DataFrame(main()).to_csv("Trip scoring/trip_scores.csv")
```
