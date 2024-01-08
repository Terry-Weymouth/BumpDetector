drop index if exists long_lat_original_gix;
drop index if exists long_lat_remapped_gix;
drop table if exists bicycle_track;
drop table if exists bicycle_data;
drop table if exists map_matching_roads;

create table bicycle_track (
  track_id serial primary key,
  file_path varchar(256),
  max_distance float,
  time timestamp not null
  );

create table bicycle_data (
  id serial primary key,
  track_id integer,
  g1 integer,
  g2 integer,
  g3 integer,
  g4 integer,
  g5 integer,
  g6 integer,
  gmax integer,
  time timestamp,
  lat float,
  long float,
  alt float,
  speed float,
  delta_time integer,
  long_lat_original geometry(POINT,4326),
  nearest_road_id bigint,
  nearest_road_distance float,
  long_lat_remapped geometry(POINT,4326),  -- projected track point after match to road
  viterbi_nearest_road_id bigint,
  viterbi_nearest_road_distance float
  );

CREATE INDEX long_lat_original_gix ON bicycle_data USING GIST ( long_lat_original );
CREATE INDEX long_lat_remapped_gix ON bicycle_data USING GIST ( long_lat_remapped );

create table map_matching_roads(
  id serial primary key,
  track_id integer,
  osm_id bigint
);