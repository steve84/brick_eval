INSERT OR REPLACE INTO colors (id, name, rgb, is_trans)
SELECT id, name, rgb, is_trans FROM colors_tmp;

INSERT OR REPLACE INTO minifigs (fig_num, name, num_parts)
SELECT fig_num, name, num_parts FROM minifigs_tmp;

INSERT OR REPLACE INTO part_categories (id, name)
SELECT id, name FROM part_categories_tmp;

INSERT OR REPLACE INTO themes (id, name, parent_id)
SELECT id, name, parent_id FROM themes_tmp;

INSERT OR REPLACE INTO sets (set_num, name, year_of_publication, theme_id, num_parts)
SELECT set_num, name, year_of_publication, theme_id, num_parts FROM sets_tmp;

INSERT OR REPLACE INTO parts (part_num, name, part_cat_id, part_material)
SELECT part_num, name, part_cat_id, part_material FROM parts_tmp;

INSERT OR REPLACE INTO elements (element_id, part_id, color_id)
SELECT element_id, p.id, color_id FROM elements_tmp e
left join parts p on e.part_num = p.part_num;


INSERT OR REPLACE INTO part_color_frequencies (part_id, color_id)
SELECT part_id, color_id FROM inventory_parts;

INSERT OR REPLACE INTO inventories (id, set_id, version)
SELECT t.id, s.id, version FROM inventories_tmp t
left join sets s on t.set_num = s.set_num;

INSERT OR REPLACE INTO part_relationships (rel_type, child_part_id, parent_part_id)
SELECT rel_type, p1.id, p2.id FROM part_relationships_tmp t
left join parts p1 on t.child_part_num = p1.part_num
left join parts p2 on t.parent_part_num = p2.part_num;

INSERT OR REPLACE INTO inventory_minifigs (inventory_id, fig_id, quantity)
SELECT inventory_id, m.id, quantity FROM inventory_minifigs_tmp t
left join minifigs m on m.fig_num = t.fig_num;

INSERT OR REPLACE INTO inventory_sets (inventory_id, set_id, quantity)
SELECT inventory_id, s.id, quantity FROM inventory_sets_tmp t
left join sets s on s.set_num = t.set_num;

INSERT OR REPLACE INTO inventory_parts (inventory_id, part_id, color_id, is_spare, quantity)
SELECT inventory_id, p.id, color_id, is_spare, quantity FROM inventory_parts_tmp t
left join parts p on t.part_num = p.part_num;


INSERT OR REPLACE INTO minifig_inventory_rel (inventory_id, inventory_minifig_id)
SELECT i.id, im.id FROM inventory_minifigs im
left join minifigs m on im.fig_id = m.id
left join inventories_tmp i on m.fig_num = i.set_num;

INSERT OR REPLACE INTO set_inventory_rel (inventory_id, inventory_set_id)
SELECT i.id, invs.id FROM inventory_sets invs
left join sets s on invs.set_id = s.id
left join inventories_tmp i on s.set_num = i.set_num;


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
