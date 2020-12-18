-- Create tmp tables to store generated data --
create table tmp_sets_info (
	set_num TEXT NOT NULL UNIQUE,
	eol VARCHAR(1) DEFAULT -1,
	retail_price INTEGER
);

create table tmp_scores (
	set_num TEXT,
	fig_num TEXT,
	score FLOAT NOT NULL,
	calc_date DATE NOT NULL
);

create table tmp_scores_with_id (
	inventory_id INTEGER NOT NULL,
	score FLOAT NOT NULL,
	calc_date DATE NOT NULL
);

-- Insert generated data into tmp tables
insert into tmp_sets_info
select set_num, eol, retail_price from sets where retail_price is not null or eol <> -1;

insert into tmp_scores
select distinct s.set_num, m.fig_num, sc.score, sc.calc_date from scores sc
left join inventories i on sc.inventory_id = i.id
left join minifig_inventory_rel mir on i.id = mir.inventory_id
left join inventory_minifigs im on mir.inventory_minifig_id = im.id
left join sets s on i.set_id = s.id
left join minifigs m on im.fig_id = m.id;

insert into tmp_scores_with_id
select i.id as inventory_id, tsc.score, tsc.calc_date from tmp_scores tsc
left join sets s on s.set_num = tsc.set_num
left join inventories i on i.set_id = s.id and i.is_latest = 1
where tsc.set_num is not null
union all
select distinct i.id as inventory_id, tsc.score, tsc.calc_date from tmp_scores tsc
left join minifigs m on m.fig_num = tsc.fig_num
left join inventory_minifigs im on im.fig_id = m.id
left join minifig_inventory_rel mir on mir.inventory_minifig_id = im.id
left join inventories i on i.id = mir.inventory_id and i.is_latest = 1
where tsc.fig_num is not null;

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
left join parts p on e.part_num = p.part_num;

INSERT OR IGNORE INTO inventories (id, set_id, version)
SELECT t.id, s.id, version FROM inventories_tmp t
left join sets s on t.set_num = s.set_num;

INSERT OR IGNORE INTO part_relationships (rel_type, child_part_id, parent_part_id)
SELECT rel_type, p1.id, p2.id FROM part_relationships_tmp t
left join parts p1 on t.child_part_num = p1.part_num
left join parts p2 on t.parent_part_num = p2.part_num;

INSERT OR IGNORE INTO inventory_minifigs (inventory_id, fig_id, quantity)
SELECT inventory_id, m.id, quantity FROM inventory_minifigs_tmp t
left join minifigs m on m.fig_num = t.fig_num;

INSERT OR IGNORE INTO inventory_sets (inventory_id, set_id, quantity)
SELECT inventory_id, s.id, quantity FROM inventory_sets_tmp t
left join sets s on s.set_num = t.set_num;

INSERT OR IGNORE INTO inventory_parts (inventory_id, part_id, color_id, is_spare, quantity)
SELECT inventory_id, p.id, color_id, is_spare, quantity FROM inventory_parts_tmp t
left join parts p on t.part_num = p.part_num;

DELETE FROM scores WHERE inventory_id NOT IN (select id FROM inventories);
PRAGMA foreign_keys = ON;

--- Insert check
select c.amount = ct.amount from (select count(*) as amount from colors) c, (select count(*) as amount from colors_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from minifigs) c, (select count(*) as amount from minifigs_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from part_categories) c, (select count(*) as amount from part_categories_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from themes) c, (select count(*) as amount from themes_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from sets) c, (select count(*) as amount from sets_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from parts) c, (select count(*) as amount from parts_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from elements) c, (select count(*) as amount from elements_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from inventories) c, (select count(*) as amount from inventories_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from part_relationships) c, (select count(*) as amount from part_relationships_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from inventory_minifigs) c, (select count(*) as amount from inventory_minifigs_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from inventory_sets) c, (select count(*) as amount from inventory_sets_tmp) ct
union all
select c.amount = ct.amount from (select count(*) as amount from inventory_parts) c, (select count(*) as amount from inventory_parts_tmp) ct;


-- Generated from base tables
INSERT OR IGNORE INTO part_color_frequencies (part_id, color_id)
SELECT part_id, color_id FROM inventory_parts;

INSERT OR IGNORE INTO minifig_inventory_rel (inventory_id, inventory_minifig_id)
SELECT i.id, im.id FROM inventory_minifigs im
left join minifigs m on im.fig_id = m.id
left join inventories_tmp i on m.fig_num = i.set_num;

INSERT OR IGNORE INTO set_inventory_rel (inventory_id, inventory_set_id)
SELECT i.id, invs.id FROM inventory_sets invs
left join sets s on invs.set_id = s.id
left join inventories_tmp i on s.set_num = i.set_num;


-- Update inventories table (is_latest)

create view v_latest_inventory as
select i.id from (select * from inventories where set_id is not null) i
left join (select set_id, max(version) as max_version from inventories group by set_id) as max_i on i.set_id = max_i.set_id and i.version = max_i.max_version
where max_i.set_id is not null
union all
select mir.inventory_id from minifig_inventory_rel mir
left join inventories i on i.id = mir.inventory_id
left join inventory_minifigs im on im.id = mir.inventory_minifig_id
left join (select im.fig_id, max(i.version) as max_version from minifig_inventory_rel mir
left join inventories i on i.id = mir.inventory_id
left join inventory_minifigs im on im.id = mir.inventory_minifig_id
group by im.fig_id) as im_max on im_max.fig_id = im.fig_id and im_max.max_version = i.version;

UPDATE inventories SET is_latest = 1 WHERE inventories.id IN (SELECT id FROM v_latest_inventory);
UPDATE inventories SET is_latest = 0 WHERE inventories.id NOT IN (SELECT id FROM v_latest_inventory);


-- Update part_color_frequencies table (quantity)

create view v_total_quantities as
select part_id, color_id, sum(quantity) as quantity
from (select ip.part_id, ip.color_id, sum(ip.quantity) as quantity
from (select * from inventories where is_latest = 1 and set_id is not null) i
left join inventory_parts ip on i.id = ip.inventory_id
group by ip.part_id, ip.color_id
union all
select ip.part_id, ip.color_id, sum(ip.quantity * im.quantity) as quantity from minifig_inventory_rel mir
left join (select * from inventories where is_latest = 1 and set_id is null) i on i.id = mir.inventory_id
left join inventory_minifigs im on im.id = mir.inventory_minifig_id
left join inventory_parts ip on i.id = ip.inventory_id
group by ip.part_id, ip.color_id)
group by part_id, color_id;


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


drop view v_total_quantities;
drop view v_latest_inventory;

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

insert into scores
select rowid as id, inventory_id, score, calc_date from tmp_scores_with_id;


drop table colors_tmp;
drop table elements_tmp;
drop table inventories_tmp;
drop table inventory_minifigs_tmp;
drop table inventory_parts_tmp;
drop table inventory_sets_tmp;
drop table minifigs_tmp;
drop table part_categories_tmp;
drop table part_relationships_tmp;
drop table parts_tmp;
drop table sets_tmp;
drop table themes_tmp;
drop table tmp_sets_info;
drop table tmp_scores;
drop table tmp_scores_with_id;