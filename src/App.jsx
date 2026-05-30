-- ============================================
-- EJECUTA ESTO EN SUPABASE > SQL EDITOR
-- Versión corregida - evita errores de duplicados
-- ============================================

-- Eliminar políticas existentes si ya existen
drop policy if exists "allow_all_usuarios"        on usuarios;
drop policy if exists "allow_all_contactos"       on contactos;
drop policy if exists "allow_all_tareas"          on tareas;
drop policy if exists "allow_all_eventos"         on eventos;
drop policy if exists "allow_all_chat"            on chat;
drop policy if exists "allow_all_metas"           on metas_servicios;

-- Recrear políticas
create policy "allow_all_usuarios"        on usuarios        for all using (true) with check (true);
create policy "allow_all_contactos"       on contactos       for all using (true) with check (true);
create policy "allow_all_tareas"          on tareas          for all using (true) with check (true);
create policy "allow_all_eventos"         on eventos         for all using (true) with check (true);
create policy "allow_all_chat"            on chat            for all using (true) with check (true);
create policy "allow_all_metas"           on metas_servicios for all using (true) with check (true);

-- Confirmar que los datos iniciales existen
insert into usuarios (nombre, email, password, rol, avatar, color, meta, comision_pct) values
  ('Admin General',   'admin@empresa.com',  'admin123',  'admin',    'AG', '#ff7a59', 0,      0),
  ('Carlos Ruiz',     'carlos@empresa.com', 'vendedor1', 'vendedor', 'CR', '#7c3aed', 150000, 8),
  ('Sofía Mendoza',   'sofia@empresa.com',  'vendedor2', 'vendedor', 'SM', '#0ea5e9', 150000, 8),
  ('Diego Torres',    'diego@empresa.com',  'vendedor3', 'vendedor', 'DT', '#10b981', 120000, 7),
  ('Valentina López', 'vale@empresa.com',   'vendedor4', 'vendedor', 'VL', '#f59e0b', 120000, 7)
on conflict (email) do nothing;

insert into metas_servicios (servicio_id, meta) values
  ('marketing',   500000),
  ('incubadora',  300000),
  ('aceleradora', 400000),
  ('software',    600000),
  ('inversiones', 1000000),
  ('creditos',    800000)
on conflict (servicio_id) do nothing;

-- Realtime (ignorar si ya existe)
alter publication supabase_realtime add table chat;
alter publication supabase_realtime add table usuarios;
alter publication supabase_realtime add table contactos;
  
