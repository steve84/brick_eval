DROP TABLE IF EXISTS tmp_part_freq;
DROP TABLE IF EXISTS tmp_act_set_score;
DROP TABLE IF EXISTS tmp_act_minifig_score;
DROP TABLE IF EXISTS tmp_minifig_props;
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

CREATE OR REPLACE VIEW v_latest_inventory as
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

CREATE OR REPLACE VIEW v_total_quantities as
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

CREATE OR REPLACE VIEW v_sets_scores AS
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

CREATE OR REPLACE VIEW v_inventory_minifigs_scores AS
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
CREATE OR REPLACE VIEW v_root_theme AS
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

-- Update minifig properties
CREATE OR REPLACE VIEW v_minifig_has_unique_part AS
SELECT m.id, MIN(pcf.total_amount) = 1 AS has_unique_part FROM minifigs m
LEFT JOIN inventory_minifigs im ON m.id = im.fig_id
LEFT JOIN minifig_inventory_rel mir ON im.id = mir.inventory_minifig_id
LEFT JOIN inventories i ON i.id = mir.inventory_id and i.is_latest = TRUE
LEFT JOIN (SELECT inventory_id, part_color_frequency_id, sum(quantity) AS quantity FROM inventory_parts GROUP BY inventory_id, part_color_frequency_id) ip ON i.id = ip.inventory_id
LEFT JOIN part_color_frequencies pcf ON ip.part_color_frequency_id = pcf.id
GROUP BY m.id;

CREATE OR REPLACE VIEW v_minifig_year_of_publication AS
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


-- Create views for ui
CREATE OR REPLACE VIEW v_inventory_parts AS
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

CREATE OR REPLACE VIEW v_sets AS 
SELECT
s.id,
s.set_num,
s.name,
s.year_of_publication,
s.num_parts,
s.eol,
s.retail_price,
sc.score,
rt.name AS root_theme,
t.name AS theme,
t.id AS theme_id
FROM sets s
LEFT JOIN scores sc ON sc.id = s.score_id
LEFT JOIN themes rt ON rt.id = s.root_theme_id
LEFT JOIN themes t ON t.id = s.theme_id;

CREATE OR REPLACE VIEW v_scores AS
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

CREATE OR REPLACE VIEW v_parts AS
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