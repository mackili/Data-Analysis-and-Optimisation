---
title: "Key Drivers of Attractiveness of Regional Rail for Commuters: Case Study of Vienna and Lower Austria"
author: [Maciej Kilijański]
date: "11.11.2024"
csl: Bibliography/harvard-cite-them-right.csl
bibliography: [Bibliography/ref.bib]
citeproc: true
output: pdf_document
header-includes:
  - \usepackage{setspace}
  - \linespread{1.5}
...

# Introduction

With local governments of regions all around Europe strive to reduce emissions and congestion caused by citizens' daily commutes, regional rail emerges as a potential solution to this problem. This paper provides a step-by-step guide to building a framework to analyze factors driving popularity of regional rail as a mode of transport people will choose for their daily commute.

The topic is extremely relevant as according to @eurostatPersonsEmploymentCommuting an average European spends 25 minutes commuting to work every workday. Spending almost an hour commuting everyday significantly influences quality of life of commuters [@hanEffectCommutingTime2022a]. Increasing popularity of railway, as a sustainable mode of transport, can bring our society closer to achieving climate neutrality in passenger transport. Rail transport also reduces traffic externalities, therefore improving citizens' life quality [@fagedaLightRailSystems2021a]. This relevance has brought many scientific writers to do research on the topic. Because of significant interest we now understand a lot of ways public transport planners can influence ridership via timetable changes [@asensioTransportModeChoice2002a; @heuermannEffectInfrastructureWorker2019a; @weliwitiyaBicycleTrainIntermodality2019a]. The effects of timetables are clearly visible in one of the regions of Poland, the Dolnośląskie voivodeship. The region has experienced the strongest growth of regional rail's passenger numbers in the country, despite having similar rolling stock to other regions in the country. It has been achieved largely with a sharp increase of the number of connections per day and establishing a minimum standard of 8 pairs of trains operated on each route. This has lead to 22.6% year-to-year increase in passengers transported between 2023 and 2024 [@kolejedolnoslaskieRekordowyStyczenKoleje2024].

However, little to no research has been done regarding the influence of amenities present during such commute on percent of potential commuter demand utilized by railways. This is largely due to lack of official data on rolling stock used on railway connections. Such data is not provided by most of big European railway operators, including České Dráhy, Deutsche Bahn, PKP Intercity and Österreichische Bundesbahnen. This paper aims at establishing a framework for retrieving of such data from a community-based website Vagonweb.cz, and transformation of this data and connecting it to official data for timetable information (GTFS) and official data about railway infrastructure (NetEx).  
A retrieval and transformation process is then conducted for Vienna and Lower Austria region in Austria. Similar process can be repeated for most regions in Central Europe due to availability of necessary data on Vagonweb.cz and usage of industry data exchange standards: GTFS and NetEx.  
The region was a convinient point for developing such framework thanks to an excelent work conducted by @brezinaPendelnOstregionPotenziale2015. Its authors conducted an analysis of commuter potential in the region using similar geospatial methods, but focused heavily on development of passenger potential of railway axis leading into the city of Vienna. Despite that, methods and techniques employed by @brezinaPendelnOstregionPotenziale2015 proved helpful in developing the framework and are heavily utilized in this paper.

The paper uses only three computation tools: ArcGIS Pro for simple geospatial calcualtions, Python programming language for complex processing and Tableau Prep ETL tool for resource intensive dataset filtering and manipulation.

# Data gathering methodology

The framework heavily relies on accessibility of geospatial data from official sources, as well as third-party data from community-based websites run by railway geeks around the world on providing data on rolling stock attributed to connections. In case of Vienna region and the entire Central Europe Vagonweb.cz provides one of the most comprehensive databases.

## NetEx

The Network and Timetable Exchange (NetEx) is a standardized data format, sanctioned by European Union's standard EN 12896 as part of a so-called Transmodel. The Transmodel contains of various data exchange format like NetEx, Siri or OJP and aims at delivering seamless experience for intra and international public transport travel within Europe [@transmodelEN12896].

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

As this paper's primary concern is amenities accessible on railway network and in connections, the only LOS necessary to use is the LOS 1-9. It provides detailed shapes of the rail network, one can measure distances on, station and network junctions locations as well as availability of station amenities like platform clocks, bicycle parkings, WiFi, Park&Ride parkings.

The 2024 NetEx provided by @oebbNetex contains this information in two files - one containing infrastructure information, the other information about stations specifically. A sample of such files can be seen in Appendix 1.

Thanks to the data model being structured in `xml` it allows for creation of flavors in implementation by adding attributes to the data structure with ease. A feature not available so easily using another popular format - `json`.

### Model transformation

Further processing of NetEx data in ArcGIS and Python for geospatial use requires transforming its `xml` format to one readeable by geospatial software. A format of choice in this paper was `geojson`, allowing for easy import and further manipulation. Transformation was conducted in Python using `xml.etree.ElementTree`, `geojson` and `json` packages available via the `pip install` command.

Both files were first imported and parsed using `ET.fromstring()` command, then the procedure exported each of the nodes necessary for further analysis and parsed it's features into a `geojson` feature structure, a comparison of which on example of a station Kapellerfeld can be seen below.

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

Transforming this information not only made it more concise and readable, it also reduced it's size for junction and station files. After importing the transformed data into ArcGIS Pro, a map of the whole railway network in Austria could be constructed (Figure 2).

![Map of Austrian rail network created in ArcGIS Pro using NetEx data. Source: Own work](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/NetEx Map.png)

Full code snippet used for `xml` to `geojson` transformation is available in Appendix 2.

## GTFS

TODO: Until 30.11

### History

### Description of data model

### Model transformation

## Vagonweb

Collecting data about rolling stock assigned to certain connections is a notoriously hard task for public railway operators in Europe. There is no open data policy forced by any of the European regulators to publish such data. For the purpose of this study, the publically available information on each connection was not sufficient

Timetables only provided information on accessibility for disabled people, WiFi, availability of the 1^st^ class, possibility to take bicycles onboard and low-floor carriages. No data on availaility of air conditioning onboard and the age of rolling stock were provided. These were however included in the scope of this study creating a need for alternative sourcing of data.

With no official sources availabe this paper resorted to webscraping of the fan-made online forum created by railway enthusiasts - [vagonweb.cz](https://www.vagonweb.cz/).

TODO: Description and history of vagonweb

### Webscraping - methodology

With lack of an official API supported by the website for downloading the data on rolling stock compositions this paper resorted to webscraping the data. The process was conducted in Python using packages described in Table 1.

| Library          | Description                                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `urllib.request` | Used for executing callouts to the website itself and receiving the data.                                                      |
| `urllib.parse`   | Used for URL parsing for the calluts to be made.                                                                               |
| `BeautifulSoup`  | Used for parsing the data retrieved and retrieving the actual part of data necessary for the analysis from the html structure. |
| `ssl`            | Used for ssl authentication to allow retrieving data using the https protocol.                                                 |

Due to complexity of the webscraping operation, the code was then divided into two files: a controller and a performer. The controler file consisted of functions running locally, importing the list of all connections needing retrieval, controlling the pace of data querying and writing the data back locally. The performer file consisted of methods interacting with the website and processing the html content retrieved. Such setup made code debugging easier and followed code readablility best practices (**SOURCE NEEDED**).

### Creating request URL

The `create_request` method creates a unique request URL for each of the train connections needing retrieval. It takes website's base URL of `https://www.vagonweb.cz/razeni/vlak.php?` and appends necessary information to it. Then a parsed string is returned. The information allowing to retrieve each train were:

- Operator - ÖBB for the case of Lower Austria and Vienna (**SOURCE NEEDED**)
- Category - S for S-Bahn, R for Regio and REX for Regional Expressess. Other categories like CAT (City Airport Train) or long distance D-Zuge, Euro/Inter-City and RailJets were not considered as the scope of this study only includes regional, commuter trains.
- Number - train number
- Year - year of the timetable.

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

###

TODO: Until 06.12

### Description & Problem

### Webscraping: Code and performance

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

# Model calculation

The model considered in this paper will was calculated as following. In order to measure attractiveness of physical infrastructure
for each of the 250m rasters, each raster was first assigned the nearest station based on proximity to their central feature.
Then the bi-directional passenger potentials were calculated for each combination of stations based on the assignment made. Thanks to the availability of GTFS transit data, these potentials were attributed to sets of morning and afternoon connections using a bi-directional network.

Each potential record was also assigned the amenities offered on both stations and rolling stock. This allowed for a _route score_ calculation. The route score was then backfitted with data about potentially necessary train changes and additional time necessary for it. Moreover, each connection was assigned a service frequency score. The last factor accounted for was the time of arrival at the destination station. Following paragraphs provide a detailed description of the calculation process.

## Distance raster to station

In order to assign stations to rasters, each raster had a centroid calculated, from which distance was measured to a station. The centroid calculation was conducted using the Point tool, according to Esri's documentation (https://pro.arcgis.com/en/pro-app/latest/help/editing/create-point-and-multipoint-features.htm). The raster dataset was retrieved from Statistik Austria and filtered by location to only include rasters that intersect communities within Lower Austria and Vienna (https://www.data.gv.at/katalog/dataset/566c99be-b436-365e-af4f-27be6c536358). Filtering was conducted using Gemeinde Ids. This allowed the Raster dataset to shrink from over a million rows to 316317. The facility assignment tool of the Network Analyst toolbox in ArcGIS Pro requires points as features to assign, hence a centroid of each raster was calculated. For this the Feature to Point tool of ArcGIS Pro was used (https://support.esri.com/en-us/knowledge-base/how-to-find-the-centroid-of-polygons-using-calculate-ge-000021849). Assignment of each raster centroid to the nearest station was conducted using the road network for Vienna and Lower Austria and Network Analyst tool in ArcGIS Pro. The size of the dataset was posing a problem:

- 381 stations (_Facilities_)
- 316.317 rasters (_Incidents_)

Giving $381\cdot316.317=120.516.777$ possible combinations.

Such number of calculations turned out to be infeasible for ArcGIS Pro as the problem would not even construct. Therefore, heuristics became a necessity. Following the example of previous analysis (https://www.arbeiterkammer.at/infopool/wien/Verkehr_und_Infrastruktur_56.pdf), each station was assigned a distance band along the road network. The distance bands were weighted, which later allowed to assign points for closeness of a station. Still following the reasoning of (https://www.arbeiterkammer.at/infopool/wien/Verkehr_und_Infrastruktur_56.pdf), the distance bands calculated for each station were:

- 500 meters
- 1000 meters
- 1500 meters
- 2000 meters
- 4000 meters
- 6000 meters
- 8000 meters

![Distance bands around stations](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/DistanceBands.png)

Then, each raster was assigned to a station based on the distance band it fell into. Rasters further than 8000 meters were excluded from the analysis. This filtering was conducted by intersecting rasters with 8km distance bands. The following method allowed to construct an origin-destination matrix for all 381 stations in Lower Austria and Vienna as destinations and x rasters within 8 km from a station. Due to low quality of data on road network in Lower Austria, the bands could not be calculated according to it and were calculated as Straight-line distances.

![Final Raster Selection](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/Maps/Selected Rasters.png)

The rasters were attributed to stations using `geopandas` package in Python. The scale of necessary calculations showed to be impossible to execute in ArcGIS Pro.

### Raster to station attribution process in Python

Data exported from ArcGIS Pro as `shp` files was loaded to Python using the `geopandas` package.

```python
import geopandas as gpd
raster_points_Wien = gpd.read_file(
    "ArcGIS/RasterPointsWien_ExportFeatures.shp"
)
raster_points_NO = gpd.read_file(
    "ArcGIS/RasterPointsNO.shp"
)
distance_bands_Wien = gpd.read_file(
    "ArcGIS/DistanceAreasWien.shp"
)
distance_bands_NO = gpd.read_file(
    "ArcGIS/Stops_MultipleRingBuffer_ExportFeatures.shp"
)
```

In order to execute a spacial join operation correctly, all geometries were transformed to use one referencing system

```python
distance_bands_Wien = distance_bands_Wien.to_crs(raster_points_Wien.crs)
raster_points_NO = raster_points_NO.to_crs(raster_points_Wien.crs)
distance_bands_NO = distance_bands_NO.to_crs(raster_points_Wien.crs)
```

As stations in Vienna were considered separately, due to better quality of road network data, spatial join operations were conducted separately for Vienna and Lower Austria.

```python
raster_join_wien = raster_points_Wien.sjoin(distance_bands_Wien, how="left")
raster_join_no = raster_points_NO.sjoin(distance_bands_NO, how="left")
```

With joins ready, the data was transformed into lists of dictionaries for Vienna and Lower Austria and then merged. All lists were transformed into pandas dataframes and saved as `csv` files for further processing.

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
```

TODO: Until 13.12

## Station to station passenger potential based on Pendler dataset

Each raster was assigned a station based on a distance from it to a station. The shorter distance was assigned to a raster. In case of many stations being within the same distance band they were assigned randomly with uniform probability. Due to the size of the dataset multicore processing was utilized in Python using the `multiprocessing` package. Final code used is available in the appendix.

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

Thanks to no use of loops and multicore processing the whole calculation executed in 12.4 seconds for 197.820 rows. The assigned station assignment was then used to aggregate station-to-station passenger flows. Each station had a sum departing and arriving passengers calculated. These sums were calculated in the same form as in the Pendler dataset from Statistik Austria, meaning a total of commuters, work commuters and school commuters. The formula for calculation was:
$$\sum_{r\in R} passengers_{r}$$
$$\text{Where } r\text{ represents a raster in Rasters } R$$

The aggregation was conducted in Tableau Prep, due to large scale of calculations needed. An ETL tool handled necessary work in very low time, while testing in Python proved to be challenging for the tool. At this point a graphical representation of results was possible to present. This was presented in Tableau.

![Commuter Balance Map](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Commuter Balance Map.png)

Figure above displays a map of commuter balances for stations in Vienna and Lower Austria. Size of the dot demarks total number of commuters that could potentially utilize the station, both leaving from it (from their place of residence) and arriving at it (to their place of work/study). Color denotes the balance between commuters leaving from and arriving to a station. Three categories were selected: red denotes negative commuter balance (more people leaving than arriving), yellow denotes close to equal yet positive commuter balance and green a strongly positive commuter balance.  
What turns attention quickly is the concentration of strongly positive stations in Vienna city center (with the exception of Wien Hauptbahnhof). Outside of Vienna only 14 stations had a strong positive balance: St. Pölten Hauptbahhof, Krems, Tulln, Katzelsdorf, St. Pölten Bildungscampus, Hollabrunn, Amstetten, Brunn-Maria Enzendorf, Achau, Horn, Gunstramsdorf Thallern, Korneuburg, Wieselburg, Fischamend.

![Biggest potential stations excluding Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Busiest Stations without Vienna.png)

Including Vienna the station potential diagram becomes dominated by the metropoly. 6 biggest potential stations are in Vienna, followed by Brunn-Maria-Enzersdorf (close to Vienna), which is then followed by another 8 stations in Vienna. This is visible in Figure x.

![Biggest potential stations including Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Busiest Stations.png)

In order to calculate amenities available for each commute to work, necessary routings were calculated. As rasters do differ in proximity to stations, this paper once again takes inspiration from https://www.arbeiterkammer.at/infopool/wien/Verkehr_und_Infrastruktur_56.pdf and calculates necessary commutes for both SLOW and MIV modes of transport. This time we took into consideration walking time calculated with data from https://doi.org/10.1016/j.sbspro.2012.12.237. The average walking pace was 1.4 meters per second, which translates to 5 km/h. Moreover, considering Figure 6, 65% of all commuters arrive in Vienna, therefore in order to calculate the MIV transit option for the average speed of Vienese trams was taken into account. This was measured to be 15.44 km/h (https://repositum.tuwien.at/bitstream/20.500.12708/193238/1/Steinwidder%20Paul%20-%202024%20-%20Bewertungsverfahren%20zur%20Analyse%20der...pdf). The time to final destination was calculated for each of the distance bands, then rounded up to a full minute:

![Commuters arriving in Vienna vs. outside of Vienna](/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/Arrivals Vienna vs. Rest.png)

| Distance [meters] | Walking time | Public Transit Time |
| ----------------- | ------------ | ------------------- |
| 500               | 6            | 2                   |
| 1000              | 12           | 4                   |
| 1500              | 18           | 6                   |
| 2000              | 24           | 8                   |
| 4000              | 48           | 18                  |
| 6000              | 72           | 24                  |
| 8000              | 96           | 32                  |

From this table bins were calculated for time necessary to arrive before 8 - the normal work and school start hour in Austria (**SOURCE**). The bins were: 10 minutes prior, 20 minutes prior, 30 minutes prior and 40 minutes prior. Values larger than these were removed due to unlikely nature of such commute.  
Station to station times were then calculated using the method described and developed in @Github2018. The script was modified to accomodate necessary restriction regarding arrival times (bins). The script imported filtered and simplified GTFS data from ÖBB and calculated shortest paths for each set of stations using the Djkstra algorithm. This allowed to save data on commute between each set of stations for each arrival time for the morning rush. Results were then saved as a `json` file structured in a following way:

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

Such structure provided a way to calculate necessary routes once and contain all possibly necessary information for further calculations.

TODO: Until 13.12

## Station to station amenities calcualtion

TODO: Until 13.12

### Amenities per station score

Amenities at each station considered by the analysis (Vienna and Lower Austria only) were extracted using Python from Netex files available at https://data.oebb.at/de/datensaetze~netex-geodaten~.

### Route score

Data was webscraped from vagonweb.cz. From 3748 trips handled by ÖBB in Vienna and Lower Austria, the enthustiast-run database contained data on 2092 of them (55.8%). The route score for train compositions was calculated based on data available from ÖBB https://data.oebb.at/de/datensaetze~fahrzeuge-personenverkehr~. Trips were attributed with following:

- CCTV
- Wheelchair place
- Bicycle place
- Air Conditioning
- WiFi
- Low Floor
- Year built

Route attribute assignment procedure was conducted using Python script below. Each trip from GTFS feed was retrieved from `json` file from vagonweb.cz. Data on composition were then retrieved and checked against official dataset of ÖBB. If composition contained certain amenity in any of carriages, it was marked as true, otherwise a false value was given.

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
    # computeStatistics(data)
    computeAttributes(data).to_csv("vagonweb/trip_attributes.csv")


if __name__ == "__main__":
    main()

```

#### Connection score

Connection amenities were calculated based on all trips taken during a commute. They were then weighted based on travel duration on each train co create a score between 0 and 1, based on each trips' attributes. 0 meaning a complete lact of amenity during the travel and 1 meaning accessibility of amenity during the entire travel. Year built value was calculated as a weighted average and the rounded to a full year. If certain rolling stock data was not available for a connection, it was interpolated using an average score for all retrieved connections from vagonweb.cz. The average scores for all connections were:

| CCTV | Wheelchair | Bicycle | AC   | WiFi | Low Floor |
| ---- | ---------- | ------- | ---- | ---- | --------- |
| 0.6  | 0.77       | 0.97    | 0.88 | 0.27 | 0.6       |

Calculations were conducted using `Trip scoring/scoring.py` and `vagonweb/trip_score.py` Python scripts.

# Analysis

The data calculated was then used to identify areas with high potential for railway services in terms of passengers but are underserved in terms of timetable offering. Each connection, which was attributed in part **Route score** was assigned number of potential passengers. These were attributed based on their home station and target station, and connection they would need to take in order to make it on time (arriving at 07:20, 07:30, 07:40, or 07:50).  
Stations were then assigned their connection attributes based on weighted average of connection attributes taken. Numbers of potential passengers per connection were considered as weights. Attributes of stations were assigned based on people leaving from station. Each time slot was calculated separately, allowing for both analysis of different commuter distances from destination stations and overall (weighted) analysis. Each station therefore was put in a following data model (example data):

| GTFS ID    | Station Name      | Time of arrival at destination | Potential passengers | CCTV | Wheelchair | Bicycle | AC   | WiFi | Low Floor |
| ---------- | ----------------- | ------------------------------ | -------------------- | ---- | ---------- | ------- | ---- | ---- | --------- |
| at:49:1349 | Wien Hauptbahnhof | 07:20                          | 1500                 | 0.6  | 0.77       | 0.97    | 0.88 | 0.27 | 0.6       |

Times of arrival at destination were attributed based on distances according to (Peperna, 1982) presented by https://www.arbeiterkammer.at/infopool/wien/Verkehr_und_Infrastruktur_56.pdf. The function states, that only 10% to 30% of people will be willing to walk to their place of work for more than 500 meters if there is public transit available, with 0% to 10% willing to do so at 800m. Therefore only 500m distance was attributed according to walking time. The times of arrival present as follows:

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

# Bibliography
