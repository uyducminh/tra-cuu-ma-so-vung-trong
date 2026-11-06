-- Bảng nhật ký thao tác của trang tra cứu và hàm xem cho quản lý.
-- Mật khẩu quản lý KHÔNG nằm ở đây; đặt riêng bằng lệnh ở cuối file (chạy tay, không commit mật khẩu).

create table if not exists public.tracuu_nhat_ky (
  id bigint generated always as identity primary key,
  thoi_gian timestamptz not null default now(),
  ten_nguoi_dung text not null check (char_length(ten_nguoi_dung) between 1 and 80),
  ma_thiet_bi text check (char_length(ma_thiet_bi) <= 64),
  thao_tac text not null check (thao_tac in ('vao_trang','tim_kiem','xem_ma','kiem_tra_nhieu','chuyen_tab')),
  chi_tiet jsonb not null default '{}'::jsonb check (pg_column_size(chi_tiet) < 16000),
  trinh_duyet text check (char_length(trinh_duyet) <= 300)
);
create index if not exists tracuu_nhat_ky_thoi_gian_idx on public.tracuu_nhat_ky (thoi_gian desc);
create index if not exists tracuu_nhat_ky_ten_idx on public.tracuu_nhat_ky (ten_nguoi_dung);

alter table public.tracuu_nhat_ky enable row level security;
revoke all on public.tracuu_nhat_ky from anon, authenticated;
grant insert (ten_nguoi_dung, ma_thiet_bi, thao_tac, chi_tiet, trinh_duyet) on public.tracuu_nhat_ky to anon, authenticated;
drop policy if exists tracuu_nhat_ky_ghi on public.tracuu_nhat_ky;
create policy tracuu_nhat_ky_ghi on public.tracuu_nhat_ky for insert to anon, authenticated with check (true);

create table if not exists public.tracuu_cau_hinh (
  khoa text primary key,
  gia_tri text not null
);
alter table public.tracuu_cau_hinh enable row level security;
revoke all on public.tracuu_cau_hinh from anon, authenticated;

create or replace function public.tracuu_xem_nhat_ky(
  p_mat_khau text, p_tu timestamptz default null, p_den timestamptz default null,
  p_ten text default null, p_thao_tac text default null, p_gioi_han int default 5000)
returns setof public.tracuu_nhat_ky
language plpgsql security definer set search_path = ''
as $$
declare h text;
begin
  select gia_tri into h from public.tracuu_cau_hinh where khoa = 'mat_khau_quan_ly';
  if h is null or extensions.crypt(coalesce(p_mat_khau,''), h) <> h then
    perform pg_sleep(1);
    raise exception 'Sai mat khau quan ly' using errcode = '28P01';
  end if;
  return query
    select * from public.tracuu_nhat_ky n
    where (p_tu is null or n.thoi_gian >= p_tu)
      and (p_den is null or n.thoi_gian <= p_den)
      and (p_ten is null or n.ten_nguoi_dung ilike '%' || p_ten || '%')
      and (p_thao_tac is null or n.thao_tac = p_thao_tac)
    order by n.thoi_gian desc
    limit least(greatest(coalesce(p_gioi_han, 5000), 1), 20000);
end $$;
revoke all on function public.tracuu_xem_nhat_ky(text, timestamptz, timestamptz, text, text, int) from public;
grant execute on function public.tracuu_xem_nhat_ky(text, timestamptz, timestamptz, text, text, int) to anon, authenticated;

-- Đặt hoặc đổi mật khẩu quản lý (chạy riêng trong SQL editor của Supabase, thay <mật khẩu>):
-- insert into public.tracuu_cau_hinh (khoa, gia_tri)
-- values ('mat_khau_quan_ly', extensions.crypt('<mật khẩu>', extensions.gen_salt('bf')))
-- on conflict (khoa) do update set gia_tri = excluded.gia_tri;
