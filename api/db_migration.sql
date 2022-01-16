DROP TABLE IF EXISTS tmp_part_freq;
DROP TABLE IF EXISTS tmp_act_set_score;
DROP TABLE IF EXISTS tmp_act_minifig_score;
DROP TABLE IF EXISTS tmp_minifig_props;
DROP TABLE IF EXISTS tmp_fig_similarities;
--- Insert queries --

-- Base tables
INSERT INTO colors (id, name, rgb, is_trans)
SELECT id, name, rgb, is_trans FROM colors_tmp;

INSERT INTO minifigs (fig_num, name, num_parts)
SELECT fig_num, name, num_parts FROM minifigs_tmp;

INSERT INTO part_categories (id, name)
SELECT id, name FROM part_categories_tmp;

INSERT INTO themes (id, name, parent_id)
SELECT id, name, parent_id FROM themes_tmp;

INSERT INTO sets (set_num, name, year_of_publication, theme_id, num_parts)
SELECT set_num, name, year_of_publication, theme_id, num_parts FROM sets_tmp;

INSERT INTO parts (part_num, name, part_cat_id, part_material)
SELECT part_num, name, part_cat_id, part_material FROM parts_tmp;

INSERT INTO part_color_frequencies (part_id, color_id)
SELECT DISTINCT p.id, c.id FROM inventory_parts_tmp ip
LEFT JOIN parts p ON p.part_num = ip.part_num
LEFT JOIN colors c ON c.id = ip.color_id;

INSERT INTO inventories (id, set_id, version)
SELECT t.id, s.id, version FROM inventories_tmp t
LEFT JOIN sets s ON t.set_num = s.set_num;

INSERT INTO part_relationships (rel_type, child_part_id, parent_part_id)
SELECT rel_type, p1.id, p2.id FROM part_relationships_tmp t
LEFT JOIN parts p1 ON t.child_part_num = p1.part_num
LEFT JOIN parts p2 ON t.parent_part_num = p2.part_num;

INSERT INTO inventory_minifigs (inventory_id, fig_id, quantity)
SELECT inventory_id, m.id, quantity FROM inventory_minifigs_tmp t
LEFT JOIN minifigs m ON m.fig_num = t.fig_num;

INSERT INTO inventory_sets (inventory_id, set_id, quantity)
SELECT inventory_id, s.id, quantity FROM inventory_sets_tmp t
LEFT JOIN sets s ON s.set_num = t.set_num;

INSERT INTO part_color_frequency_element_rel (element_id, part_color_frequency_id)
SELECT e.element_id, pcf.id FROM elements_tmp e
LEFT JOIN parts p ON e.part_num = p.part_num
LEFT JOIN colors c ON e.color_id = c.id
LEFT JOIN part_color_frequencies pcf ON p.id = pcf.part_id AND c.id = pcf.color_id
WHERE pcf.id IS NOT NULL;

INSERT INTO inventory_parts (inventory_id, part_color_frequency_id, is_spare, quantity)
SELECT inventory_id, pcf.id, is_spare, quantity FROM inventory_parts_tmp t
LEFT JOIN parts p ON t.part_num = p.part_num
LEFT JOIN colors c ON t.color_id = c.id
LEFT JOIN part_color_frequencies pcf ON p.id = pcf.part_id AND c.id = pcf.color_id
WHERE pcf.id IS NOT NULL;

-- Generated FROM base tables
INSERT INTO minifig_inventory_rel (inventory_id, inventory_minifig_id, quantity)
SELECT i.id, im.id, im.quantity FROM inventory_minifigs im
LEFT JOIN minifigs m ON im.fig_id = m.id
LEFT JOIN inventories_tmp i ON m.fig_num = i.set_num;

INSERT INTO set_inventory_rel (inventory_id, inventory_set_id)
SELECT i.id, invs.id FROM inventory_sets invs
LEFT JOIN sets s ON invs.set_id = s.id
LEFT JOIN inventories_tmp i ON s.set_num = i.set_num;

-- Update inventories table (is_latest)
DROP VIEW IF EXISTS v_latest_inventory;
CREATE VIEW v_latest_inventory as
SELECT i.id FROM (SELECT * FROM inventories WHERE set_id IS NOT NULL) i
LEFT JOIN (SELECT set_id, max(version) AS max_version FROM inventories GROUP BY set_id) AS max_i ON i.set_id = max_i.set_id AND i.version = max_i.max_version
WHERE max_i.set_id IS NOT NULL
UNION ALL
SELECT mir.inventory_id FROM minifig_inventory_rel mir
LEFT JOIN inventories i ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON im.id = mir.inventory_minifig_id
LEFT JOIN (SELECT im.fig_id, max(i.version) AS max_version FROM minifig_inventory_rel mir
LEFT JOIN inventories i ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON im.id = mir.inventory_minifig_id
GROUP BY im.fig_id) AS im_max ON im_max.fig_id = im.fig_id AND im_max.max_version = i.version;

UPDATE inventories SET is_latest = TRUE WHERE inventories.id IN (SELECT id FROM v_latest_inventory);
UPDATE inventories SET is_latest = FALSE WHERE inventories.id NOT IN (SELECT id FROM v_latest_inventory);


-- Update part_color_frequencies table (quantity)
DROP VIEW IF EXISTS v_total_quantities;
CREATE VIEW v_total_quantities as
SELECT subq.part_color_frequency_id, sum(subq.quantity) AS quantity
FROM (SELECT ip.part_color_frequency_id, sum(ip.quantity) AS quantity
FROM (SELECT * FROM inventories WHERE is_latest = TRUE AND set_id IS NOT NULL) i
LEFT JOIN inventory_parts ip ON i.id = ip.inventory_id
GROUP BY ip.part_color_frequency_id
UNION ALL
SELECT ip.part_color_frequency_id, sum(ip.quantity * im.quantity) AS quantity FROM minifig_inventory_rel mir
LEFT JOIN (SELECT * FROM inventories WHERE is_latest = TRUE AND set_id is NULL) i ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON im.id = mir.inventory_minifig_id
LEFT JOIN inventory_parts ip ON i.id = ip.inventory_id
GROUP BY ip.part_color_frequency_id) AS subq
GROUP BY subq.part_color_frequency_id;

CREATE TABLE tmp_part_freq (
	part_color_frequency_id INTEGER UNIQUE NOT NULL,
	quantity INTEGER NOT NULL
);

INSERT INTO tmp_part_freq
SELECT part_color_frequency_id, quantity FROM v_total_quantities WHERE part_color_frequency_id IS NOT NULL;

UPDATE part_color_frequencies pcf
SET
      total_amount = (SELECT quantity 
                            FROM tmp_part_freq
                            WHERE tmp_part_freq.part_color_frequency_id = pcf.id)
WHERE
    EXISTS (
        SELECT *
        FROM tmp_part_freq
        WHERE tmp_part_freq.part_color_frequency_id = pcf.id
    );

DROP TABLE IF EXISTS tmp_part_freq;


DROP VIEW IF EXISTS v_total_quantities;
DROP VIEW IF EXISTS v_latest_inventory;

-- Update generated data --
UPDATE sets
SET
      (eol, retail_price) = (SELECT tmp_sets_info.eol, tmp_sets_info.retail_price
                            FROM tmp_sets_info
                            WHERE tmp_sets_info.set_num = sets.set_num)
WHERE
    EXISTS (
        SELECT *
        FROM tmp_sets_info
        WHERE tmp_sets_info.set_num = sets.set_num
    );

INSERT INTO scores (inventory_id, score, calc_date)
SELECT i.id AS inventory_id, tsc.score, tsc.calc_date FROM tmp_scores tsc
LEFT JOIN sets s ON s.set_num = tsc.set_num
LEFT JOIN inventories i ON i.set_id = s.id AND i.is_latest = TRUE
WHERE tsc.set_num IS NOT NULL AND i.id IS NOT NULL
UNION ALL
SELECT DISTINCT i.id AS inventory_id, tsc.score, tsc.calc_date FROM tmp_scores tsc
LEFT JOIN minifigs m ON m.fig_num = tsc.fig_num
LEFT JOIN inventory_minifigs im ON im.fig_id = m.id
LEFT JOIN minifig_inventory_rel mir ON mir.inventory_minifig_id = im.id
LEFT JOIN inventories i ON i.id = mir.inventory_id AND i.is_latest = TRUE
WHERE tsc.fig_num IS NOT NULL AND i.id IS NOT NULL;

INSERT INTO element_prices (element_id, provider_id, price)
SELECT pcfer.id, tep.provider_id, tep.price FROM tmp_element_prices tep
LEFT JOIN part_color_frequency_element_rel pcfer on pcfer.element_id = tep.element_id
WHERE pcfer.id IS NOT NULL;

-- Set score ids
CREATE TABLE tmp_act_set_score (
	set_id INTEGER NOT NULL,
	score_id INTEGER NOT NULL
);

CREATE UNIQUE INDEX tmp_act_set_index ON tmp_act_set_score (set_id);

DROP VIEW IF EXISTS v_sets_scores;
CREATE VIEW v_sets_scores AS
    SELECT DISTINCT s.id AS set_id, sc.id AS score_id FROM (
        SELECT * FROM scores WHERE id IN (SELECT DISTINCT
        first_value(id) OVER (PARTITION BY inventory_id ORDER BY calc_date DESC)
        FROM scores
        ORDER BY 1
    )) SC
    LEFT JOIN inventories i ON SC.inventory_id = i.id
    LEFT JOIN sets s ON i.set_id = s.id
    WHERE s.id IS NOT NULL;

INSERT INTO tmp_act_set_score
select * from v_sets_scores;

UPDATE sets SET score_id = (SELECT score_id FROM tmp_act_set_score WHERE tmp_act_set_score.set_id = sets.id);
DROP VIEW IF EXISTS v_sets_scores;
DROP TABLE IF EXISTS tmp_act_set_score;


CREATE TABLE tmp_act_minifig_score (
	minifig_id INTEGER NOT NULL,
	score_id INTEGER NOT NULL
);

CREATE UNIQUE INDEX tmp_act_minifig_index ON tmp_act_minifig_score (minifig_id);

DROP VIEW IF EXISTS v_inventory_minifigs_scores;
CREATE VIEW v_inventory_minifigs_scores AS
    SELECT DISTINCT im.id AS minifig_id, sc.id AS score_id FROM (
        SELECT * FROM scores WHERE id IN (SELECT DISTINCT
        first_value(id) OVER (PARTITION BY inventory_id ORDER BY calc_date DESC)
        FROM scores
        ORDER BY 1
    )) SC
    LEFT JOIN inventories i ON SC.inventory_id = i.id
    LEFT JOIN minifig_inventory_rel mir ON i.id = mir.inventory_id
    LEFT JOIN inventory_minifigs im ON mir.inventory_minifig_id = im.id
    WHERE im.id IS NOT NULL;

INSERT INTO tmp_act_minifig_score
select * from v_inventory_minifigs_scores;

UPDATE inventory_minifigs SET score_id = (
    SELECT score_id FROM tmp_act_minifig_score WHERE
    tmp_act_minifig_score.minifig_id = inventory_minifigs.id
);
DROP VIEW IF EXISTS v_inventory_minifigs_scores;
DROP TABLE IF EXISTS tmp_act_minifig_score;

-- Set root theme ids
DROP VIEW IF EXISTS v_root_theme;
CREATE VIEW v_root_theme AS
SELECT s.id, COALESCE(t3.id, t2.id, t1.id) AS root_theme_id
FROM sets s
LEFT JOIN themes t1 ON s.theme_id = t1.id
LEFT JOIN themes t2 ON t2.id = t1.parent_id
LEFT JOIN themes t3 ON t3.id = t2.parent_id;
UPDATE sets SET root_theme_id = (
    SELECT root_theme_id FROM v_root_theme WHERE
    v_root_theme.id = sets.id
);
DROP VIEW IF EXISTS v_root_theme;

-- Determine if set has stickers
UPDATE sets SET has_stickers = 't' WHERE id in (
    select distinct s.id from sets s
    left join inventories i on s.id = i.set_id
    left join inventory_parts ip on i.id = ip.inventory_id
    left join part_color_frequencies pcf on ip.part_color_frequency_id = pcf.id
    left join parts p on pcf.part_id = p.id
    left join part_categories pc on p.part_cat_id = pc.id
    where pc.name = 'Stickers'
);

-- Update minifig properties
DROP VIEW IF EXISTS v_minifig_has_unique_part;
CREATE VIEW v_minifig_has_unique_part AS
SELECT m.id, MIN(pcf.total_amount) = 1 AS has_unique_part FROM minifigs m
LEFT JOIN inventory_minifigs im ON m.id = im.fig_id
LEFT JOIN minifig_inventory_rel mir ON im.id = mir.inventory_minifig_id
LEFT JOIN inventories i ON i.id = mir.inventory_id and i.is_latest = TRUE
LEFT JOIN (SELECT inventory_id, part_color_frequency_id, sum(quantity) AS quantity FROM inventory_parts GROUP BY inventory_id, part_color_frequency_id) ip ON i.id = ip.inventory_id
LEFT JOIN part_color_frequencies pcf ON ip.part_color_frequency_id = pcf.id
GROUP BY m.id;

DROP VIEW IF EXISTS v_minifig_year_of_publication;
CREATE VIEW v_minifig_year_of_publication AS
SELECT m.id, MIN(s.year_of_publication) AS year_of_publication FROM minifigs m
LEFT JOIN inventory_minifigs im ON m.id = im.fig_id
LEFT JOIN inventories i ON i.id = im.inventory_id and i.is_latest = TRUE
LEFT JOIN sets s ON i.set_id = s.id
GROUP BY m.id;

CREATE TABLE tmp_minifig_props (
	id INTEGER UNIQUE NOT NULL,
	has_unique_part BOOLEAN NOT NULL,
    year_of_publication INTEGER NOT NULL
);

INSERT INTO tmp_minifig_props
SELECT v1.id, v1.has_unique_part, v2.year_of_publication FROM v_minifig_has_unique_part v1
LEFT JOIN v_minifig_year_of_publication v2 on v2.id = v1.id
WHERE v1.has_unique_part IS NOT NULL AND v2.year_of_publication IS NOT NULL;

UPDATE minifigs SET (has_unique_part, year_of_publication) = (
    SELECT has_unique_part, year_of_publication FROM tmp_minifig_props WHERE
    tmp_minifig_props.id = minifigs.id
);

DROP TABLE IF EXISTS tmp_minifig_props;


-- Insert minifig similarity data
create view v_actual_minifig_inventories as
select * from inventory_parts where inventory_id in (
select distinct ifig.id from inventories iset
left join inventory_minifigs im on im.inventory_id = iset.id
left join minifig_inventory_rel mir on mir.inventory_minifig_id = im.id
left join inventories ifig on ifig.id = mir.inventory_id
where iset.set_id is not null and iset.is_latest = 't' and ifig.is_latest = 't')
and is_spare = 'f';

create view v_actual_minifig_scores as
select ami.inventory_id, 1 / ((sum(pcf.total_amount) * 1.0) / sum(ami.quantity)) as score from v_actual_minifig_inventories ami
left join part_color_frequencies pcf on pcf.id = ami.part_color_frequency_id
group by ami.inventory_id;


create view v_actual_minifig_similarities as
select ami.id1, ami.id2, (ami.simi * 1.0 / mi1.num_parts) as pct from (
select id1, id2, count(*) as simi from (
select ami1.inventory_id as id1, ami2.inventory_id as id2 from v_actual_minifig_inventories ami1
left join v_actual_minifig_inventories ami2 on ami1.part_color_frequency_id = ami2.part_color_frequency_id and ami1.inventory_id <> ami2.inventory_id
where ami2.inventory_id is not null) ami
group by id1, id2) ami
left join (select inventory_id, max(inventory_minifig_id) as inventory_minifig_id from minifig_inventory_rel group by inventory_id) mir1 on mir1.inventory_id = ami.id1
left join inventory_minifigs im1 on im1.id = mir1.inventory_minifig_id
left join minifigs mi1 on mi1.id = im1.fig_id;

create view v_actual_minifig_set_occurances as
select subq.fig_id, count(subq.id) as amount from (select im.fig_id, i.id from (select * from inventories where is_latest = 't' and set_id is not null) i
left join inventory_minifigs im on im.inventory_id = i.id
where im.id is not null) as subq
group by subq.fig_id;

create view v_actual_minifig_set_stats as
select im.fig_id, max(s.num_parts) as max_parts,  min(s.num_parts) as min_parts from inventory_minifigs im
left join (select * from inventories where is_latest = 't' and set_id is not null) i on i.id = im.inventory_id
left join sets s on s.id = i.set_id
group by im.fig_id;

CREATE TABLE tmp_fig_similarities (
    id1 INTEGER NOT NULL,
    id2 INTEGER NOT NULL,
    pct NUMERIC NOT NULL
);


insert into tmp_fig_similarities
select * from v_actual_minifig_similarities where pct >= 0.75;


insert into minifig_similarities (
inventory_minifig_id_1,
inventory_minifig_id_2,
set_occurance_minifig_1,
set_occurance_minifig_2,
max_set_parts_minifig_1,
max_set_parts_minifig_2,
min_set_parts_minifig_1,
min_set_parts_minifig_2,
score_minifig_1,
score_minifig_2,
num_parts_minifig_1,
num_parts_minifig_2,
theme_minifig_1,
theme_minifig_2,
name_minifig_1,
name_minifig_2,
num_minifig_1,
num_minifig_2,
similarity)
select 
mir1.inventory_minifig_id,
mir2.inventory_minifig_id,
amso1.amount,
amso2.amount,
mss1.max_parts,
mss2.max_parts,
mss1.min_parts,
mss2.min_parts,
ams1.score,
ams2.score,
m1.num_parts,
m2.num_parts,
t1.name,
t2.name,
m1.name,
m2.name,
m1.fig_num,
m2.fig_num,
ams.pct
from tmp_fig_similarities ams
left join (select inventory_id, max(inventory_minifig_id) as inventory_minifig_id from minifig_inventory_rel group by inventory_id) mir1 on mir1.inventory_id = ams.id1
left join (select inventory_id, max(inventory_minifig_id) as inventory_minifig_id from minifig_inventory_rel group by inventory_id) mir2 on mir2.inventory_id = ams.id2
left join inventory_minifigs im1 on im1.id = mir1.inventory_minifig_id
left join inventory_minifigs im2 on im2.id = mir2.inventory_minifig_id
left join inventories i1 on im1.inventory_id = i1.id
left join inventories i2 on im2.inventory_id = i2.id
left join sets s1 on i1.set_id = s1.id
left join sets s2 on i2.set_id = s2.id
left join themes t1 on s1.root_theme_id = t1.id
left join themes t2 on s2.root_theme_id = t2.id
left join v_actual_minifig_scores ams1 on ams1.inventory_id = ams.id1
left join v_actual_minifig_scores ams2 on ams2.inventory_id = ams.id2
left join minifigs m1 on m1.id = im1.fig_id
left join minifigs m2 on m2.id = im2.fig_id
left join v_actual_minifig_set_occurances amso1 on amso1.fig_id = m1.id
left join v_actual_minifig_set_occurances amso2 on amso2.fig_id = m2.id
left join v_actual_minifig_set_stats mss1 on mss1.fig_id = im1.fig_id
left join v_actual_minifig_set_stats mss2 on mss2.fig_id = im2.fig_id;

DROP TABLE tmp_fig_similarities;
DROP VIEW v_actual_minifig_set_occurances;
DROP VIEW v_actual_minifig_similarities;
DROP VIEW v_actual_minifig_scores;
DROP VIEW v_actual_minifig_inventories;
DROP VIEW v_actual_minifig_set_stats;

-- Create views for ui
DROP VIEW IF EXISTS v_inventory_parts;
CREATE VIEW v_inventory_parts AS
SELECT
ip.id,
ip.inventory_id,
p.name,
p.part_num,
p.part_material,
ip.is_spare,
c.name AS color_name,
c.is_trans,
c.rgb,
ip.quantity,
pcf.total_amount,
e.element_id
FROM inventory_parts ip
LEFT JOIN part_color_frequencies pcf ON pcf.id = ip.part_color_frequency_id
LEFT JOIN parts p ON p.id = pcf.part_id
LEFT JOIN colors c ON c.id = pcf.color_id
LEFT JOIN (select DISTINCT part_color_frequency_id, first_value(element_id) OVER (PARTITION BY part_color_frequency_id ORDER BY id DESC) AS element_id from part_color_frequency_element_rel) e ON e.part_color_frequency_id = pcf.id;

DROP VIEW IF EXISTS v_sets;
CREATE VIEW v_sets AS 
SELECT
s.id,
s.set_num,
s.name,
s.year_of_publication,
s.num_parts,
s.eol,
s.retail_price,
s.has_stickers,
sc.score,
rt.name AS root_theme,
t.name AS theme,
t.id AS theme_id
FROM sets s
LEFT JOIN scores sc ON sc.id = s.score_id
LEFT JOIN themes rt ON rt.id = s.root_theme_id
LEFT JOIN themes t ON t.id = s.theme_id;

DROP VIEW IF EXISTS v_scores;
CREATE VIEW v_scores AS
select * from (select sc.id, false as is_set, im.id as entity_id, sc.score, sc.calc_date, mf.fig_num as num, mf.name, mf.num_parts, mf.year_of_publication,
case when sc.score < st.lower_quartil then 1
when sc.score < st.median then 2
when sc.score < st.upper_quartil then 3
else 4 end as rating
from inventory_minifigs im
left join scores sc on sc.id = im.score_id
left join minifigs mf on mf.id = im.fig_id
left join statistics st on st.is_set = 'f' and st.theme_id is null
union all
select sc.id, true as is_set, s.id as entity_id, sc.score, sc.calc_date, s.set_num as num, s.name, s.num_parts, s.year_of_publication,
case when sc.score < st.lower_quartil then 1
when sc.score < st.median then 2
when sc.score < st.upper_quartil then 3
else 4 end as rating
from sets s
left join scores sc on sc.id = s.score_id
left join statistics st on st.is_set = 't' and st.theme_id is null) as sc
where sc.id is not null;

DROP VIEW IF EXISTS v_parts;
CREATE VIEW v_parts AS
select pcf.id, pcf.total_amount, c.name as color_name, c.rgb, c.is_trans, p.part_num, p.name as part_name, p.part_material,
case when p.part_num like '%pr%' then true else false end as is_print,
pc.name as category_name, pcfr.element_id, ep.price from part_color_frequencies pcf
left join colors c on c.id = pcf.color_id
left join parts p on p.id = pcf.part_id
left join part_categories pc on pc.id = p.part_cat_id
left join part_color_frequency_element_rel pcfr on pcfr.part_color_frequency_id = pcf.id
left join element_prices ep on ep.element_id = pcfr.id;

DROP VIEW IF EXISTS v_minifig_has_unique_part;
DROP VIEW IF EXISTS v_minifig_year_of_publication;

DROP TABLE IF EXISTS colors_tmp;
DROP TABLE IF EXISTS elements_tmp;
DROP TABLE IF EXISTS inventories_tmp;
DROP TABLE IF EXISTS inventory_minifigs_tmp;
DROP TABLE IF EXISTS inventory_parts_tmp;
DROP TABLE IF EXISTS inventory_sets_tmp;
DROP TABLE IF EXISTS minifigs_tmp;
DROP TABLE IF EXISTS part_categories_tmp;
DROP TABLE IF EXISTS part_relationships_tmp;
DROP TABLE IF EXISTS parts_tmp;
DROP TABLE IF EXISTS sets_tmp;
DROP TABLE IF EXISTS themes_tmp;
DROP TABLE IF EXISTS tmp_sets_info;
DROP TABLE IF EXISTS tmp_scores;
DROP TABLE IF EXISTS tmp_element_prices;