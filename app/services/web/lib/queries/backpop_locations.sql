WITH
  book_locations AS (
  SELECT
    BookMeta_Title,
    BookMeta_Author,
    SPLIT(V2Locations,';') AS locations
  FROM
    `gdelt-bq.hathitrustbooks.{year}`)
SELECT
  BookMeta_Title AS title,
  BookMeta_Author AS author,
  STRING_AGG(location, "|") AS location
FROM (
  SELECT
    BookMeta_Title,
    BookMeta_Author,
    CONCAT(lat, "~", long, "~", cnt,"~",name) AS location
  FROM (
    SELECT
      *,
      count(*) cnt
    FROM (
      SELECT
        CAST(BookMeta_Title AS STRING) AS BookMeta_Title,
        CAST(BookMeta_Author AS STRING) AS BookMeta_Author,
        ROUND(SAFE_CAST(REGEXP_EXTRACT(locations,r'^[2-5]#.*?#.*?#.*?#.*?#(.*?)#.*?#') AS FLOAT64),3) AS lat,
        ROUND(SAFE_CAST(REGEXP_EXTRACT(locations,r'^[2-5]#.*?#.*?#.*?#.*?#.*?#(.*?)#') AS FLOAT64),3) AS long,
        CAST(REGEXP_EXTRACT(locations,r'^[2-5]#(.*?)#.*?#.*?#.*?#.*?#.*?#') AS STRING) AS name
      FROM
        book_locations,
        UNNEST(locations) AS locations )
    WHERE
      CAST(lat AS float64) IS NOT NULL
      AND CAST(long AS float64) IS NOT NULL
    GROUP BY
      BookMeta_Title,
      BookMeta_Author,
      lat,
      long,
      name))
GROUP BY
  BookMeta_Title,
  BookMeta_Author