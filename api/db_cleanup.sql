DROP TABLE IF EXISTS tmp_sets_info;
DROP TABLE IF EXISTS tmp_scores;
DROP TABLE IF EXISTS tmp_element_prices;

-- Create tmp tables to store generated data --
CREATE TABLE tmp_sets_info (
	set_num TEXT NOT NULL UNIQUE,
	eol VARCHAR(2) DEFAULT -1,
	name_de TEXT,
	lego_slug TEXT
);

CREATE TABLE tmp_scores (
	set_num TEXT,
	fig_num TEXT,
	score FLOAT NOT NULL,
	calc_date DATE NOT NULL
);

CREATE TABLE tmp_element_prices (
	element_id TEXT NOT NULL,
	provider_id INTEGER NOT NULL,
	price INTEGER NOT NULL
);

CREATE TABLE tmp_set_prices (
	set_num TEXT NOT NULL,
	check_date DATE NOT NULL,
	retail_price INTEGER NOT NULL
);


-- Insert generated data into tmp tables
INSERT INTO tmp_sets_info
SELECT set_num, eol, name_de, lego_slug FROM sets WHERE eol <> '-1' or name_de is not null or lego_slug is not null;

INSERT INTO tmp_scores
SELECT DISTINCT s.set_num, m.fig_num, sc.score, sc.calc_date FROM scores sc
LEFT JOIN inventories i ON sc.inventory_id = i.id
LEFT JOIN minifig_inventory_rel mir ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON mir.inventory_minifig_id = im.id
LEFT JOIN sets s ON i.set_id = s.id
LEFT JOIN minifigs m ON im.fig_id = m.id;

INSERT INTO tmp_element_prices
SELECT element_id, provider_id, price FROM element_prices;

INSERT INTO tmp_set_prices
SELECT s.set_num, sp.check_date, sp.retail_price FROM set_prices sp
LEFT JOIN sets s ON sp.set_id = s.id;


-- Delete queries --
TRUNCATE
colors, minifigs, part_categories, themes, sets, parts, part_color_frequency_element_rel, part_color_frequencies,
inventories, part_relationships, inventory_minifigs, inventory_sets, inventory_parts,
minifig_inventory_rel, set_inventory_rel, scores, element_prices, statistics, minifig_similarities CASCADE;

-- Drop tables

DROP TABLE IF EXISTS colors CASCADE;
DROP TABLE IF EXISTS part_color_frequency_element_rel CASCADE;
DROP TABLE IF EXISTS inventories CASCADE;
DROP TABLE IF EXISTS inventory_minifigs CASCADE;
DROP TABLE IF EXISTS inventory_parts CASCADE;
DROP TABLE IF EXISTS inventory_sets CASCADE;
DROP TABLE IF EXISTS minifig_inventory_rel CASCADE;
DROP TABLE IF EXISTS minifigs CASCADE;
DROP TABLE IF EXISTS part_categories CASCADE;
DROP TABLE IF EXISTS part_color_frequencies CASCADE;
DROP TABLE IF EXISTS part_relationships CASCADE;
DROP TABLE IF EXISTS parts CASCADE;
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS set_prices CASCADE;
DROP TABLE IF EXISTS set_inventory_rel CASCADE;
DROP TABLE IF EXISTS sets CASCADE;
DROP TABLE IF EXISTS statistics CASCADE;
DROP TABLE IF EXISTS themes CASCADE;
DROP TABLE IF EXISTS element_prices CASCADE;
DROP TABLE IF EXISTS minifig_similarities CASCADE;
