INSERT OR REPLACE INTO colors (id, name, rgb, is_trans)
SELECT id, name, rgb, is_trans FROM colors_tmp;

INSERT OR REPLACE INTO inventories (id, version)
SELECT id, version FROM inventories_tmp;

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
