-- Generate base tmp tables by executing create_tmp_tables.py

-- Create tmp tables to store generated data --
CREATE TABLE tmp_sets_info (
	set_num TEXT NOT NULL UNIQUE,
	eol VARCHAR(1) DEFAULT -1,
	retail_price INTEGER
);

CREATE TABLE tmp_scores (
	set_num TEXT,
	fig_num TEXT,
	score FLOAT NOT NULL,
	calc_date DATE NOT NULL
);


-- Insert generated data into tmp tables
INSERT INTO tmp_sets_info
SELECT set_num, eol, retail_price FROM sets WHERE retail_price IS NOT NULL OR eol <> -1;

INSERT INTO tmp_scores
SELECT DISTINCT s.set_num, m.fig_num, sc.score, sc.calc_date FROM scores sc
LEFT JOIN inventories i ON sc.inventory_id = i.id
LEFT JOIN minifig_inventory_rel mir ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON mir.inventory_minifig_id = im.id
LEFT JOIN sets s ON i.set_id = s.id
LEFT JOIN minifigs m ON im.fig_id = m.id;


-- Delete queries --
PRAGMA foreign_keys = OFF;
DELETE FROM colors WHERE id NOT NULL;
DELETE FROM minifigs WHERE id NOT NULL;
DELETE FROM part_categories WHERE id NOT NULL;
DELETE FROM themes WHERE id NOT NULL;
DELETE FROM sets WHERE id NOT NULL;
DELETE FROM parts WHERE id NOT NULL;
DELETE FROM elements WHERE element_id NOT NULL;
DELETE FROM part_color_frequencies WHERE part_id NOT NULL;
DELETE FROM inventories WHERE id NOT NULL;
DELETE FROM part_relationships WHERE child_part_id NOT NULL;
DELETE FROM inventory_minifigs WHERE inventory_id NOT NULL;
DELETE FROM inventory_sets WHERE inventory_id NOT NULL;
DELETE FROM inventory_parts WHERE inventory_id NOT NULL;
DELETE FROM minifig_inventory_rel WHERE inventory_id NOT NULL;
DELETE FROM set_inventory_rel WHERE inventory_id  NOT NULL;
DELETE FROM scores WHERE id NOT NULL;

-- Insert queries --

-- Base tables
INSERT OR IGNORE INTO colors (id, name, rgb, is_trans)
SELECT id, name, rgb, is_trans FROM colors_tmp;

INSERT OR IGNORE INTO minifigs (fig_num, name, num_parts)
SELECT fig_num, name, num_parts FROM minifigs_tmp;

INSERT OR IGNORE INTO part_categories (id, name)
SELECT id, name FROM part_categories_tmp;

INSERT OR IGNORE INTO themes (id, name, parent_id)
SELECT id, name, parent_id FROM themes_tmp;

INSERT OR IGNORE INTO sets (set_num, name, year_of_publication, theme_id, num_parts)
SELECT set_num, name, year_of_publication, theme_id, num_parts FROM sets_tmp;

INSERT OR IGNORE INTO parts (part_num, name, part_cat_id, part_material)
SELECT part_num, name, part_cat_id, part_material FROM parts_tmp;

INSERT OR IGNORE INTO elements (element_id, part_id, color_id)
SELECT element_id, p.id, color_id FROM elements_tmp e
LEFT JOIN parts p ON e.part_num = p.part_num;

INSERT OR IGNORE INTO inventories (id, set_id, version)
SELECT t.id, s.id, version FROM inventories_tmp t
LEFT JOIN sets s ON t.set_num = s.set_num;

INSERT OR IGNORE INTO part_relationships (rel_type, child_part_id, parent_part_id)
SELECT rel_type, p1.id, p2.id FROM part_relationships_tmp t
LEFT JOIN parts p1 ON t.child_part_num = p1.part_num
LEFT JOIN parts p2 ON t.parent_part_num = p2.part_num;

INSERT OR IGNORE INTO inventory_minifigs (inventory_id, fig_id, quantity)
SELECT inventory_id, m.id, quantity FROM inventory_minifigs_tmp t
LEFT JOIN minifigs m ON m.fig_num = t.fig_num;

INSERT OR IGNORE INTO inventory_sets (inventory_id, set_id, quantity)
SELECT inventory_id, s.id, quantity FROM inventory_sets_tmp t
LEFT JOIN sets s ON s.set_num = t.set_num;

INSERT OR IGNORE INTO inventory_parts (inventory_id, part_id, color_id, is_spare, quantity)
SELECT inventory_id, p.id, color_id, is_spare, quantity FROM inventory_parts_tmp t
LEFT JOIN parts p ON t.part_num = p.part_num;

--- Insert check
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM colors) c, (SELECT count(*) AS amount FROM colors_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM minifigs) c, (SELECT count(*) AS amount FROM minifigs_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM part_categories) c, (SELECT count(*) AS amount FROM part_categories_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM themes) c, (SELECT count(*) AS amount FROM themes_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM sets) c, (SELECT count(*) AS amount FROM sets_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM parts) c, (SELECT count(*) AS amount FROM parts_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM elements) c, (SELECT count(*) AS amount FROM elements_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM inventories) c, (SELECT count(*) AS amount FROM inventories_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM part_relationships) c, (SELECT count(*) AS amount FROM part_relationships_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM inventory_minifigs) c, (SELECT count(*) AS amount FROM inventory_minifigs_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM inventory_sets) c, (SELECT count(*) AS amount FROM inventory_sets_tmp) ct
UNION ALL
SELECT c.amount = ct.amount FROM (SELECT count(*) AS amount FROM inventory_parts) c, (SELECT count(*) AS amount FROM inventory_parts_tmp) ct;


-- Generated FROM base tables
INSERT OR IGNORE INTO part_color_frequencies (part_id, color_id)
SELECT DISTINCT part_id, color_id FROM inventory_parts;

INSERT OR IGNORE INTO minifig_inventory_rel (inventory_id, inventory_minifig_id)
SELECT i.id, im.id FROM inventory_minifigs im
LEFT JOIN minifigs m ON im.fig_id = m.id
LEFT JOIN inventories_tmp i ON m.fig_num = i.set_num;

INSERT OR IGNORE INTO set_inventory_rel (inventory_id, inventory_set_id)
SELECT i.id, invs.id FROM inventory_sets invs
LEFT JOIN sets s ON invs.set_id = s.id
LEFT JOIN inventories_tmp i ON s.set_num = i.set_num;

PRAGMA foreign_keys = ON;

-- Update inventories table (is_latest)

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

UPDATE inventories SET is_latest = 1 WHERE inventories.id IN (SELECT id FROM v_latest_inventory);
UPDATE inventories SET is_latest = 0 WHERE inventories.id NOT IN (SELECT id FROM v_latest_inventory);


-- Update part_color_frequencies table (quantity)

CREATE VIEW v_total_quantities as
SELECT part_id, color_id, sum(quantity) AS quantity
FROM (SELECT ip.part_id, ip.color_id, sum(ip.quantity) AS quantity
FROM (SELECT * FROM inventories WHERE is_latest = 1 AND set_id IS NOT NULL) i
LEFT JOIN inventory_parts ip ON i.id = ip.inventory_id
GROUP BY ip.part_id, ip.color_id
UNION ALL
SELECT ip.part_id, ip.color_id, sum(ip.quantity * im.quantity) AS quantity FROM minifig_inventory_rel mir
LEFT JOIN (SELECT * FROM inventories WHERE is_latest = 1 AND set_id is NULL) i ON i.id = mir.inventory_id
LEFT JOIN inventory_minifigs im ON im.id = mir.inventory_minifig_id
LEFT JOIN inventory_parts ip ON i.id = ip.inventory_id
GROUP BY ip.part_id, ip.color_id)
GROUP BY part_id, color_id;


UPDATE part_color_frequencies
SET
      total_amount = (SELECT v_total_quantities.quantity 
                            FROM v_total_quantities
                            WHERE v_total_quantities.part_id = part_color_frequencies.part_id AND 
							v_total_quantities.color_id = part_color_frequencies.color_id)

WHERE
    EXISTS (
        SELECT *
        FROM v_total_quantities
        WHERE v_total_quantities.part_id = part_color_frequencies.part_id AND 
							v_total_quantities.color_id = part_color_frequencies.color_id
    );


DROP VIEW v_total_quantities;
DROP VIEW v_latest_inventory;

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
LEFT JOIN inventories i ON i.set_id = s.id AND i.is_latest = 1
WHERE tsc.set_num IS NOT NULL
UNION ALL
SELECT DISTINCT i.id AS inventory_id, tsc.score, tsc.calc_date FROM tmp_scores tsc
LEFT JOIN minifigs m ON m.fig_num = tsc.fig_num
LEFT JOIN inventory_minifigs im ON im.fig_id = m.id
LEFT JOIN minifig_inventory_rel mir ON mir.inventory_minifig_id = im.id
LEFT JOIN inventories i ON i.id = mir.inventory_id AND i.is_latest = 1
WHERE tsc.fig_num IS NOT NULL;

-- Set score ids
DROP VIEW IF EXISTS v_sets_scores;
CREATE VIEW v_sets_scores AS
    SELECT DISTINCT s.id AS set_id, sc.id AS score_id FROM (
        SELECT * FROM scores
        GROUP BY inventory_id
        HAVING MAX(calc_date)
    ) SC
    LEFT JOIN inventories i ON sc.inventory_id = i.id
    LEFT JOIN sets s ON i.set_id = s.id
    WHERE s.id IS NOT NULL;
UPDATE sets SET score_id = (
    SELECT score_id FROM v_sets_scores
    WHERE v_sets_scores.set_id = sets.id
);
DROP VIEW v_sets_scores;


DROP VIEW IF EXISTS v_inventory_minifigs_scores;
CREATE VIEW v_inventory_minifigs_scores AS
    SELECT DISTINCT im.id AS minifig_id, sc.id AS score_id FROM (
        SELECT * FROM scores
        GROUP BY inventory_id
        HAVING MAX(calc_date)
    ) SC
    LEFT JOIN inventories i ON sc.inventory_id = i.id
    LEFT JOIN minifig_inventory_rel mir ON i.id = mir.inventory_id
    LEFT JOIN inventory_minifigs im ON mir.inventory_minifig_id = im.id
    WHERE im.id IS NOT NULL;
UPDATE inventory_minifigs SET score_id = (
    SELECT score_id FROM v_inventory_minifigs_scores WHERE
    v_inventory_minifigs_scores.minifig_id = inventory_minifigs.id
);
DROP VIEW v_inventory_minifigs_scores;


DROP TABLE colors_tmp;
DROP TABLE elements_tmp;
DROP TABLE inventories_tmp;
DROP TABLE inventory_minifigs_tmp;
DROP TABLE inventory_parts_tmp;
DROP TABLE inventory_sets_tmp;
DROP TABLE minifigs_tmp;
DROP TABLE part_categories_tmp;
DROP TABLE part_relationships_tmp;
DROP TABLE parts_tmp;
DROP TABLE sets_tmp;
DROP TABLE themes_tmp;
DROP TABLE tmp_sets_info;
DROP TABLE tmp_scores;